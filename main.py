#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多功能Telegram价格查询机器人
支持汇率查询、Steam游戏价格、流媒体订阅价格、应用商店价格查询等功能

功能特点:
- 汇率实时查询和转换
- Steam游戏价格多国对比
- Netflix、Disney+、Spotify等流媒体价格查询
- App Store、Google Play应用价格查询
- 管理员权限系统
- 用户和群组白名单管理
- 用户缓存管理
"""

import asyncio
import importlib
import logging
import logging.handlers
import os
import pkgutil

import httpx
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# 导入环境变量配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv 未安装，直接使用环境变量")

# ========================================
# 配置日志系统
# ========================================
from utils.config_manager import get_config

config = get_config()

# 确保日志目录存在
os.makedirs(os.path.dirname(config.log_file), exist_ok=True)

# 配置日志系统（带轮换和压缩）
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    handlers=[
        logging.handlers.RotatingFileHandler(
            config.log_file, 
            maxBytes=config.log_max_size,
            backupCount=config.log_backup_count,
            encoding="utf-8"
        ), 
        logging.StreamHandler()
    ],
)

# 设置第三方库日志级别
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# 输出关键配置信息
logger.info("=" * 50)
logger.info(" Telegram Bot 启动")
logger.info("=" * 50)
logger.info(f" 自动删除延迟: {config.auto_delete_delay} 秒")
logger.info(f" 用户命令删除延迟: {config.user_command_delete_delay} 秒")
logger.info(f" 删除用户命令: {'启用' if config.delete_user_commands else '禁用'}")
logger.info(f" 日志级别: {config.log_level.upper()}")
logger.info("=" * 50)

# ========================================
# 导入核心模块
# ========================================
from utils.cache_manager import CacheManager
from utils.command_factory import command_factory
from utils.error_handling import with_error_handling
from utils.permissions import Permission
from utils.rate_converter import RateConverter
from utils.task_scheduler import init_task_scheduler
from utils.script_loader import init_script_loader
from utils.message_delete_scheduler import message_delete_scheduler
from utils.log_manager import schedule_log_maintenance
from utils.user_cache_manager import get_user_cache_manager  # 新增：导入用户缓存管理器

# ========================================
# 导入命令模块
# ========================================
from commands import (
    app_store,
    apple_services,
    disney_plus,
    google_play,
    netflix,
    spotify,
    steam,
    system_commands,
)
from commands.rate_command import set_rate_converter


@with_error_handling
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理错误"""
    logger.error("Exception while handling an update:", exc_info=context.error)

    # 尝试向用户发送错误信息
    if isinstance(update, Update) and update.effective_message:
        try:
            from utils.message_manager import send_and_auto_delete
            from utils.config_manager import get_config
            config = get_config()
            
            # 使用自动删除功能发送错误消息
            await send_and_auto_delete(
                context=context,
                chat_id=update.effective_chat.id,
                text="❌ 处理请求时发生错误，请稍后重试。\n"
                     "如果问题持续存在，请联系管理员。",
                delay=config.auto_delete_delay,
                command_message_id=update.effective_message.message_id if hasattr(update.effective_message, 'message_id') else None
            )
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")  # 记录失败原因而不是静默忽略


def load_commands():
    """动态加载并注册所有命令"""
    commands_dir = "commands"
    for _, name, _ in pkgutil.iter_modules([commands_dir]):
        try:
            importlib.import_module(f"{commands_dir}.{name}")
            logger.info(f"成功加载命令模块: {name}")
        except Exception as e:
            logger.error(f"加载命令模块 {name} 失败: {e}")


def setup_handlers(application: Application):
    """设置命令处理器"""

    # 动态加载所有命令
    load_commands()

    # 使用命令工厂设置处理器
    command_factory.setup_handlers(application)

    # 手动添加管理员对话处理器
    from commands.admin_commands import admin_panel_handler

    application.add_handler(admin_panel_handler.get_conversation_handler())

    # 错误处理器
    application.add_error_handler(error_handler)

    logger.info("所有命令处理器已设置完成")


