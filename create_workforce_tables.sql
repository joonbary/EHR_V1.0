-- Weekly Workforce Snapshot Table
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
    FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id),
    UNIQUE(snapshot_date, company, job_group, grade, position, contract_type)
);

-- Weekly Join/Leave Table
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
);

-- Weekly Workforce Change Table
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
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_date ON weekly_workforce_snapshot(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_company ON weekly_workforce_snapshot(company);
CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_job_group ON weekly_workforce_snapshot(job_group);
CREATE INDEX IF NOT EXISTS idx_workforce_snapshot_contract_type ON weekly_workforce_snapshot(contract_type);

CREATE INDEX IF NOT EXISTS idx_join_leave_date ON weekly_join_leave(date);
CREATE INDEX IF NOT EXISTS idx_join_leave_type ON weekly_join_leave(type);
CREATE INDEX IF NOT EXISTS idx_join_leave_company ON weekly_join_leave(company);

CREATE INDEX IF NOT EXISTS idx_workforce_change_current_date ON weekly_workforce_change(current_date);
CREATE INDEX IF NOT EXISTS idx_workforce_change_base_type ON weekly_workforce_change(base_type);
CREATE INDEX IF NOT EXISTS idx_workforce_change_company ON weekly_workforce_change(company);