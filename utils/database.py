import os
import json
import secrets
import string
import threading
import time
import requests
import sqlite3
from typing import Optional, Dict, Any

DB_NAME = 'posts.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            post_code TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            full_post_data TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'uz'
        )
    ''')
    conn.commit()
    conn.close()

def generate_post_code(length=5):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def add_post_to_db(user_id: int, post_data: dict, buttons_list: list) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    post_code = generate_post_code()

    full_post_data = json.dumps({
        'post_content': post_data,
        'buttons_list': buttons_list
    })

    try:
        cursor.execute("INSERT INTO posts (post_code, user_id, full_post_data) VALUES (?, ?, ?)",
                       (post_code, user_id, full_post_data))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return add_post_to_db(user_id, post_data, buttons_list)
    finally:
        conn.close()
    return post_code

def get_post_from_db(post_code: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT full_post_data, user_id FROM posts WHERE post_code = ?", (post_code,))
    result = cursor.fetchone()
    conn.close()
    if result:
        post_data_json = result[0]
        user_id = result[1]
        full_data = json.loads(post_data_json)
        full_data['user_id'] = user_id
        return full_data
    return None

def update_post_in_db(post_code: str, post_data: dict, buttons_list: list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    full_post_data = json.dumps({
        'post_content': post_data,
        'buttons_list': buttons_list
    })
    
    cursor.execute("""
        UPDATE posts 
        SET full_post_data = ?
        WHERE post_code = ?
    """, (full_post_data, post_code))
    
    conn.commit()
    conn.close()

def set_user_language(user_id: int, language: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, language)
        VALUES (?, ?)
    ''', (user_id, language))
    conn.commit()
    conn.close()

def get_user_language(user_id: int) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'uz'

def keep_awake():
    def ping():
        while True:
            try:
                service_name = os.getenv("RENDER_SERVICE_NAME", "post-bot")
                requests.get(f"https://{service_name}.onrender.com")
            except Exception as e:
                print(f"Ping error: {str(e)}")
            time.sleep(300)
    
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()