async def setup_application(application: Application, config) -> None:
    """异步设置应用"""
    logger.info(" 开始初始化机器人应用...")
    
    # ========================================
    # 第一步：初始化核心组件
    # ========================================
    logger.info(" 初始化核心组件...")
    cache_manager = CacheManager(config.cache_dir)
    rate_converter = RateConverter(config.exchange_rate_api_keys, cache_manager)
    httpx_client = httpx.AsyncClient()
    
    # 新增：初始化用户缓存管理器
    user_cache_manager = get_user_cache_manager()
    
    # 将核心组件存储到 bot_data 中
    application.bot_data["cache_manager"] = cache_manager
    application.bot_data["rate_converter"] = rate_converter
    application.bot_data["httpx_client"] = httpx_client
    application.bot_data["user_cache_manager"] = user_cache_manager  # 新增
    logger.info("✅ 核心组件初始化完成")

    # ========================================
    # 第二步：为命令模块注入依赖
    # ========================================
    logger.info(" 注入命令模块依赖...")
    set_rate_converter(rate_converter)
    steam.set_rate_converter(rate_converter)
    steam.set_cache_manager(cache_manager)
    steam.set_steam_checker(cache_manager, rate_converter)
    netflix.set_rate_converter(rate_converter)
    disney_plus.set_rate_converter(rate_converter)
    spotify.set_dependencies(cache_manager, rate_converter)
    app_store.set_rate_converter(rate_converter)
    app_store.set_cache_manager(cache_manager)
    google_play.set_rate_converter(rate_converter)
    apple_services.set_rate_converter(rate_converter)
    
    # 新增：为需要用户缓存的模块注入依赖
    # 这里可以根据实际需要为特定命令模块注入用户缓存管理器
    # 例如：system_commands.set_user_cache_manager(user_cache_manager)
    
    logger.info("✅ 命令模块依赖注入完成")

    # ========================================
    # 第三步：初始化任务管理系统
    # ========================================
    logger.info("⚙️ 初始化任务管理系统...")
    
    # 初始化任务管理器
    from utils.task_manager import get_task_manager
    task_manager = get_task_manager()
    logger.info(f" 任务管理器已初始化，最大任务数: {task_manager.max_tasks}")
    
    # 初始化定时任务调度器
    task_scheduler = init_task_scheduler(cache_manager)
    application.bot_data["task_scheduler"] = task_scheduler
    
    # 根据配置添加定时清理任务
    cleanup_tasks_added = 0
    if config.spotify_weekly_cleanup:
        task_scheduler.add_weekly_cache_cleanup("spotify", "spotify", weekday=6, hour=5, minute=0)
        logger.info(" 已配置 Spotify 每周日UTC 5:00 定时清理")
        cleanup_tasks_added += 1
    
    if config.disney_weekly_cleanup:
        task_scheduler.add_weekly_cache_cleanup("disney_plus", "disney_plus", weekday=6, hour=5, minute=0)
        logger.info(" 已配置 Disney+ 每周日UTC 5:00 定时清理")
        cleanup_tasks_added += 1
    
    # 启动任务调度器（如果有任务）
    if cleanup_tasks_added > 0:
        task_scheduler.start()
        logger.info(f" 定时任务调度器已启动，活动任务: {cleanup_tasks_added} 个")
    else:
        logger.info("⏸️ 无定时清理任务，调度器保持待机状态")
    
    # 启动消息删除调度器
    message_delete_scheduler.start(application.bot)
    application.bot_data["message_delete_scheduler"] = message_delete_scheduler
    logger.info("️ 消息删除调度器已启动")
    
    # 调度日志维护任务
    schedule_log_maintenance()
    logger.info(" 日志维护任务已调度")
    
    logger.info("✅ 任务管理系统初始化完成")

    # ========================================
    # 第四步：预加载数据
    # ========================================
    logger.info(" 预加载数据...")
    try:
        await rate_converter.get_rates()
        logger.info("✅ 汇率数据预加载完成")
    except Exception as e:
        logger.warning(f"⚠️ 汇率数据预加载失败: {e}")

    # ========================================
    # 第五步：设置命令处理器
    # ========================================
    logger.info(" 设置命令处理器...")
    setup_handlers(application)
    logger.info("✅ 命令处理器设置完成")

    # ========================================
    # 第六步：设置机器人命令菜单
    # ========================================
    logger.info(" 设置机器人命令菜单...")
    
    # 获取所有权限级别的命令
    user_commands = command_factory.get_command_list(Permission.USER)
    admin_commands = command_factory.get_command_list(Permission.ADMIN)
    super_admin_commands = command_factory.get_command_list(Permission.SUPER_ADMIN)
    
    # 合并所有命令（超级管理员能看到所有命令）
    all_commands = {}
    all_commands.update(user_commands)
    all_commands.update(admin_commands)
    all_commands.update(super_admin_commands)
    
    # 手动添加由ConversationHandler处理的admin命令
    all_commands["admin"] = "打开管理员面板"
    
    # 创建机器人命令列表
    bot_commands = [
        BotCommand(command, description) for command, description in all_commands.items()
    ]
    
    try:
        await application.bot.set_my_commands(bot_commands)
        logger.info(f"✅ 命令菜单设置完成:")
        logger.info(f" 用户命令: {len(user_commands)} 条")
        logger.info(f"‍ 管理员命令: {len(admin_commands)} 条")
        logger.info(f" 超级管理员命令: {len(super_admin_commands)} 条")
        logger.info(f" 总计: {len(bot_commands)} 条命令")
    except Exception as e:
        logger.error(f"❌ 设置机器人命令菜单失败: {e}")

    # ========================================
    # 第七步：加载自定义脚本（可选）
    # ========================================
    if config.load_custom_scripts:
        logger.info(" 加载自定义脚本...")
        script_loader = init_script_loader(config.custom_scripts_dir)
        
        # 准备机器人上下文供脚本使用
        bot_context = {
            'application': application,
            'cache_manager': cache_manager,
            'rate_converter': rate_converter,
            'task_scheduler': task_scheduler,
            'user_cache_manager': user_cache_manager,  # 新增：为脚本提供用户缓存管理器
            'config': config,
            'logger': logger
        }
        
        # 加载脚本
        success = script_loader.load_scripts(bot_context)
        if success:
            logger.info("✅ 自定义脚本加载完成")
        else:
            logger.warning("⚠️ 部分自定义脚本加载失败")
            
        # 将脚本加载器存储到bot_data中
        application.bot_data["script_loader"] = script_loader
    else:
        logger.info(" 自定义脚本加载已禁用")
    
    logger.info(" 机器人应用初始化完成！")


async def cleanup_application(application: Application) -> None:
    """清理应用资源"""
    logger.info(" 开始清理应用资源...")
    
    try:
        # ========================================
        # 第一步：关闭网络连接
        # ========================================
        if "httpx_client" in application.bot_data:
            await application.bot_data["httpx_client"].aclose()
            logger.info("✅ httpx客户端已关闭")
        
        # ========================================
        # 第二步：停止调度器
        # ========================================
        if "task_scheduler" in application.bot_data:
            application.bot_data["task_scheduler"].stop()
            logger.info("✅ 定时任务调度器已停止")
        
        if "message_delete_scheduler" in application.bot_data:
            application.bot_data["message_delete_scheduler"].stop()
            logger.info("✅ 消息删除调度器已停止")
        
        # ========================================
        # 第三步：关闭任务管理器
        # ========================================
        from utils.task_manager import shutdown_task_manager
        await shutdown_task_manager()
        logger.info("✅ 任务管理器已关闭")
        
        # ========================================
        # 第四步：清理用户缓存管理器（如果需要）
        # ========================================
        # 用户缓存管理器使用 SQLite，通常不需要特殊清理
        # 但如果有连接池或其他资源，可以在这里处理
        
        logger.info(" 应用资源清理完成")
            
    except Exception as e:
        logger.error(f"❌ 清理资源时出错: {e}")


def main() -> None:
    """主函数"""
    # ========================================
    # 第一步：验证环境配置
    # ========================================
    logger.info(" 验证环境配置...")
    config = get_config()
    
    # 验证 Bot Token
    bot_token = config.bot_token
    if not bot_token:
        logger.error("❌ 未设置 BOT_TOKEN 环境变量")
        return

    # 验证超级管理员ID
    super_admin_id = config.super_admin_id
    if not super_admin_id:
        logger.error("❌ 未设置 SUPER_ADMIN_ID 环境变量")
        return

    try:
        int(super_admin_id)
        logger.info(f"✅ 超级管理员ID: {super_admin_id}")
    except ValueError:
        logger.error("❌ SUPER_ADMIN_ID 必须是数字")
        return

    # ========================================
    # 第二步：创建并配置应用
    # ========================================
    logger.info(" 创建 Telegram Bot 应用...")
    application = Application.builder().token(bot_token).build()

    # 设置异步初始化和清理回调
    async def init_and_run(app):
        await setup_application(app, config)
        logger.info("✅ 机器人启动完成，开始服务...")
    
    application.post_init = init_and_run
    application.post_shutdown = cleanup_application

    # ========================================
    # 第三步：启动机器人
    # ========================================
    try:
        if config.webhook_url:
            # Webhook 模式
            url_path = f"/telegram/{config.bot_token}/webhook"
            webhook_url = f"{config.webhook_url.rstrip('/')}{url_path}"

            logger.info(" Webhook 模式启动")
            logger.info(f" Webhook URL: {webhook_url}")
            logger.info(f" 本地监听: {config.webhook_listen}:{config.webhook_port}")
            
            application.run_webhook(
                listen=config.webhook_listen,
                port=config.webhook_port,
                url_path=url_path,
                secret_token=config.webhook_secret_token,
                webhook_url=webhook_url
            )
        else:
            # Polling 模式
            logger.info(" Polling 模式启动")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except KeyboardInterrupt:
        logger.info("⏹️ 接收到停止信号，正在关闭机器人...")
    except Exception as e:
        logger.error(f"❌ 机器人运行时出错: {e}")
    finally:
        logger.info(" 机器人已停止")


if __name__ == "__main__":
    main()