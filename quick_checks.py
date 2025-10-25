"""
Quick Database Checks
Fast overview of database status
"""

import sqlite3
import os


def quick_checks():
    """Quick database health check"""
    
    db_path = "data/defects.db"
    
    print("🔍 QUICK DATABASE CHECKS")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        print("   Run: python database.py")
        return
    
    print("✅ Database file exists")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count defects
        cursor.execute("SELECT COUNT(*) FROM defects")
        defect_count = cursor.fetchone()[0]
        print(f"\n📊 Total Defects: {defect_count}")
        
        # Count open
        cursor.execute("SELECT COUNT(*) FROM defects WHERE status='OPEN'")
        open_count = cursor.fetchone()[0]
        print(f"📖 Open Defects: {open_count}")
        
        # By priority
        print("\n📈 By Priority:")
        cursor.execute("SELECT priority, COUNT(*) FROM defects GROUP BY priority")
        for priority, count in cursor.fetchall():
            print(f"   {priority}: {count}")
        
        # By status
        print("\n🚦 By Status:")
        cursor.execute("SELECT status, COUNT(*) FROM defects GROUP BY status")
        for status, count in cursor.fetchall():
            print(f"   {status}: {count}")
        
        # Teams
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        print(f"\n👥 Teams: {team_count}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database is healthy!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Database may be corrupted. Try recreating it.")


if __name__ == "__main__":
    quick_checks()
