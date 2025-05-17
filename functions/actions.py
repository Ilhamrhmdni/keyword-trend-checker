# actions.py

import requests
import os
import random

# Base URL
LIVE_URL = "https://live.shopee.co.id "

# Headers dasar untuk interaksi livestream
HEADERS_LIVE = {
    "Host": "live.shopee.co.id",
    "User-Agent": "ShopeeID/3.15.24 (com.beeasy.shopee.id; build:3.15.24; iOS 16.1.1) Alamofire/5.0.5 language=id app_type=1 Cronet/102.0.5005.61",
    "X-Livestreaming-Auth": "ls_ios_v1_20001_1706619410_05731F9E-487C-47FC-8A6B-293731FDF110|HPBHsukBXAj1fu10omr0UqDWfOE65FnfQemUKWPlyM4=",
    "X-Ls-Sz-Token": "cz05clFC1DnsL9ztxfJZ0A==|aHRVuxPN20df7VqgcGssUsRESRkX/NYlNv4CcGeLwpdrbXUJR4jWhC2JEy8d7uKMPjZb6zMKg8WYfTx5NrDS+L9b16BZMg==|M2F8y1gIdLZicwT5|08|1",
    "Client-Info": "device_id=B71CEC41A1AB42E1ABED79E26E6AD76B;device_model=iPhone%2011;os=1;os_version=16.1.1;client_version=31524;network=1;platform=2;language=id;cpu_model=ARM64E",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

def get_random_cookie():
    """
    Ambil cookie acak dari folder cookies/
    """
    session_dir = "./cookies"
    try:
        files = [f for f in os.listdir(session_dir) if f.endswith(".json")]
        if not files:
            return None
        selected_file = random.choice(files)
        with open(os.path.join(session_dir, selected_file), 'r') as f:
            data = f.read().strip()
            return data
    except Exception as e:
        print(f"[ERROR] Gagal ambil cookie: {e}")
        return None

def bot_like(sessionid):
    """
    Kirim like ke sesi livestream
    """
    url = f"{LIVE_URL}/api/v1/session/{sessionid}/like"
    cookie = get_random_cookie()
    
    payload = {
        "like_cnt": 20
    }
    
    headers = {
        **HEADERS_LIVE,
        "Cookie": cookie
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def bot_komen(sessionid, message):
    """
    Kirim komentar ke sesi livestream
    """
    url = f"{LIVE_URL}/api/v1/session/{sessionid}/message"
    cookie = get_random_cookie()

    payload = {
        "content": '{"content":"' + message + '","type":100}',
        "usersig": "",
        "uuid": "AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns="
    }

    headers = {
        **HEADERS_LIVE,
        "Cookie": cookie,
        "Content-Type": "application/json;charset=UTF-8"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def trending_live(page=1, offset=0):
    """
    Dapatkan daftar livestream yang sedang trending
    """
    cookie = get_random_cookie()
    url = f"{LIVE_URL}/api/v1/topscroll?offset={offset}&limit=20&device_id=AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns=&ctx_id=AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns-1709900145069-808594&page_no={page}"

    headers = {
        **HEADERS_LIVE,
        "Cookie": cookie,
        "User-Agent": "okhttp/3.12.4 app_type=1 Cronet/102.0.5005.61"
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
