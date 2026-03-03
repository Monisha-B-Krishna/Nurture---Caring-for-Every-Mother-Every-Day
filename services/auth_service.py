import bcrypt
from database.db import get_connection


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


# -------------------------------------------------
# AUTO ASHA ASSIGNMENT (LOAD BALANCED + SAFE)
# -------------------------------------------------

def auto_assign_asha(district):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, COUNT(w.id) as woman_count
        FROM users u
        LEFT JOIN users w ON w.asha_id = u.id
        WHERE u.role = 'asha'
        AND LOWER(u.district) = LOWER(?)
        GROUP BY u.id
        ORDER BY woman_count ASC
        LIMIT 1
    """, (district,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result["id"]

    return None


# -------------------------------------------------
# CREATE USER (AUTO ASSIGN IF WOMAN)
# -------------------------------------------------

def create_user(name, username, password, role, district=None):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    role = role.lower()  # enforce lowercase

    asha_id = None

    if role == "woman" and district:
        asha_id = auto_assign_asha(district)

    cursor.execute("""
        INSERT INTO users (name, username, password, role, district, asha_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, username, hashed_pw, role, district, asha_id))

    conn.commit()
    conn.close()


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()

    if user and verify_password(password, user["password"]):
        return dict(user)

    return None