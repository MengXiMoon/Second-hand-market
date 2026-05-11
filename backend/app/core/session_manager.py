import time
from typing import Dict, Optional


class SessionManager:
    """管控各账号的唯一活跃登录：同一账号只能在一台设备在线，先登录的不会被顶号"""

    def __init__(self):
        # user_id -> {"username": str, "login_at": float}
        self._sessions: Dict[int, dict] = {}

    def is_logged_in(self, user_id: int) -> bool:
        return user_id in self._sessions

    def login(self, user_id: int, username: str) -> None:
        self._sessions[user_id] = {"username": username, "login_at": time.time()}

    def logout(self, user_id: int) -> None:
        self._sessions.pop(user_id, None)

    def get_session(self, user_id: int) -> Optional[dict]:
        return self._sessions.get(user_id)

    def clear_expired(self, max_age_seconds: int = 86400) -> int:
        """清理超过 max_age_seconds 的会话，返回清理数量"""
        now = time.time()
        expired = [uid for uid, s in self._sessions.items() if now - s["login_at"] > max_age_seconds]
        for uid in expired:
            self._sessions.pop(uid, None)
        return len(expired)


session_manager = SessionManager()
