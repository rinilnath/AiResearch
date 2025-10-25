"""
Database Layer for Defect Management System
Handles all database operations using SQLite
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import json


class DefectDatabase:
    """
    Database manager for defect tracking system
    """
    
    def __init__(self, db_path: str = "data/defects.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Defects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                raw_input TEXT NOT NULL,
                equipment TEXT,
                location TEXT,
                issue TEXT,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                priority_reasoning TEXT,
                recommended_actions TEXT,
                assigned_team TEXT NOT NULL,
                estimated_resolution_time TEXT,
                status TEXT DEFAULT 'OPEN',
                resolution_notes TEXT,
                resolved_at TEXT,
                resolved_by TEXT,
                actual_resolution_time_hours REAL
            )
        """)
        
        # Teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE NOT NULL,
                contact_email TEXT,
                contact_phone TEXT,
                specialization TEXT
            )
        """)
        
        # Defect history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS defect_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                defect_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                status_from TEXT,
                status_to TEXT,
                notes TEXT,
                changed_by TEXT,
                FOREIGN KEY (defect_id) REFERENCES defects (id)
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                defect_id INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                notification_type TEXT,
                message TEXT,
                sent_at TEXT,
                status TEXT DEFAULT 'PENDING',
                FOREIGN KEY (defect_id) REFERENCES defects (id)
            )
        """)
        
        conn.commit()
        
        # Load teams data if table is empty
        self._load_initial_teams()
    
    def _load_initial_teams(self):
        """Load teams from CSV if database is empty"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        
        if count == 0:
            try:
                teams_df = pd.read_csv('data/teams.csv')
                for _, row in teams_df.iterrows():
                    cursor.execute("""
                        INSERT INTO teams (team_name, contact_email, contact_phone, specialization)
                        VALUES (?, ?, ?, ?)
                    """, (row['team_name'], row['contact_email'], row['contact_phone'], row['specialization']))
                conn.commit()
            except FileNotFoundError:
                # Create default teams
                default_teams = [
                    ('Maintenance', 'maintenance@plant.com', '+1-555-0101', 'Mechanical repairs'),
                    ('Quality Control', 'qc@plant.com', '+1-555-0102', 'Quality assurance'),
                    ('Safety', 'safety@plant.com', '+1-555-0103', 'Safety systems'),
                    ('Engineering', 'engineering@plant.com', '+1-555-0104', 'Technical design'),
                    ('Production', 'production@plant.com', '+1-555-0105', 'Production operations')
                ]
                for team in default_teams:
                    cursor.execute("""
                        INSERT INTO teams (team_name, contact_email, contact_phone, specialization)
                        VALUES (?, ?, ?, ?)
                    """, team)
                conn.commit()
    
    def create_defect(self, ai_result: Dict) -> str:
        """
        Create a new defect entry from AI analysis result
        Returns: ticket_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate ticket ID
        timestamp = datetime.now()
        ticket_id = self._generate_ticket_id(ai_result.get('category', 'DEF'), timestamp)
        
        # Extract data from AI result
        extracted_info = ai_result.get('extracted_info', {})
        
        # Insert defect
        cursor.execute("""
            INSERT INTO defects (
                ticket_id, timestamp, raw_input, equipment, location, issue,
                category, priority, priority_reasoning, recommended_actions,
                assigned_team, estimated_resolution_time, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            ai_result.get('timestamp', timestamp.isoformat()),
            ai_result.get('raw_input', ''),
            extracted_info.get('equipment', 'Unknown'),
            extracted_info.get('location', 'Unknown'),
            extracted_info.get('issue', '')[:200],
            ai_result.get('category', 'Unknown'),
            ai_result.get('priority', 'MEDIUM'),
            ai_result.get('priority_reasoning', ''),
            json.dumps(ai_result.get('recommended_actions', [])),
            ai_result.get('assigned_team', 'Engineering'),
            ai_result.get('estimated_resolution_time', 'Unknown'),
            'OPEN'
        ))
        
        defect_id = cursor.lastrowid
        conn.commit()
        
        # Create initial history entry
        self._add_history_entry(defect_id, None, 'OPEN', 'Defect reported and categorized by AI')
        
        # Create notification
        self._create_notification(defect_id, ai_result.get('assigned_team', 'Engineering'), 
                                 'NEW_DEFECT', f"New {ai_result.get('priority')} priority defect: {ticket_id}")
        
        return ticket_id
    
    def _generate_ticket_id(self, category: str, timestamp: datetime) -> str:
        """Generate unique ticket ID - FIXED VERSION"""
        category_code = {
            'Mechanical': 'MECH',
            'Electrical': 'ELEC',
            'Quality Control': 'QC',
            'Safety': 'SAFE',
            'Process': 'PROC'
        }.get(category, 'DEF')
        
        date_str = timestamp.strftime('%Y%m%d')
        
        # Find the highest number for this category-date combo
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ticket_id FROM defects 
            WHERE ticket_id LIKE ?
            ORDER BY ticket_id DESC
            LIMIT 1
        """, (f"{category_code}-{date_str}-%",))
        
        result = cursor.fetchone()
        
        if result:
            # Extract the number from the last ticket
            last_ticket = result[0]
            try:
                last_num = int(last_ticket.split('-')[-1])
                count = last_num + 1
            except:
                count = 1
        else:
            count = 1
        
        return f"{category_code}-{date_str}-{count:03d}"
    
    def _add_history_entry(self, defect_id: int, status_from: Optional[str], 
                          status_to: str, notes: str, changed_by: str = "System"):
        """Add history entry for status change"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO defect_history (defect_id, timestamp, status_from, status_to, notes, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (defect_id, datetime.now().isoformat(), status_from, status_to, notes, changed_by))
        
        conn.commit()
    
    def _create_notification(self, defect_id: int, team_name: str, 
                           notification_type: str, message: str):
        """Create notification for team"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (defect_id, team_name, notification_type, message, sent_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (defect_id, team_name, notification_type, message, datetime.now().isoformat(), 'SENT'))
        
        conn.commit()
    
    def update_defect_status(self, ticket_id: str, new_status: str, 
                            notes: str = "", changed_by: str = "User") -> bool:
        """Update defect status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current status and defect_id
        cursor.execute("SELECT id, status FROM defects WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        defect_id, old_status = row
        
        # Update status
        update_fields = ["status = ?"]
        params = [new_status]
        
        if new_status == 'RESOLVED':
            update_fields.append("resolved_at = ?")
            update_fields.append("resolved_by = ?")
            params.extend([datetime.now().isoformat(), changed_by])
        
        if notes:
            update_fields.append("resolution_notes = ?")
            params.append(notes)
        
        params.append(ticket_id)
        
        cursor.execute(f"""
            UPDATE defects 
            SET {', '.join(update_fields)}
            WHERE ticket_id = ?
        """, params)
        
        conn.commit()
        
        # Add history
        self._add_history_entry(defect_id, old_status, new_status, notes, changed_by)
        
        # Create notification
        self._create_notification(defect_id, '', 'STATUS_UPDATE', 
                                f"Status changed from {old_status} to {new_status}")
        
        return True
    
    def get_all_defects(self) -> pd.DataFrame:
        """Get all defects as DataFrame"""
        conn = self.get_connection()
        query = "SELECT * FROM defects ORDER BY timestamp DESC"
        return pd.read_sql_query(query, conn)
    
    def get_defects_by_status(self, status: str) -> pd.DataFrame:
        """Get defects filtered by status"""
        conn = self.get_connection()
        query = "SELECT * FROM defects WHERE status = ? ORDER BY timestamp DESC"
        return pd.read_sql_query(query, conn, params=(status,))
    
    def get_defects_by_priority(self, priority: str) -> pd.DataFrame:
        """Get defects filtered by priority"""
        conn = self.get_connection()
        query = "SELECT * FROM defects WHERE priority = ? ORDER BY timestamp DESC"
        return pd.read_sql_query(query, conn, params=(priority,))
    
    def get_defect_by_ticket_id(self, ticket_id: str) -> Optional[Dict]:
        """Get single defect by ticket ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM defects WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total defects
        cursor.execute("SELECT COUNT(*) FROM defects")
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute("SELECT status, COUNT(*) FROM defects GROUP BY status")
        by_status = dict(cursor.fetchall())
        
        # By priority
        cursor.execute("SELECT priority, COUNT(*) FROM defects GROUP BY priority")
        by_priority = dict(cursor.fetchall())
        
        # By category
        cursor.execute("SELECT category, COUNT(*) FROM defects GROUP BY category")
        by_category = dict(cursor.fetchall())
        
        # By team
        cursor.execute("SELECT assigned_team, COUNT(*) FROM defects GROUP BY assigned_team")
        by_team = dict(cursor.fetchall())
        
        # Recent defects (last 7 days)
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM defects 
            WHERE DATE(timestamp) >= DATE('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        recent_trend = cursor.fetchall()
        
        return {
            'total_defects': total,
            'by_status': by_status,
            'by_priority': by_priority,
            'by_category': by_category,
            'by_team': by_team,
            'recent_trend': recent_trend,
            'open_count': by_status.get('OPEN', 0),
            'in_progress_count': by_status.get('IN_PROGRESS', 0),
            'resolved_count': by_status.get('RESOLVED', 0),
            'critical_count': by_priority.get('CRITICAL', 0),
            'high_count': by_priority.get('HIGH', 0)
        }
    
    def get_historical_defects(self) -> pd.DataFrame:
        """Load historical defects from CSV for AI training"""
        try:
            return pd.read_csv('data/historical_defects.csv')
        except FileNotFoundError:
            return pd.DataFrame()
    
    def get_teams(self) -> pd.DataFrame:
        """Get all teams"""
        conn = self.get_connection()
        return pd.read_sql_query("SELECT * FROM teams", conn)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Test function
def test_database():
    """Test database operations"""
    db = DefectDatabase()
    
    # Test AI result structure
    test_ai_result = {
        'timestamp': datetime.now().isoformat(),
        'raw_input': 'Test defect report',
        'extracted_info': {
            'equipment': 'Test Press',
            'location': 'Line 1',
            'issue': 'Test issue'
        },
        'category': 'Mechanical',
        'priority': 'HIGH',
        'priority_reasoning': 'Test reasoning',
        'recommended_actions': ['Action 1', 'Action 2'],
        'assigned_team': 'Maintenance',
        'estimated_resolution_time': '2 hours'
    }
    
    # Create defect
    ticket_id = db.create_defect(test_ai_result)
    print(f"Created defect: {ticket_id}")
    
    # Get summary
    stats = db.get_summary_stats()
    print(f"\nSummary Stats:")
    print(f"Total Defects: {stats['total_defects']}")
    print(f"By Priority: {stats['by_priority']}")
    
    return db


if __name__ == "__main__":
    # Run test
    test_database()
