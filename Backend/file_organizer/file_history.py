"""
File Movement History Tracking
"""

import json
import time
from pathlib import Path
from typing import List, Dict
from config.settings import DATA_DIR

HISTORY_FILE = DATA_DIR / "file_history.json"


class FileHistory:
    def __init__(self):
        self.history: List[Dict] = []
        self.load_history()
    
    def load_history(self):
        """Load history from disk"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
                print(f"📜 Loaded {len(self.history)} history entries")
            except Exception as e:
                print(f"⚠️ Error loading history: {e}")
                self.history = []
        else:
            self.history = []
            print("📜 No history file found, starting fresh")
    
    def save_history(self):
        """Save history to disk"""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving history: {e}")
    
    def add_movement(self, file_name: str, from_path: str, to_path: str, 
                     category: str, confidence: float, detection: str = "AI Detection"):
        """Add a new file movement to history"""
        movement = {
            "id": int(time.time() * 1000),  # Unique ID
            "filename": file_name,
            "fromPath": from_path,
            "toPath": to_path,
            "category": category,
            "confidence": f"{int(confidence * 100)}%",
            "detection": detection,
            "timestamp": time.time(),
            "timeAgo": "Just now",
            "status": "completed"
        }
        
        self.history.insert(0, movement)  # Add to beginning
        
        # Keep only last 1000 movements
        if len(self.history) > 1000:
            self.history = self.history[:1000]
        
        self.save_history()
        print(f"📝 Added to history: {file_name} -> {category}")
        return movement
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent history with time ago calculations"""
        current_time = time.time()
        
        for movement in self.history[:limit]:
            time_diff = current_time - movement.get('timestamp', current_time)
            movement['timeAgo'] = self._format_time_ago(time_diff)
        
        return self.history[:limit]
    
    def get_movement_by_id(self, movement_id: int) -> Dict:
        """Get a specific movement by ID"""
        for movement in self.history:
            if movement['id'] == movement_id:
                return movement
        return None
    
    def update_movement_status(self, movement_id: int, status: str):
        """Update the status of a movement (for undo)"""
        for movement in self.history:
            if movement['id'] == movement_id:
                movement['status'] = status
                self.save_history()
                return movement
        return None
    
    def _format_time_ago(self, seconds: float) -> str:
        """Format seconds into human-readable time ago"""
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} min{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
    
    def get_stats(self) -> Dict:
        """Get statistics about file movements"""
        total = len(self.history)
        completed = sum(1 for m in self.history if m.get('status') == 'completed')
        undone = sum(1 for m in self.history if m.get('status') == 'undone')
        
        # Calculate average confidence
        confidences = []
        for m in self.history:
            conf_str = m.get('confidence', '0%')
            try:
                conf_val = int(conf_str.rstrip('%'))
                confidences.append(conf_val)
            except:
                pass
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "total": total,
            "completed": completed,
            "undone": undone,
            "pending": 0,
            "success_rate": f"{int(avg_confidence)}%"
        }


# Global instance
file_history = FileHistory()