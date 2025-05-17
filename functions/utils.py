import os
import random

def get_random_cookie(cookie_dir="cookies"):
    """Ambil cookie acak dari folder cookies"""
    try:
        files = [f for f in os.listdir(cookie_dir) if f.endswith(".json")]
        if not files:
            return None
        selected_file = random.choice(files)
        with open(os.path.join(cookie_dir, selected_file), "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"[ERROR] Gagal ambil cookie: {e}")
        return None
