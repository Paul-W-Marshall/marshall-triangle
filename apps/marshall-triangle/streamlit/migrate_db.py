import sqlite3
import json

def migrate_db():
    """Migrate data from environments and harmony_states tables to marshall_states table"""
    try:
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()
        
        # Create marshall_states table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS marshall_states (
            name TEXT PRIMARY KEY,
            icon_params TEXT,
            r_target REAL,
            g_target REAL,
            b_target REAL
        )
        ''')
        
        # Check if environments table exists and migrate data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='environments'")
        if cursor.fetchone():
            cursor.execute("SELECT name, icon_params, r_target, g_target, b_target FROM environments")
            environments = cursor.fetchall()
            
            # Insert each record into marshall_states table
            for env in environments:
                name, icon_params, r, g, b = env
                
                # Check if record already exists in marshall_states
                cursor.execute("SELECT COUNT(*) FROM marshall_states WHERE name = ?", (name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO marshall_states (name, icon_params, r_target, g_target, b_target) VALUES (?, ?, ?, ?, ?)",
                        (name, icon_params, r, g, b)
                    )
            
            print(f"Successfully migrated {len(environments)} records from environments to marshall_states")
        
        # Check if harmony_states table exists and migrate data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='harmony_states'")
        if cursor.fetchone():
            cursor.execute("SELECT name, icon_params, r_target, g_target, b_target FROM harmony_states")
            harmony_states = cursor.fetchall()
            
            # Insert each record into marshall_states table
            for state in harmony_states:
                name, icon_params, r, g, b = state
                
                # Check if record already exists in marshall_states
                cursor.execute("SELECT COUNT(*) FROM marshall_states WHERE name = ?", (name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO marshall_states (name, icon_params, r_target, g_target, b_target) VALUES (?, ?, ?, ?, ?)",
                        (name, icon_params, r, g, b)
                    )
            
            print(f"Successfully migrated {len(harmony_states)} records from harmony_states to marshall_states")
        
        # Commit the changes
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    migrate_db()