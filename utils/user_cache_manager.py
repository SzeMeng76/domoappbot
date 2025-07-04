#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户缓存管理器
"""

import sqlite3
import logging
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
from telegram import User
from utils.config_manager import get_config

logger = logging.getLogger(__name__)

class UserCacheManager:
    """用户缓存管理器"""

    def __init__(self, db_path: str = "data/user.db"):
        self.db_path = db_path
        self.config = get_config()
        if self.config.enable_user_cache:
            self._init_table()

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def _init_table(self):
        """初始化用户缓存表"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_cache (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON user_cache (user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON user_cache (username)")
                conn.commit()
                logger.info("用户缓存表 'user_cache' 初始化完成")
        except Exception as e:
            logger.error(f"初始化用户缓存表失败: {e}")
            raise

    def update_user_cache(self, user: User, chat_id: int):
        """根据配置更新或插入用户信息到缓存"""
        # 第一重门：检查总开关
        if not self.config.enable_user_cache:
            return

        # 第二重门：检查是否在指定群组
        if self.config.user_cache_group_ids and chat_id not in self.config.user_cache_group_ids:
            return
            
        # 第三重门：只处理有用户名的用户
        if not user.username:
            return

        try:
            with self.get_connection() as conn:
                current_time = time.time()
                conn.execute("""
                    INSERT INTO user_cache (user_id, username, first_name, last_name, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        first_name = excluded.first_name,
                        last_name = excluded.last_name,
                        last_seen = excluded.last_seen
                """, (user.id, user.username, user.first_name, user.last_name, current_time))
                conn.commit()
                logger.debug(f"已更新用户缓存: {user.id} (@{user.username})")
        except Exception as e:
            logger.error(f"更新用户缓存失败: {e}")

    def get_user_from_cache(self, user_id: int) -> Optional[Dict[str, Any]]:
        """从缓存中获取用户信息"""
        if not self.config.enable_user_cache:
            return None
        try:
            with self.get_connection() as conn:
                result = conn.execute("SELECT * FROM user_cache WHERE user_id = ?", (user_id,)).fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"从缓存获取用户失败: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """通过用户名从缓存中获取用户信息"""
        if not self.config.enable_user_cache:
            return None
        try:
            with self.get_connection() as conn:
                # 查询时忽略大小写
                result = conn.execute("SELECT * FROM user_cache WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"通过用户名获取用户失败: {e}")
            return None

_user_cache_manager = None

def get_user_cache_manager() -> UserCacheManager:
    """获取用户缓存管理器实例（单例模式）"""
    global _user_cache_manager
    if _user_cache_manager is None:
        _user_cache_manager = UserCacheManager()
    return _user_cache_manager
