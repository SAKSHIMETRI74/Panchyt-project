import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users table (Citizens and Panchayat Officials)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone VARCHAR(10) UNIQUE NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'CITIZEN',
        ward_number VARCHAR(10) DEFAULT 'Ward-1',
        false_strikes INTEGER DEFAULT 0,
        is_blocked BOOLEAN DEFAULT 0,
        failed_login_attempts INTEGER DEFAULT 0,
        lockout_until TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Phone OTPs for secure verification
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phone_otps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone VARCHAR(10) NOT NULL,
        otp_hash VARCHAR(255) NOT NULL,
        attempts INTEGER DEFAULT 0,
        resend_count INTEGER DEFAULT 1,
        is_verified BOOLEAN DEFAULT 0,
        verification_token VARCHAR(64) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_otps ON phone_otps(phone, is_verified);")

    # 3. Complaints table - UNIFIED MASTER COMPLAINTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id VARCHAR(30) UNIQUE NOT NULL,
        citizen_id INTEGER NOT NULL,
        title VARCHAR(150) NOT NULL,
        category VARCHAR(50) NOT NULL,
        description TEXT NOT NULL,
        severity VARCHAR(20) DEFAULT 'Medium',
        status VARCHAR(30) DEFAULT 'Pending',
        photo_filename VARCHAR(255),
        latitude REAL,
        longitude REAL,
        location_address VARCHAR(255),
        ai_confidence REAL DEFAULT 0.0,
        ai_category VARCHAR(50),
        ai_flagged BOOLEAN DEFAULT 0,
        ai_notes TEXT,
        assigned_to VARCHAR(100),
        officer_remarks TEXT,
        is_false_complaint BOOLEAN DEFAULT 0,
        resolved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (citizen_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_id ON complaints(tracking_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaints(status, severity);")

    # 4. Comprehensive Audit Trail
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER NOT NULL,
        actor_id INTEGER NOT NULL,
        actor_role VARCHAR(30) NOT NULL,
        action VARCHAR(60) NOT NULL,
        previous_state TEXT,
        new_state TEXT,
        justification TEXT NOT NULL,
        ip_address VARCHAR(45),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
    );
    """)

    # 5. Citizen Appeals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_appeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER NOT NULL,
        citizen_id INTEGER NOT NULL,
        appeal_reason TEXT NOT NULL,
        evidence_filename VARCHAR(255),
        status VARCHAR(30) DEFAULT 'PENDING',
        reviewed_by INTEGER,
        review_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    
    # 1. Official PDO Account with Strict Department Credentials
    cursor.execute("SELECT id FROM users WHERE phone = ?", (Config.DEFAULT_ADMIN_PHONE,))
    admin = cursor.fetchone()
    if not admin:
        admin_pass_hash = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        cursor.execute("""
            INSERT INTO users (phone, full_name, password_hash, role, ward_number)
            VALUES (?, ?, ?, 'ADMIN', 'Panchayat Administrative Bhavan')
        """, (Config.DEFAULT_ADMIN_PHONE, Config.DEFAULT_ADMIN_NAME, admin_pass_hash))
    
    # 2. Primary Test Citizen Account
    sample_citizen_phone = "9845012345"
    cursor.execute("SELECT id FROM users WHERE phone = ?", (sample_citizen_phone,))
    citizen = cursor.fetchone()
    if not citizen:
        cit_pass_hash = generate_password_hash("Citizen@123")
        cursor.execute("""
            INSERT INTO users (phone, full_name, password_hash, role, ward_number)
            VALUES (?, 'Basavaraju Gowda (ಬಸವರಾಜು ಗೌಡ)', ?, 'CITIZEN', 'Ward-3 (North)')
        """, (sample_citizen_phone, cit_pass_hash))
        citizen_id = cursor.lastrowid
    else:
        citizen_id = citizen["id"]

    # 3. UNIFIED COMPLAINTS: Match exactly what Citizen and Official see
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]

    if count < 6:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        year = datetime.now().year
        
        unified_complaints = [
            # RESOLVED (4 items)
            (
                f"GP-{year}-1001", citizen_id, "Broken drinking water distribution pipe",
                "Drinking Water", "Continuous water leakage at the Ward-3 main valve near Anjaneya temple.",
                "Critical", "Resolved", 12.9716, 77.5946, "Main Road, Ward-3",
                0.95, "Drinking Water Infrastructure", 0, "Verified genuine defect evidence.",
                "Ramesh (Panchayat Plumber)", "Replaced PVC junction section. Water pressure normalized.", now_str
            ),
            (
                f"GP-{year}-1002", citizen_id, "Burnt streetlights near Government School",
                "Streetlights", "Three streetlights off on school lane causing safety issues for students.",
                "Medium", "Resolved", 12.9780, 77.5900, "School Road, Ward-3",
                0.92, "Electrical Infrastructure", 0, "Photo confirms 45W fixture defect.",
                "Anand (Gram Electrician)", "Replaced fused LED fixture and junction breaker.", now_str
            ),
            (
                f"GP-{year}-1003", citizen_id, "Choked stormwater culvert causing rain flooding",
                "Sanitation & Drainage", "Solid debris choked the culvert channel near the dairy cooperative.",
                "High", "Resolved", 12.9650, 77.6010, "Cross-4 Road, Ward-3",
                0.93, "Drainage Infrastructure", 0, "Confirmed blocked culvert channel.",
                "Suresh Sanitation Team", "JCB cleared culvert channel. Rainwater flow restored.", now_str
            ),
            (
                f"GP-{year}-1004", citizen_id, "Handpump borewell handle detachment",
                "Drinking Water", "Borewell handle broken near community hall. 35 families affected.",
                "High", "Resolved", 12.9700, 77.5980, "Community Hall, Ward-3",
                0.96, "Water Infrastructure", 0, "Visual confirmation of broken iron linkage.",
                "Ramesh Plumber", "Replaced iron linkage rod and greased pivot.", now_str
            ),

            # IN PROGRESS / RESOLVING WORK (3 items)
            (
                f"GP-{year}-1005", citizen_id, "Road pothole patch work near Market Cross",
                "Village Roads", "Deep road trench after monsoon rain making two-wheelers skid.",
                "High", "In Progress", 12.9740, 77.5920, "Market Road, Ward-2",
                0.94, "Road Infrastructure", 0, "Clear visual of asphalt erosion.",
                "Mahesh (Civil Works Contractor)", "Gravel foundation laid. Bitumen tar leveling in progress today.", None
            ),
            (
                f"GP-{year}-1006", citizen_id, "Open drainage slab broken near bus stop",
                "Sanitation & Drainage", "Reinforced cement slab broken, danger of pedestrians falling.",
                "Critical", "In Progress", 12.9760, 77.5950, "Main Bus Stop, Ward-1",
                0.95, "Drainage Infrastructure", 0, "Confirmed broken concrete cover slab.",
                "Kiran (Engineering Team)", "New precast RCC slab delivered. Crew installing reinforcement.", None
            ),
            (
                f"GP-{year}-1007", citizen_id, "Electric wire sparking near transformer",
                "Streetlights", "Overhead cable touching tree branch sparking during wind.",
                "Critical", "In Progress", 12.9690, 77.5910, "Post Office Road, Ward-2",
                0.97, "Electrical Grid", 0, "Verified tree branch proximity to phase line.",
                "BESCOM / Gram Lineman", "Tree trimming team dispatched. Line isolation underway.", None
            ),

            # PENDING REVIEW (2 items)
            (
                f"GP-{year}-1008", citizen_id, "Solid waste accumulation near weekly market ground",
                "Sanitation & Drainage", "Debris not cleared after Saturday market causing foul smell.",
                "Medium", "Pending", 12.9730, 77.5990, "Weekly Market Ground, Ward-1",
                0.91, "Sanitation", 0, "Garbage accumulation photo confirmed.",
                None, None, None
            ),
            (
                f"GP-{year}-1009", citizen_id, "New streetlight request at East Village dead-end",
                "Streetlights", "Dead-end lane has no light post, total darkness at night.",
                "Low", "Pending", 12.9810, 77.5890, "East Village Lane 4",
                0.89, "Lighting Request", 0, "Lane alignment verified.",
                None, None, None
            )
        ]
        
        for c in unified_complaints:
            cursor.execute("""
                INSERT OR IGNORE INTO complaints (
                    tracking_id, citizen_id, title, category, description,
                    severity, status, latitude, longitude, location_address,
                    ai_confidence, ai_category, ai_flagged, ai_notes,
                    assigned_to, officer_remarks, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, c)
            complaint_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO complaint_audit_logs (
                    complaint_id, actor_id, actor_role, action,
                    previous_state, new_state, justification, ip_address
                ) VALUES (?, ?, 'SYSTEM', 'INITIAL_RECORD', 'None', ?, 'Official grievance record', '127.0.0.1')
            """, (complaint_id, citizen_id, c[6]))

    conn.commit()
