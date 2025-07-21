import logging
import re
import shlex
import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

import httpx
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.country_data import (
    SUPPORTED_COUNTRIES,
    COUNTRY_NAME_TO_CODE,
    get_country_flag,
)
from utils.price_parser import extract_currency_and_price
from utils.command_factory import command_factory
from utils.permissions import Permission
from utils.formatter import foldable_text_v2, foldable_text_with_markdown_v2
from utils.message_manager import schedule_message_deletion
from utils.config_manager import config_manager, get_config
from utils.session_manager import app_search_sessions as user_search_sessions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default search countries if none are specified by the user
DEFAULT_COUNTRIES = ["CN", "NG", "TR", "IN", "MY", "US"]

# iTunes Search API base URL
ITUNES_API_URL = "https://itunes.apple.com/"

# Headers for iTunes API requests
ITUNES_HEADERS = {
    "User-Agent": "iTunes/12.11.3 (Windows; Microsoft Windows 10 x64 Professional Edition (Build 19041); x64) AppleWebKit/7611.1022.4001.1 (KHTML, like Gecko) Version/14.1.1 Safari/7611.1022.4001.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


def set_rate_converter(converter):
    global rate_converter
    rate_converter = converter


def set_cache_manager(manager):
    global cache_manager
    cache_manager = manager


class SappSearchAPI:
    """调用iTunes Search API进行App搜索的API类"""

    @staticmethod
    async def search_apps(
        query: str, country: str = "us", app_type: str = "software", limit: int = 50
    ) -> Dict:
        """
        使用iTunes Search API搜索App
        """
        try:
            async with httpx.AsyncClient(verify=False) as client:
                params = {
                    "term": query,
                    "country": country,
                    "media": "software",
                    "limit": limit,
                    "entity": app_type,
                }

                response = await client.get(
                    f"{ITUNES_API_URL}search",
                    params=params,
                    headers=ITUNES_HEADERS,
                    timeout=15,
                )
                response.raise_for_status()
                data = response.json()

                if (not data.get("results") and app_type != "software"):
                    fallback_params = {
                        "term": query,
                        "country": country,
                        "media": "software",
                        "limit": limit,
                        "explicit": "Yes",
                    }
                    fallback_response = await client.get(
                        f"{ITUNES_API_URL}search",
                        params=fallback_params,
                        headers=ITUNES_HEADERS,
                        timeout=15,
                    )
                    fallback_response.raise_for_status()
                    fallback_data = fallback_response.json()
                    if fallback_data.get("results"):
                        data = fallback_data

                results = data.get("results", [])
                filtered_results = SappSearchAPI._filter_results_by_platform(
                    results, app_type
                )

                return {
                    "results": filtered_results,
                    "query": query,
                    "country": country,
                    "app_type": app_type,
                }

        except Exception as e:
            logger.error(f"App search error: {e}")
            return {
                "results": [],
                "query": query,
                "country": country,
                "app_type": app_type,
                "error": str(e),
            }

    @staticmethod
    def _filter_results_by_platform(
        results: List[Dict], requested_app_type: str
    ) -> List[Dict]:
        """
        根据请求的平台类型过滤搜索结果
        """
        if requested_app_type == "software":
            return [app for app in results if app.get("kind") != "mac-software"]
        elif requested_app_type == "macSoftware":
            return [app for app in results if app.get("kind") == "mac-software"]
        elif requested_app_type == "iPadSoftware":
            filtered = []
            for app in results:
                if app.get("kind") == "mac-software":
                    continue
                supported_devices = app.get("supportedDevices", [])
                if any("iPad" in device for device in supported_devices):
                    filtered.append(app)
                elif not supported_devices and app.get("kind") != "mac-software":
                    filtered.append(app)
            return filtered
        return results

    @staticmethod
    async def get_app_details(app_id: str, country: str = "us") -> Optional[Dict]:
        """
        根据App ID获取详细信息
        """
        try:
            async with httpx.AsyncClient(verify=False) as client:
                params = {"id": app_id, "country": country.lower()}
                response = await client.get(
                    f"{ITUNES_API_URL}lookup",
                    params=params,
                    headers=ITUNES_HEADERS,
                    timeout=15,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting app details: {e}")
            return None


def format_search_results(search_data: Dict) -> str:
    """Formats the search result message to be a simple prompt."""
    if search_data.get("error"):
        return f"❌ 搜索失败: {search_data['error']}"

    results = search_data["results"]
    app_type = search_data.get("app_type", "software")
    platform_name = {
        "software": "iOS",
        "macSoftware": "macOS",
        "iPadSoftware": "iPadOS",
    }.get(app_type, "iOS")

    if not results:
        return f"🔍 没有找到关键词 '{search_data['query']}' 的相关 {platform_name} 应用 (国家: {search_data['country'].upper()})"

    return f"请从下方选择您要查询的 {platform_name} 应用："


def create_search_keyboard(search_data: Dict, session_id: str) -> InlineKeyboardMarkup:
    """创建搜索结果的内联键盘"""
    keyboard = []
    results = search_data["results"]
    app_type = search_data.get("app_type", "software")
    platform_icon = {"software": "📱", "macSoftware": "💻", "iPadSoftware": "📱"}.get(
        app_type, "📱"
    )

    for i in range(min(len(results), 5)):
        app = results[i]
        track_name = app.get("trackName", "未知应用")
        app_kind = app.get("kind", "")
        if app_kind == "mac-software":
            icon = "💻"
        elif any("iPad" in device for device in app.get("supportedDevices", [])):
            icon = "📱"
        else:
            icon = platform_icon
        button_text = f"{icon} {i + 1}. {track_name}"
        callback_data = (
            f"app_select_{i}_{search_data.get('current_page', 1)}_{session_id}"
        )
        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    current_page = search_data.get("current_page", 1)
    total_pages = search_data.get("total_pages", 1)
    nav_row = []
    if current_page > 1:
        nav_row.append(
            InlineKeyboardButton(
                "⬅️ 上一页", callback_data=f"app_page_{current_page - 1}_{session_id}"
            )
        )
    nav_row.append(
        InlineKeyboardButton(
            f"📄 {current_page}/{total_pages}",
            callback_data=f"app_page_info_{session_id}",
        )
    )
    if current_page < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                "下一页 ➡️", callback_data=f"app_page_{current_page + 1}_{session_id}"
            )
        )
    if nav_row:
        keyboard.append(nav_row)

    action_row = [
        InlineKeyboardButton(
            "🌍 更改搜索地区", callback_data=f"app_change_region_{session_id}"
        ),
        InlineKeyboardButton("❌ 关闭", callback_data=f"app_close_{session_id}"),
    ]
    keyboard.append(action_row)
    return InlineKeyboardMarkup(keyboard)


