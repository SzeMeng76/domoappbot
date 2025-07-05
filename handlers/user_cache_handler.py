#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户缓存处理器
自动缓存所有消息发送者的用户信息
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.config_manager import get_config

logger = logging.getLogger(__name__)

async def cache_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    自动缓存用户信息的处理器
    """
    logger.debug(f"[UserCache] 处理器被触发")

    # 获取用户缓存管理器
    user_cache_manager = context.bot_data.get('user_cache_manager')
    if not user_cache_manager:
        logger.error(f"[UserCache] 无法获取用户缓存管理器")
        return

    # 获取消息和用户信息
    message = update.message
    if not message or not message.from_user:
        logger.debug(f"[UserCache] 消息或用户信息为空")
        return

    user = message.from_user
    chat_id = message.chat.id

    logger.debug(f"[UserCache] 处理消息: 用户={user.id}(@{user.username}), 群组={chat_id}")

    # 只缓存有用户名的用户
    if user.username:
        try:
            user_cache_manager.update_user_cache(user, chat_id)
            logger.info(f"[UserCache] 已缓存用户信息: {user.id} (@{user.username}) 来自群组: {chat_id}")
        except Exception as e:
            logger.error(f"[UserCache] 缓存用户信息失败: {e}")
    else:
        logger.debug(f"[UserCache] 跳过无用户名用户: {user.id} ({user.first_name}) 来自群组: {chat_id}")

def setup_user_cache_handler(application):
    """
    设置用户缓存处理器
    """
    config = get_config()

    # 检查是否启用用户缓存
    if not config.enable_user_cache:
        logger.info("用户缓存功能已禁用，跳过设置用户缓存处理器")
        return

    # 检查是否配置了监听群组
    if not config.user_cache_group_ids:
        logger.info("未配置用户缓存监听群组，跳过设置用户缓存处理器")
        return

    # 创建群组过滤器，只监听配置中的群组
    group_filter = filters.Chat(config.user_cache_group_ids)

    # 创建消息处理器，只监听配置中的超级群组消息
    handler = MessageHandler(
        filters.ChatType.SUPERGROUP & filters.TEXT & group_filter,
        cache_user_info
    )

    # 添加到应用程序，使用默认优先级
    application.add_handler(handler)

    logger.info(f"✅ 用户缓存处理器已设置，监听 {len(config.user_cache_group_ids)} 个群组: {config.user_cache_group_ids}")
