import psycopg2
import os
from datetime import datetime
from app.utils.logger import log
import json
import bcrypt
import secrets

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "sensor_data"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "password"),
        port=os.getenv("DB_PORT", 5432)
    )

def initialize_schema():
    """
    Initializes the database schema by executing schema.sql once at startup.
    Executes each statement individually to support TimescaleDB commands.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        for statement in schema_sql.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    cur.execute(stmt)
                except Exception as stmt_err:
                    log(f"[DB] ❌ Error executing: {stmt[:50]}... → {stmt_err}", level="ERROR")
                    conn.rollback()  # ← Rollback on failure but continue
        conn.commit()
        cur.close()
        conn.close()
        log("[DB] ✅ Schema initialized.")

    except Exception as e:
        log(f"[DB] Failed to initialize schema: {e}", level="ERROR")


async def insert_sample_data(client_id, channel_id, raw_signal, filtered_signal, features, classification):
    """
    Inserts one row into the 'proben' table, including raw and filtered signals.
    """
    try:
        conn = get_connection()
        cur = conn.cursor() 

        cur.execute("""
            INSERT INTO proben (client_id, channel_id, timestamp, grw, ff, varianz, klasse, raw_signal, filtered_signal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            client_id,
            channel_id,
            datetime.utcnow(),
            features["GRW"],
            features["FF"],
            features["Var"],
            classification,
            json.dumps(raw_signal),
            json.dumps(filtered_signal)
        ))

        conn.commit()
        cur.close()
        conn.close()

        log(f"[DB] Inserted sample for client {client_id}, class {classification}")

    except Exception as e:
        log(f"[DB] Failed to insert data: {e}", level="ERROR")

def create_user(username, password, email=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s OR (email = %s AND email IS NOT NULL)", (username, email))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "Username or email already exists"
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password_hash))
        conn.commit()
        cur.close()
        conn.close()
        return True, "User created successfully"
    except Exception as e:
        log(f"[DB] Failed to create user: {e}", level="ERROR")
        return False, str(e)

def authenticate_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            user_id, password_hash = row
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                return user_id
        return None
    except Exception as e:
        log(f"[DB] Failed to authenticate user: {e}", level="ERROR")
        return None

def generate_reset_token(username):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return None
        reset_token = secrets.token_urlsafe(32)
        cur.execute("UPDATE users SET reset_token = %s WHERE username = %s", (reset_token, username))
        conn.commit()
        cur.close()
        conn.close()
        return reset_token
    except Exception as e:
        log(f"[DB] Failed to generate reset token: {e}", level="ERROR")
        return None

def fetch_latest_samples(limit=100):
    """
    Fetch the latest N samples from the 'proben' table.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT client_id, channel_id, timestamp, grw, ff, varianz, klasse, raw_signal, filtered_signal
            FROM proben
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            for key in ["raw_signal", "filtered_signal"]:
                if row_dict.get(key):
                    try:
                        row_dict[key] = json.loads(row_dict[key])
                    except Exception:
                        row_dict[key] = []
                else:
                    row_dict[key] = []
            results.append(row_dict)
        cur.close()
        conn.close()
        return results
    except Exception as e:
        log(f"[DB] Failed to fetch samples: {e}", level="ERROR")
        return []
