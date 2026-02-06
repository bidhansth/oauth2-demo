from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
import secrets

class StateStorage:
    def __init__(self, expiry_minutes: int = 10):
        self._store: Dict[str, dict] = {}
        self.expiry_minutes = expiry_minutes

    def create_state_and_nonce(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        self._store[state] = {
            "nonce": nonce,
            "created_at": datetime.now(timezone.utc)
        }
        
        return state, nonce
    
    def get_nonce(self, state: str) -> Optional[str]:
        self._cleanup_expired()

        data = self._store.pop(state, None)
        if data is None:
            return None
        
        age = datetime.now(timezone.utc) - data["created_at"]
        if age > timedelta(minutes=self.expiry_minutes):
            return None
        
        return data["nonce"]
    
    def _cleanup_expired(self):
        now = datetime.now(timezone.utc)
        expired_keys = [
            state
            for state, data in self._store.items()
            if now - data["created_at"] > timedelta(minutes=self.expiry_minutes)
        ]
        for key in expired_keys:
            del self._store[key]

state_storage = StateStorage(expiry_minutes=10)