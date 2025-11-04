"""
Move Logger - Tracks file movements and generates session reports
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict
from config.settings import MOVE_LOGS_DIR
import json


class MoveSession:
    """Track a batch of file movements"""
    
    def __init__(self):
        self.session_start = datetime.now()
        self.moves = []
    
    def add_move(self, original_path: str, destination_path: str, category: str, 
                 confidence: float, summary: str = ""):
        """Record a file movement"""
        self.moves.append({
            "timestamp": datetime.now().isoformat(),
            "original_path": original_path,
            "destination_path": destination_path,
            "filename": Path(original_path).name,
            "category": category,
            "confidence": confidence,
            "summary": summary
        })
    
    def generate_report(self) -> str:
        """Generate a text report of all moves in this session"""
        if not self.moves:
            return "No files moved in this session."
        
        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds()
        
        report = []
        report.append("=" * 80)
        report.append("LEOLOGIC FILE ORGANIZATION REPORT")
        report.append("=" * 80)
        report.append(f"Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Session End:   {session_end.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration:      {duration:.1f} seconds")
        report.append(f"Files Moved:   {len(self.moves)}")
        report.append("")
        report.append("=" * 80)
        report.append("FILE MOVEMENTS")
        report.append("=" * 80)
        report.append("")
        
        # Group by category
        by_category = {}
        for move in self.moves:
            cat = move['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(move)
        
        for category, moves in sorted(by_category.items()):
            report.append(f"📁 CATEGORY: {category}")
            report.append(f"   Files: {len(moves)}")
            report.append("")
            
            for i, move in enumerate(moves, 1):
                report.append(f"   {i}. {move['filename']}")
                report.append(f"      From: {move['original_path']}")
                report.append(f"      To:   {move['destination_path']}")
                report.append(f"      Confidence: {move['confidence']:.1%}")
                if move['summary']:
                    summary_short = move['summary'][:100] + "..." if len(move['summary']) > 100 else move['summary']
                    report.append(f"      Summary: {summary_short}")
                report.append("")
        
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self) -> str:
        """Save report to file and return path"""
        timestamp = self.session_start.strftime('%Y%m%d_%H%M%S')
        report_filename = f"move_report_{timestamp}.txt"
        report_path = MOVE_LOGS_DIR / report_filename
        
        # Generate text report
        text_report = self.generate_report()
        
        # Save text report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        # Also save JSON for machine parsing
        json_path = report_path.with_suffix('.json')
        json_data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_files": len(self.moves),
            "moves": self.moves
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Move report saved: {report_path}")
        return str(report_path)


# Global session instance
current_session = MoveSession()


def start_new_session():
    """Start a new move tracking session"""
    global current_session
    current_session = MoveSession()


def add_move(original_path: str, destination_path: str, category: str, 
            confidence: float, summary: str = ""):
    """Add a move to current session"""
    current_session.add_move(original_path, destination_path, category, confidence, summary)


def save_session_report() -> str:
    """Save current session report and start new session"""
    report_path = current_session.save_report()
    start_new_session()
    return report_path
