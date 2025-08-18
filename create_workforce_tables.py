"""
Workforce 테이블 생성 스크립트
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Weekly Workforce Snapshot Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_workforce_snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date DATE NOT NULL,
            company VARCHAR(100) NOT NULL,
            job_group VARCHAR(50) NOT NULL,
            grade VARCHAR(50) NOT NULL,
            position VARCHAR(50),
            contract_type VARCHAR(50) NOT NULL,
            headcount INTEGER NOT NULL,
            uploaded_at DATETIME NOT NULL,
            uploaded_by_id INTEGER,
            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id)
        )
    ''')
    
    # Unique constraint
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_workforce_snapshot_unique 
        ON weekly_workforce_snapshot(snapshot_date, company, job_group, grade, position, contract_type)
    ''')
    
    # Weekly Join/Leave Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_join_leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(20) NOT NULL,
            name VARCHAR(100) NOT NULL,
            company VARCHAR(100) NOT NULL,
            org_unit VARCHAR(100) NOT NULL,
            grade VARCHAR(50) NOT NULL,
            position VARCHAR(50),
            job_group VARCHAR(50),
            date DATE NOT NULL,
            reason TEXT,
            uploaded_at DATETIME NOT NULL,
            uploaded_by_id INTEGER,
            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id)
        )
    ''')
    
    # Weekly Workforce Change Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_workforce_change (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_date DATE NOT NULL,
            base_date DATE NOT NULL,
            base_type VARCHAR(20) NOT NULL,
            company VARCHAR(100) NOT NULL,
            job_group VARCHAR(50) NOT NULL,
            grade VARCHAR(50) NOT NULL,
            position VARCHAR(50),
            contract_type VARCHAR(50) NOT NULL,
            current_headcount INTEGER NOT NULL,
            base_headcount INTEGER NOT NULL,
            created_at DATETIME NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_date ON weekly_workforce_snapshot(snapshot_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_company ON weekly_workforce_snapshot(company)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_job_group ON weekly_workforce_snapshot(job_group)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_join_leave_date ON weekly_join_leave(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_join_leave_type ON weekly_join_leave(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_join_leave_company ON weekly_join_leave(company)')
    
    # current_date is SQLite function, so skip this index
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workforce_change_base_type ON weekly_workforce_change(base_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workforce_change_company ON weekly_workforce_change(company)')
    
    conn.commit()
    print("Tables created successfully!")
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'weekly_%'")
    tables = cursor.fetchall()
    print("\nCreated tables:")
    for table in tables:
        print(f"  - {table[0]}")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()