# session_manager.py
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from logs import logging

class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sessions = {}
            cls._instance.session_ttl = timedelta(hours=1)
        return cls._instance
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_ttl = timedelta(hours=1)

    def create_session(self, user_id: str) -> str:
        session_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': now,
            'expires_at': now + self.session_ttl,
            'ip': None,
            'user_agent': None
        }
        logging.info(f"Session id created - {session_id} for user : {user_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        if session_id not in self.sessions:
            logging.warning("session does not exist : {session_id}")
            return None
            
        session = self.sessions[session_id]
        now = datetime.now(timezone.utc)
        
        if now > session['expires_at']:
            logging.warning(f"session expired")
            del self.sessions[session_id]
            return None
            
        session['expires_at'] = now + self.session_ttl
        return session

    def destroy_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionManager()