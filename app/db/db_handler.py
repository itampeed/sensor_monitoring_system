import psycopg2
import os
from datetime import datetime
from app.utils.logger import log
import json
import bcrypt
import secrets # or your actual DB session

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "sensor_data"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "bilal"),
        port=os.getenv("DB_PORT", 5432)
    )

# Example async DB call to fetch channels for a client
def get_channels_for_client(client_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM kanal WHERE client_id = %s", (client_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]  # Only return channel names
    except Exception as e:
        log(f"[DB] Failed to fetch channels for client {client_id}: {e}", level="ERROR")
        return []

def initialize_schema():
    try:
        conn = get_connection()
        cur = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cur.execute(schema_sql)  # run whole schema at once
        conn.commit()
        cur.close()
        conn.close()
        log("[DB] ✅ Schema initialized.")
    except Exception as e:
        log(f"[DB] ❌ Failed to initialize schema: {e}", level="ERROR")


async def insert_sample_data(client_id, channel_id, raw_signal, filtered_signal, features_dict, classification):
    """
    Inserts one row into the 'proben' table, including all 9 features and signals.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO proben (
                client_id, channel_id, timestamp,
                sigstat_mw, statsig_qmw, stat_stdaw, stat_var,
                stat_wb, stat_n6m, sig_qwm, sig_grw, sig_ff,
                klasse, raw_signal, filtered_signal
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """, (
            client_id,
            channel_id,
            datetime.utcnow(),
            float(features_dict["I-L1_SigStat-MW"]),
            float(features_dict["I-L1_StatSig-qMW"]),
            float(features_dict["I-L1_Stat-StdAW"]),
            float(features_dict["I-L1_Stat-Var"]),
            float(features_dict["I-L1_Stat-Wb"]),
            float(features_dict["I-L1_Stat-N6M"]),
            float(features_dict["I-L1_Sig-QWM"]),
            float(features_dict["I-L1_Sig-GRW"]),
            float(features_dict["I-L1_Sig-FF"]),
            int(classification),
            json.dumps(raw_signal),
            json.dumps(filtered_signal)
        ))

        conn.commit()
        cur.close()
        conn.close()

        log(f"[DB] ✅ Inserted sample for client {client_id}, class {classification}")

    except Exception as e:
        log(f"[DB] ❌ Failed to insert data: {e}", level="ERROR")


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

def fetch_latest_samples(limit=200):
    """
    Fetch the latest N samples from the 'proben' table, including all 9 features.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                client_id, channel_id, timestamp,
                sigstat_mw, statsig_qmw, stat_stdaw, stat_var,
                stat_wb, stat_n6m, sig_qwm, sig_grw, sig_ff,
                klasse, raw_signal, filtered_signal
            FROM proben
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        results = []

        for row in rows:
            row_dict = dict(zip(columns, row))

            # Convert signal fields from JSON strings to Python objects
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
