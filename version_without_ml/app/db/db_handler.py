import psycopg2
import os
from datetime import datetime, timedelta
from app.utils.logger import log
import json
import bcrypt
import secrets

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "sensor_data"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "bilal"),
        port=os.getenv("DB_PORT", 5432)
    )

def get_kanal_id_by_name(channel_name):
    """Get kanal ID by channel name"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM kanal WHERE name = %s", (channel_name,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        log(f"[DB] Failed to get kanal ID for {channel_name}: {e}", level="ERROR")
        return None

def get_channels_for_client(client_id):
    """Get all channels available (for now, return all channels)"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM kanal")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        log(f"[DB] Failed to fetch channels: {e}", level="ERROR")
        return []

def initialize_schema():
    try:
        conn = get_connection()
        cur = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cur.execute(schema_sql)
        conn.commit()
        cur.close()
        conn.close()
        log("[DB] ✅ Schema initialized.")
    except Exception as e:
        log(f"[DB] ❌ Failed to initialize schema: {e}", level="ERROR")

async def insert_sample_data(client_id, channel_id, raw_signal, filtered_signal, features_dict, classification):
    """
    Insert data according to the new ER diagram structure:
    1. Insert raw data points into datenpunkt table
    2. Insert extracted features into merkmale table  
    3. Insert classification result into proben table
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Get kanal_id for the channel
        kanal_id = get_kanal_id_by_name(channel_id)
        if not kanal_id:
            log(f"[DB] Channel {channel_id} not found, creating it", level="WARNING")
            # Create channel if it doesn't exist (assign to first messplattform)
            cur.execute("""
                INSERT INTO kanal (name, einheit, messplattform_id) 
                VALUES (%s, %s, 1) RETURNING id
            """, (channel_id, 'V'))
            kanal_id = cur.fetchone()[0]
            
        # Insert each raw signal value as a separate datenpunkt
        datenpunkt_ids = []
        timestamp = datetime.utcnow()
        
        for i, value in enumerate(raw_signal):
            point_timestamp = timestamp + timedelta(milliseconds=i * 10)
            filtered_value = filtered_signal[i] if i < len(filtered_signal) else None
            cur.execute("""
                INSERT INTO datenpunkt (kanal_id, timestamp, wert, filtered_wert)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (kanal_id, point_timestamp, float(value), filtered_value))
            datenpunkt_ids.append(cur.fetchone()[0])
        
        # Use the first datenpunkt for features and classification
        if datenpunkt_ids:
            main_datenpunkt_id = datenpunkt_ids[0]
            
            # Insert features into merkmale table
            feature_names = [
                "I-L1_SigStat-MW", "I-L1_StatSig-qMW", "I-L1_Stat-StdAW", 
                "I-L1_Stat-Var", "I-L1_Stat-Wb", "I-L1_Stat-N6M",
                "I-L1_Sig-QWM", "I-L1_Sig-GRW", "I-L1_Sig-FF"
            ]
            
            for feature_name in feature_names:
                if feature_name in features_dict:
                    cur.execute("""
                        INSERT INTO merkmale (datenpunkt_id, name, wert, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (main_datenpunkt_id, feature_name, float(features_dict[feature_name]), timestamp))
            
            # Insert classification result into proben table
            cur.execute("""
                INSERT INTO proben (datenpunkt_id, klasse, timestamp)
                VALUES (%s, %s, %s)
            """, (main_datenpunkt_id, int(classification), timestamp))

        conn.commit()
        cur.close()
        conn.close()
        
        log(f"[DB] ✅ Inserted sample for client {client_id}, channel {channel_id}, class {classification}")
        
    except Exception as e:
        log(f"[DB] ❌ Failed to insert data: {e}", level="ERROR")
        raise

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
    Fetch the latest samples with their features and classifications
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                p.id as probe_id,
                p.klasse,
                p.timestamp,
                d.wert as datenpunkt_wert,
                d.filtered_wert as datenpunkt_filtered_wert,
                d.timestamp as datenpunkt_timestamp,
                k.name as kanal_name,
                m.bezeichnung as messplattform_name,
                array_agg(me.name || ':' || me.wert) as features
            FROM proben p
            JOIN datenpunkt d ON p.datenpunkt_id = d.id
            JOIN kanal k ON d.kanal_id = k.id
            JOIN messplattform m ON k.messplattform_id = m.id
            LEFT JOIN merkmale me ON me.datenpunkt_id = d.id
            GROUP BY p.id, p.klasse, p.timestamp, d.wert, d.filtered_wert, d.timestamp, k.name, m.bezeichnung
            ORDER BY p.timestamp DESC
            LIMIT %s
        """, (limit,))

        rows = cur.fetchall()
        results = []

        for row in rows:
            probe_id, klasse, timestamp, datenpunkt_wert, datenpunkt_filtered_wert, datenpunkt_timestamp, kanal_name, messplattform_name, features = row
            
            # Parse features from array
            features_dict = {}
            if features and features[0]:  # Check if features exist
                for feature_str in features:
                    if ':' in feature_str:
                        name, value = feature_str.split(':', 1)
                        try:
                            features_dict[name] = float(value)
                        except ValueError:
                            features_dict[name] = value

            results.append({
                'probe_id': probe_id,
                'klasse': klasse,
                'timestamp': timestamp,
                'datenpunkt_wert': datenpunkt_wert,
                'datenpunkt_filtered_wert': datenpunkt_filtered_wert,
                'datenpunkt_timestamp': datenpunkt_timestamp,
                'kanal_name': kanal_name,
                'messplattform_name': messplattform_name,
                'features': features_dict
            })

        cur.close()
        conn.close()
        return results

    except Exception as e:
        log(f"[DB] Failed to fetch samples: {e}", level="ERROR")
        return []
