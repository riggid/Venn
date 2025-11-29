"""Group data repository."""
import json
from typing import Dict, List, Optional
from datetime import datetime


class GroupsRepository:
    """Repository for managing group data."""
    
    def __init__(self, file_path: str = "groups.json"):
        self.file_path = file_path
    
    def load_all(self) -> Dict:
        """Load all groups from JSON file."""
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_all(self, groups: Dict) -> None:
        """Save all groups to JSON file."""
        with open(self.file_path, "w") as f:
            json.dump(groups, f, indent=2)
    
    def get(self, group_name: str) -> Optional[Dict]:
        """Get group by name."""
        groups = self.load_all()
        return groups.get(group_name)
    
    def create(self, group_name: str, members: List[str], vibe: str, 
               created_by: str) -> None:
        """Create a new group."""
        groups = self.load_all()
        groups[group_name] = {
            "members": members,
            "vibe": vibe,
            "created_by": created_by,
            "created_at": datetime.now().isoformat()
        }
        self.save_all(groups)
    
    def add_member(self, group_name: str, member_email: str) -> None:
        """Add a member to a group."""
        groups = self.load_all()
        if group_name in groups:
            if member_email not in groups[group_name].get("members", []):
                groups[group_name]["members"].append(member_email)
                self.save_all(groups)
    
    def get_user_groups(self, user_email: str) -> Dict:
        """Get all groups that a user is a member of."""
        groups = self.load_all()
        return {
            name: data for name, data in groups.items()
            if user_email in data.get("members", [])
        }
    
    def exists(self, group_name: str) -> bool:
        """Check if group exists."""
        groups = self.load_all()
        return group_name in groups
    
    def remove_member(self, group_name: str, member_email: str) -> bool:
        """Remove a member from a group. Returns True if successful."""
        groups = self.load_all()
        if group_name in groups:
            members = groups[group_name].get("members", [])
            if member_email in members:
                members.remove(member_email)
                groups[group_name]["members"] = members
                # If no members left, delete the group
                if not members:
                    del groups[group_name]
                self.save_all(groups)
                return True
        return False
    
    def delete(self, group_name: str) -> bool:
        """Delete a group. Returns True if successful."""
        groups = self.load_all()
        if group_name in groups:
            del groups[group_name]
            self.save_all(groups)
            return True
        return False
    
    def search(self, query: str) -> Dict:
        """Search groups by name or vibe."""
        groups = self.load_all()
        query_lower = query.lower()
        return {
            name: data for name, data in groups.items()
            if query_lower in name.lower() or query_lower in data.get("vibe", "").lower()
        }

