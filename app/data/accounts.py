"""Account data repository."""
import json
from typing import Dict, Optional


class AccountsRepository:
    """Repository for managing account data."""
    
    def __init__(self, file_path: str = "accounts.json"):
        self.file_path = file_path
    
    def load_all(self) -> Dict:
        """Load all accounts from JSON file."""
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_all(self, accounts: Dict) -> None:
        """Save all accounts to JSON file."""
        with open(self.file_path, "w") as f:
            json.dump(accounts, f, indent=2)
    
    def get(self, email: str) -> Optional[Dict]:
        """Get account by email."""
        accounts = self.load_all()
        return accounts.get(email)
    
    def save(self, email: str, account_data: Dict) -> None:
        """Save or update an account."""
        accounts = self.load_all()
        accounts[email] = account_data
        self.save_all(accounts)
    
    def exists(self, email: str) -> bool:
        """Check if account exists."""
        accounts = self.load_all()
        return email in accounts