async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /app 命令，智能判断关键词和App ID"""
    if not update.message or not update.effective_chat:
        return

    if not context.args:
        help_message = (
            "🔍 *App Store 搜索*\n\n"
            "请提供应用名称或App ID进行搜索，可指定国家和平台：\n\n"
            "**用法示例:**\n"
            "`/app 微信`\n"
            "`/app id1643375332`\n"
            "`/app WhatsApp US -mac`\n"
        )
        sent_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=foldable_text_with_markdown_v2(help_message),
            parse_mode="MarkdownV2",
        )
        schedule_message_deletion(
            chat_id=sent_message.chat_id, message_id=sent_message.message_id, delay=30
        )
        return

    user_id = update.effective_user.id if update.effective_user else 0
    args_str_full = " ".join(context.args)

    # --- ✨✨✨ 新增的“安检门”，检查输入的是不是App ID ✨✨✨ ---
    id_match = re.match(r'id(\d+)', args_str_full.strip())

    if id_match:
        # 如果是 App ID, 就走 VIP 通道！
        app_id = id_match.group(1)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔍 正在通过 App ID `{app_id}` 直接查找..."
        )
        
        session = {
            "user_specified_countries": None,
            "search_data": {"app_type": "software"}
        }
        
        app_info = await SappSearchAPI.get_app_details(app_id=app_id, country="us")
        
        if app_info:
            # 伪造一个 callback_query 对象来复用 show_app_details
            from types import SimpleNamespace
            query_mock = SimpleNamespace(
                message=message,
                edit_message_text=message.edit_text
            )
            await show_app_details(query_mock, app_id, app_info, context, session)
        else:
            await message.edit_text(f"❌ 未找到 App ID 为 `{app_id}` 的应用。")
        return # VIP 通道任务完成，直接结束！

    # --- 安检门结束 ---
    # 如果不是 App ID, 就走下面的普通关键词搜索流程
    
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=foldable_text_v2("🔍 正在解析参数并准备搜索..."),
        parse_mode="MarkdownV2",
    )

    try:
        args_str_processed = args_str_full
        app_type = "software"

        if "-mac" in args_str_processed:
            app_type = "macSoftware"
            args_str_processed = args_str_processed.replace("-mac", "").strip()
        elif "-ipad" in args_str_processed:
            app_type = "iPadSoftware"
            args_str_processed = args_str_processed.replace("-ipad", "").strip()
        args_str_processed = " ".join(args_str_processed.split())

        countries_parsed: list[str] = []
        app_name_to_search = None

        # ... (后续的参数解析和搜索逻辑和原来保持一致) ...
        # (The rest of the argument parsing and search logic remains the same)

        # (This part is copied from the original code provided by the user)
        if not args_str_processed:
            error_message = "❌ 请输入应用名称。"
            await message.delete()
            config = get_config()
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=foldable_text_v2(error_message),
                parse_mode="MarkdownV2",
            )
            schedule_message_deletion(
                chat_id=sent_message.chat_id,
                message_id=sent_message.message_id,
                delay=config.auto_delete_delay,
            )
            return

        try:
            param_lexer = shlex.shlex(args_str_processed, posix=True)
            param_lexer.quotes = '"""＂'
            param_lexer.whitespace_split = True
            all_params_list = [p for p in list(param_lexer) if p]
        except ValueError as e:
            error_message = f"❌ 参数解析错误: {str(e)}"
            await message.delete()
            config = get_config()
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=foldable_text_v2(error_message),
                parse_mode="MarkdownV2",
            )
            schedule_message_deletion(
                chat_id=sent_message.chat_id,
                message_id=sent_message.message_id,
                delay=config.auto_delete_delay,
            )
            return

        if not all_params_list:
            error_message = "❌ 参数解析后为空，请输入应用名称。"
            await message.delete()
            config = get_config()
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=foldable_text_v2(error_message),
                parse_mode="MarkdownV2",
            )
            schedule_message_deletion(
                chat_id=sent_message.chat_id,
                message_id=sent_message.message_id,
                delay=config.auto_delete_delay,
            )
            return

        app_name_parts_collected = []
        for param_idx, param_val in enumerate(all_params_list):
            is_country = (
                param_val.upper() in SUPPORTED_COUNTRIES
                or param_val in COUNTRY_NAME_TO_CODE
            )
            if is_country:
                countries_parsed.extend(all_params_list[param_idx:])
                break
            app_name_parts_collected.append(param_val)

        if not app_name_parts_collected:
            error_message = "❌ 未能从输入中解析出有效的应用名称。"
            await message.delete()
            config = get_config()
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=foldable_text_v2(error_message),
                parse_mode="MarkdownV2",
            )
            schedule_message_deletion(
                chat_id=sent_message.chat_id,
                message_id=sent_message.message_id,
                delay=config.auto_delete_delay,
            )
            return
        app_name_to_search = " ".join(app_name_parts_collected)

        final_countries_to_search = []
        if not countries_parsed:
            final_countries_to_search = None
        else:
            for country_input_str in countries_parsed:
                resolved_code = COUNTRY_NAME_TO_CODE.get(
                    country_input_str, country_input_str.upper()
                )
                if (
                    resolved_code in SUPPORTED_COUNTRIES
                    and resolved_code not in final_countries_to_search
                ):
                    final_countries_to_search.append(resolved_code)
        
        session_id = str(uuid.uuid4())
        country_code = (
            final_countries_to_search[0] if final_countries_to_search else "US"
        ).lower()
        final_query = app_name_to_search
        
        platform_display = {
            "software": "iOS",
            "macSoftware": "macOS",
            "iPadSoftware": "iPadOS",
        }.get(app_type, "iOS")

        search_status_message = f"🔍 正在在 {country_code.upper()} 区域搜索 {platform_display} 应用 '{final_query}' ..."
        await message.edit_text(
            foldable_text_v2(search_status_message), parse_mode="MarkdownV2"
        )

        raw_search_data = await SappSearchAPI.search_apps(
            final_query, country=country_code, app_type=app_type, limit=200
        )
        all_results = raw_search_data.get("results", [])

        per_page = 5
        total_results = len(all_results)
        total_pages = (
            min(10, (total_results + per_page - 1) // per_page)
            if total_results > 0
            else 1
        )
        page_results = all_results[0:per_page]

        search_data_for_session = {
            "query": final_query,
            "country": country_code,
            "app_type": app_type,
            "all_results": all_results,
            "current_page": 1,
            "total_pages": total_pages,
            "total_results": total_results,
            "per_page": per_page,
            "results": page_results,
        }

        user_search_sessions[session_id] = {
            "user_id": user_id,
            "query": final_query,
            "search_data": search_data_for_session,
            "user_specified_countries": final_countries_to_search or None,
            "chat_id": update.effective_chat.id,
            "session_id": session_id,
            "created_at": datetime.now(),
            "user_command_message_id": update.message.message_id,
            "bot_response_message_id": message.message_id,
        }

        logger.info(
            f"✅ 新的App Store搜索会话已创建，ID: {session_id}, 用户: {user_id}, 聊天: {update.effective_chat.id}"
        )

        result_text = format_search_results(search_data_for_session)
        keyboard = create_search_keyboard(
            search_data_for_session, session_id
        )

        await message.edit_text(
            foldable_text_v2(result_text),
            reply_markup=keyboard,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )

        delete_delay = config_manager.config.auto_delete_delay
        logger.info(
            f"🔧 调度消息删除: 消息 {message.message_id} 将在 {delete_delay} 秒后删除"
        )

        task_id = schedule_message_deletion(
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
            delay=delete_delay,
            task_type="search_result",
            user_id=user_id,
            session_id=session_id,
        )
        if task_id:
            logger.info(
                f"✅ 成功调度删除任务 {task_id} 用于搜索结果消息 {message.message_id}"
            )
        else:
            logger.error(f"❌ 调度删除任务失败，消息 {message.message_id}")

        if config_manager.config.delete_user_commands and update.message:
            user_command_task_id = schedule_message_deletion(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                delay=config_manager.config.user_command_delete_delay,
                task_type="user_command",
                user_id=user_id,
                session_id=session_id,
            )
            if user_command_task_id:
                logger.info(f"✅ 成功调度用户命令删除任务 {user_command_task_id}")
            else:
                logger.error("❌ 调度用户命令删除任务失败")

    except Exception as e:
        logger.error(f"Search process error: {e}")
        error_message = f"❌ 搜索失败: {str(e)}\n\n请稍后重试或联系管理员."
        await message.delete()
        config = get_config()
        sent_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=foldable_text_v2(error_message),
            parse_mode="MarkdownV2",
        )
        schedule_message_deletion(
            sent_message.chat_id,
            sent_message.message_id,
            delay=config.auto_delete_delay,
        )

# ... (The rest of the file: handle_app_search_callback, show_app_details, etc., remains unchanged) ...
# ... (I will copy the rest of the original file from the user's input to append here) ...

async def handle_app_search_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """处理App搜索相关的回调查询"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id if update.effective_chat else None

    if not chat_id:
        logger.error("❌ 无法获取聊天ID")
        return

    try:
        parts = query.data.split("_")
        action = parts[1]
        session_id = parts[-1]
    except (IndexError, ValueError):
        await query.edit_message_text("无效的回调请求。")
        return

    session = user_search_sessions.get(session_id)
    if not session or session.get("user_id") != user_id:
        await query.edit_message_text("这是一个过期或无效的会话，请重新发起搜索。")
        return

    logger.info(
        f"🔍 Processing callback for session {session_id} (user={user_id}, chat={chat_id}): {query.data}"
    )

    try:
        if action == "select":
            app_index = int(parts[2])
            search_data = session["search_data"]
            if app_index < len(search_data["results"]):
                selected_app = search_data["results"][app_index]
                app_id = selected_app.get("trackId")

                if app_id:
                    loading_message = f"🔍 正在获取 '{selected_app.get('trackName', '应用')}' 的详细价格信息"
                    await query.edit_message_text(
                        foldable_text_v2(loading_message), parse_mode="MarkdownV2"
                    )
                    await show_app_details(
                        query, app_id, selected_app, context, session
                    )
                else:
                    error_message = "❌ 无法获取应用ID，请重新选择。"
                    await query.edit_message_text(
                        foldable_text_v2(error_message), parse_mode="MarkdownV2"
                    )

        elif action == "page":
            page_action = parts[2]
            if page_action == "info":
                return

            page = int(page_action)
            session["search_data"]["current_page"] = page
            search_data = session["search_data"]
            all_results = search_data["all_results"]
            per_page = search_data["per_page"]
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            page_results = all_results[start_index:end_index]
            search_data["results"] = page_results
            result_text = format_search_results(search_data)
            keyboard = create_search_keyboard(search_data, session_id)
            await query.edit_message_text(
                foldable_text_v2(result_text),
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )

        elif action == "change" and len(parts) > 2 and parts[2] == "region":
            change_region_text = "请选择新的搜索地区："
            region_buttons = [
                InlineKeyboardButton(
                    "🇨🇳 中国", callback_data=f"app_region_CN_{session_id}"
                ),
                InlineKeyboardButton(
                    "🇭🇰 香港", callback_data=f"app_region_HK_{session_id}"
                ),
                InlineKeyboardButton(
                    "🇹🇼 台湾", callback_data=f"app_region_TW_{session_id}"
                ),
                InlineKeyboardButton(
                    "🇯🇵 日本", callback_data=f"app_region_JP_{session_id}"
                ),
                InlineKeyboardButton(
                    "🇬🇧 英国", callback_data=f"app_region_GB_{session_id}"
                ),
                InlineKeyboardButton(
                    "❌ 关闭", callback_data=f"app_close_{session_id}"
                ),
            ]
            keyboard = [
                region_buttons[i : i + 2] for i in range(0, len(region_buttons), 2)
            ]
            await query.edit_message_text(
                foldable_text_v2(change_region_text),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2",
            )

        elif action == "region":
            country_code = parts[2]
            session["search_data"]["country"] = country_code.lower()
            search_data = session["search_data"]
            final_query = search_data["query"]
            app_type = search_data["app_type"]
            loading_message = (
                f"🔍 正在在 {country_code.upper()} 区域重新搜索 '{final_query}'..."
            )
            await query.edit_message_text(
                foldable_text_v2(loading_message), parse_mode="MarkdownV2"
            )
            raw_search_data = await SappSearchAPI.search_apps(
                final_query, country=country_code.lower(), app_type=app_type, limit=200
            )
            all_results = raw_search_data.get("results", [])
            per_page = 5
            total_results = len(all_results)
            total_pages = (
                min(10, (total_results + per_page - 1) // per_page)
                if total_results > 0
                else 1
            )
            page_results = all_results[0:per_page]
            search_data_for_session = {
                "query": final_query,
                "country": country_code.lower(),
                "app_type": app_type,
                "all_results": all_results,
                "current_page": 1,
                "total_pages": total_pages,
                "total_results": total_results,
                "per_page": per_page,
                "results": page_results,
            }
            session["search_data"] = search_data_for_session
            result_text = format_search_results(search_data_for_session)
            keyboard = create_search_keyboard(
                search_data_for_session, session_id
            )
            await query.edit_message_text(
                foldable_text_v2(result_text),
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
            )

        elif (
            action == "back"
            and len(parts) > 2
            and parts[2] == "to"
            and parts[3] == "search"
        ):
            search_data = session["search_data"]
            result_text = format_search_results(search_data)
            keyboard = create_search_keyboard(search_data, session_id)
            await query.edit_message_text(
                foldable_text_v2(result_text),
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )

        elif action == "new" and len(parts) > 2 and parts[2] == "search":
            new_search_message = "🔍 *开始新的搜索*\n\n请使用 `/app 应用名称` 命令开始新的搜索。\n\n例如: `/app 微信`"
            await query.edit_message_text(
                foldable_text_with_markdown_v2(new_search_message),
                parse_mode="MarkdownV2",
            )
            if session_id in user_search_sessions:
                del user_search_sessions[session_id]

        elif action == "close":
            from utils.message_manager import cancel_session_deletions
            cancelled_count = cancel_session_deletions(session_id)
            logger.info(
                f"✅ 已取消会话 {session_id} 的 {cancelled_count} 个定时删除任务"
            )
            try:
                await context.bot.delete_message(
                    chat_id=chat_id, message_id=session["bot_response_message_id"]
                )
                await context.bot.delete_message(
                    chat_id=chat_id, message_id=session["user_command_message_id"]
                )
                logger.info(f"✅ 已删除会话 {session_id} 的所有消息")
            except Exception as e:
                logger.error(f"❌ 删除消息时发生错误: {e}")
                await query.edit_message_text(
                    "🔍 搜索已关闭。\n\n使用 `/app 应用名称` 开始新的搜索。"
                )
            if session_id in user_search_sessions:
                del user_search_sessions[session_id]
                logger.info(f"✅ 会话 {session_id} 已由用户关闭并清理")

    except Exception as e:
        logger.error(f"处理回调查询时发生错误: {e}")
        error_message = f"❌ 操作失败: {str(e)}\n\n请重新搜索或联系管理员."
        await query.edit_message_text(
            foldable_text_v2(error_message), parse_mode="MarkdownV2"
        )


async def show_app_details(
    query,
    app_id: str,
    app_info: Dict,
    context: ContextTypes.DEFAULT_TYPE,
    session: Dict,
) -> None:
    try:
        user_specified_countries = session.get("user_specified_countries")
        countries_to_check = user_specified_countries or DEFAULT_COUNTRIES
        app_name = app_info.get("trackName", "未知应用")
        app_type = session.get("search_data", {}).get("app_type", "software")
        price_tasks = [
            get_app_prices(app_name, country, app_id, app_name, app_type, context)
            for country in countries_to_check
        ]
        price_results_raw = await asyncio.gather(*price_tasks)
        target_plan = find_common_plan(price_results_raw)
        successful_results = [res for res in price_results_raw if res["status"] == "ok"]
        sorted_results = sorted(
            successful_results, key=lambda res: sort_key_func(res, target_plan)
        )
        platform_info = {
            "software": {"icon": "📱", "name": "iOS"},
            "macSoftware": {"icon": "💻", "name": "macOS"},
            "iPadSoftware": {"icon": "📱", "name": "iPadOS"},
        }.get(app_type, {"icon": "📱", "name": "iOS"})
        header_lines = [f"{platform_info['icon']} *{app_name}*"]
        header_lines.append(f"🎯 平台: {platform_info['name']}")
        header_lines.append(f"🆔 App ID: `id{app_id}`")
        raw_header = "\n".join(header_lines)
        price_details_lines = []
        if not sorted_results:
            price_details_lines.append("在可查询的区域中未找到该应用的价格信息。")
        else:
            for res in sorted_results:
                country_name = res["country_name"]
                app_price_str = res["app_price_str"]
                price_details_lines.append(f"🌍 国家/地区: {country_name}")
                price_details_lines.append(f"💰 应用价格 : {app_price_str}")
                if res["app_price_cny"] is not None and res["app_price_cny"] > 0:
                    price_details_lines[-1] += f" (约 ¥{res['app_price_cny']:.2f} CNY)"
                if res.get("in_app_purchases"):
                    for iap in res["in_app_purchases"]:
                        iap_name = iap["name"]
                        iap_price = iap["price_str"]
                        iap_line = f"  •   {iap_name}: {iap_price}"
                        if iap["cny_price"] is not None and iap["cny_price"] != float(
                            "inf"
                        ):
                            iap_line += f" (约 ¥{iap['cny_price']:.2f} CNY)"
                        price_details_lines.append(iap_line)
                    price_details_lines.append("")
        price_details_text = "\n".join(price_details_lines)
        full_raw_message = f"{raw_header}\n\n{price_details_text}"
        formatted_message = foldable_text_with_markdown_v2(full_raw_message)
        await query.edit_message_text(
            formatted_message, parse_mode="MarkdownV2", disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"显示应用详情时发生错误: {e}", exc_info=True)
        error_message = f"❌ 获取应用详情失败: {str(e)}"
        await query.edit_message_text(
            foldable_text_v2(error_message), parse_mode="MarkdownV2"
        )


async def get_app_prices(
    app_name: str,
    country_code: str,
    app_id: int,
    app_name_from_store: str,
    app_type: str,
    context: ContextTypes.DEFAULT_TYPE,
) -> Dict:
    """Fetches and formats app and in-app purchase prices for a given country."""
    global cache_manager, rate_converter
    cache_key = f"app_prices_{app_id}_{country_code}_{app_type}"
    cached_data = cache_manager.load_cache(
        cache_key,
        max_age_seconds=config_manager.config.app_store_cache_duration,
        subdirectory="app_store",
    )
    if cached_data:
        cache_timestamp = cache_manager.get_cache_timestamp(
            cache_key, subdirectory="app_store"
        )
        cache_info = (
            f"*(缓存于: {datetime.fromtimestamp(cache_timestamp).strftime('%Y-%m-%d %H:%M')})*"
            if cache_timestamp
            else ""
        )
        return {
            "country_code": country_code,
            "country_name": SUPPORTED_COUNTRIES.get(country_code, {}).get(
                "name", country_code
            ),
            "flag_emoji": get_country_flag(country_code),
            "status": "ok",
            "app_price_str": cached_data.get("app_price_str"),
            "app_price_cny": cached_data.get("app_price_cny"),
            "in_app_purchases": cached_data.get("in_app_purchases", []),
            "cache_info": cache_info,
        }

    country_info = SUPPORTED_COUNTRIES.get(country_code, {})
    country_name = country_info.get("name", country_code)
    flag_emoji = get_country_flag(country_code)
    url = f"https://apps.apple.com/{country_code.lower()}/app/id{app_id}"
    try:
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            response = await client.get(url, timeout=12)
            response.raise_for_status()
            content = response.text
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.info(f"App 'id{app_id}' not found in {country_code} (404).")
            return {
                "country_code": country_code,
                "country_name": country_name,
                "flag_emoji": flag_emoji,
                "status": "not_listed",
                "error_message": "未上架",
            }
        else:
            logger.error(
                f"HTTP error fetching prices for {app_name} in {country_code}: {e}"
            )
            return {
                "country_code": country_code,
                "country_name": country_name,
                "flag_emoji": flag_emoji,
                "status": "error",
                "error_message": f"获取失败 (HTTP {e.response.status_code})",
            }
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch prices for {app_name} in {country_code}: {e}")
        return {
            "country_code": country_code,
            "country_name": country_name,
            "flag_emoji": flag_emoji,
            "status": "error",
            "error_message": "获取失败 (网络错误)",
        }
    except Exception as e:
        logger.error(
            f"Unknown error fetching prices for {app_name} in {country_code}: {e}"
        )
        return {
            "country_code": country_code,
            "country_name": country_name,
            "flag_emoji": flag_emoji,
            "status": "error",
            "error_message": "获取失败 (未知错误)",
        }
    try:
        try:
            soup = BeautifulSoup(content, "lxml")
        except Exception:
            soup = BeautifulSoup(content, "html.parser")
        app_price_str = "免费"
        app_price_cny = 0.0
        authoritative_currency = None
        script_tags = soup.find_all("script", type="application/ld+json")
        for script in script_tags:
            try:
                json_data = json.loads(script.string)
                if (
                    isinstance(json_data, dict)
                    and json_data.get("@type") == "SoftwareApplication"
                ):
                    offers = json_data.get("offers", {})
                    if offers:
                        price = offers.get("price", 0)
                        currency = offers.get("priceCurrency", "USD")
                        authoritative_currency = currency
                        category = offers.get("category", "").lower()
                        if category != "free" and float(price) > 0:
                            app_price_str = f"{price} {currency}"
                            if country_code != "CN" and rate_converter:
                                cny_price = await rate_converter.convert(
                                    float(price), currency, "CNY"
                                )
                                if cny_price is not None:
                                    app_price_cny = cny_price
                        break
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        in_app_items = soup.select("li.list-with-numbers__item")
        unique_items = set()
        in_app_purchases = []
        if in_app_items:
            for item in in_app_items:
                name_tag = item.find(
                    "span", class_="truncate-single-line truncate-single-line--block"
                )
                price_tag = item.find(
                    "span",
                    class_="list-with-numbers__item__price medium-show-tablecell",
                )
                if name_tag and price_tag:
                    name = name_tag.text.strip()
                    price_str = price_tag.text.strip()
                    if (name, price_str) not in unique_items:
                        unique_items.add((name, price_str))
                        in_app_cny_price = None
                        if country_code != "CN" and rate_converter:
                            detected_currency, price_value = extract_currency_and_price(
                                price_str, country_code
                            )
                            if authoritative_currency:
                                detected_currency = authoritative_currency
                            if price_value is not None:
                                cny_price = await rate_converter.convert(
                                    price_value, detected_currency, "CNY"
                                )
                                if cny_price is not None:
                                    in_app_cny_price = cny_price
                        in_app_purchases.append(
                            {
                                "name": name,
                                "price_str": price_str,
                                "cny_price": in_app_cny_price,
                            }
                        )
        result_data = {
            "country_code": country_code,
            "country_name": country_name,
            "flag_emoji": flag_emoji,
            "status": "ok",
            "app_price_str": app_price_str,
            "app_price_cny": app_price_cny,
            "in_app_purchases": in_app_purchases,
        }
        cache_manager.save_cache(cache_key, result_data, subdirectory="app_store")
        return result_data
    except Exception as e:
        logger.error(f"Error parsing prices for {app_name} in {country_code}: {e}")
        return {
            "country_code": country_code,
            "country_name": country_name,
            "flag_emoji": flag_emoji,
            "status": "error",
            "error_message": "解析失败",
        }


def extract_cny_price(price_str: str) -> float:
    """Extracts CNY price from a formatted string for sorting."""
    if "免费" in price_str:
        return 0.0
    match = re.search(r"\(约 ¥([\d,.]+)\)", price_str)
    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return float("inf")
    return float("inf")


def find_common_plan(all_price_data: list[Dict]) -> str | None:
    """Finds the most common subscription plan name across all results for sorting."""
    plan_counts = {}
    for price_data in all_price_data:
        if price_data["status"] == "ok":
            for iap in price_data.get("in_app_purchases", []):
                plan_name = iap["name"]
                plan_counts[plan_name] = plan_counts.get(plan_name, 0) + 1
    if not plan_counts:
        return None
    max_count = max(plan_counts.values())
    common_plans = [plan for plan, count in plan_counts.items() if count == max_count]
    for keyword in ["Pro", "Premium", "Plus", "Standard"]:
        for plan in common_plans:
            if keyword in plan:
                return plan
    return common_plans[0] if common_plans else None


def sort_key_func(
    price_data: Dict, target_plan: str | None = None
) -> tuple[float, float]:
    """Sorting key function for price results, prioritizing target plan or cheapest in-app/app price."""
    if price_data["status"] != "ok":
        return (float("inf"), float("inf"))
    app_price = price_data.get("app_price_cny", float("inf"))
    target_plan_price = float("inf")
    min_in_app_price = float("inf")
    in_app_purchases = price_data.get("in_app_purchases", [])
    for iap in in_app_purchases:
        cny_price = iap.get("cny_price")
        if cny_price is not None:
            if iap["name"] == target_plan:
                target_plan_price = cny_price
            min_in_app_price = min(min_in_app_price, cny_price)
    if target_plan_price != float("inf"):
        effective_price = target_plan_price
    elif min_in_app_price != float("inf"):
        effective_price = min_in_app_price
    else:
        effective_price = app_price
    return (effective_price, app_price)


async def app_store_clean_cache_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """清理App Store缓存"""
    if not update.effective_user or not update.effective_chat:
        return
    user_id = update.effective_user.id
    from utils.compatibility_adapters import AdminManager
    from utils.cache_manager import CacheManager
    admin_manager = AdminManager()
    if not (
        admin_manager.is_super_admin(user_id)
        or admin_manager.has_permission(user_id, "manage_cache")
    ):
        sent_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text="❌ 你没有缓存管理权限。"
        )
        schedule_message_deletion(
            chat_id=sent_message.chat_id, message_id=sent_message.message_id, delay=5
        )
        return
    try:
        cache_manager = CacheManager()
        cleared_count = 0
        cache_manager.clear_cache(key_prefix="app_prices")
        cache_manager.clear_cache(subdirectory="app_store")
        app_store_path = cache_manager.cache_dir / "app_store"
        if app_store_path.exists():
            cleared_count += len(list(app_store_path.glob("*.json")))
        cleared_count += len(list(cache_manager.cache_dir.glob("app_prices*.json")))
        result_text = f"✅ App Store缓存清理完成\n\n清理了 {cleared_count} 个缓存文件"
        sent_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=foldable_text_v2(result_text),
            parse_mode="MarkdownV2",
        )
        schedule_message_deletion(
            chat_id=sent_message.chat_id, message_id=sent_message.message_id, delay=10
        )
    except Exception as e:
        logger.error(f"App Store缓存清理失败: {e}")
        sent_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"❌ 缓存清理失败: {str(e)}"
        )
        schedule_message_deletion(
            chat_id=sent_message.chat_id, message_id=sent_message.message_id, delay=5
        )

# Register commands
command_factory.register_command(
    "app",
    app_command,
    permission=Permission.USER,
    description="App Store应用搜索（支持iOS/macOS/iPadOS平台筛选）",
)
command_factory.register_command(
    "app_cleancache",
    app_store_clean_cache_command,
    permission=Permission.ADMIN,
    description="清理App Store缓存",
)
command_factory.register_callback(
    "^app_",
    handle_app_search_callback,
    permission=Permission.USER,
    description="App搜索回调处理",
)
