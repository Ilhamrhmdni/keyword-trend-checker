import requests
from functions.utils import get_random_cookie

live_url = "https://live.shopee.co.id "

# --- Headers standar livestreaming ---
headers_live = {
    "Host": "live.shopee.co.id",
    "Client-Request-Id": "5e178189-14ab-4e9f-9e0d-15270821e8dd.369",
    "User-Agent": "ShopeeID/3.15.24 (com.beeasy.shopee.id; build:3.15.24; iOS 16.1.1) Alamofire/5.0.5 language=id app_type=1 Cronet/102.0.5005.61",
    "X-Livestreaming-Auth": "ls_ios_v1_20001_1706619410_05731F9E-487C-47FC-8A6B-293731FDF110|HPBHsukBXAj1fu10omr0UqDWfOE65FnfQemUKWPlyM4=",
    "X-Ls-Sz-Token": "9QhPkALUJ1I7QQNoYoErEg==|7XRVuxPN20df7VqgcGssUsRESRkX/NYlNv4CcELDTndobXUJR4jWhC2JEy8d7uKMPjZb6zMKg8WYfTx5NrDS+L9b16BZMg==|M2F8y1gIdLZicwT5|08|1",
    "X-Livestreaming-Source": "shopee",
    "Client-Info": "device_id=B71CEC41A1AB42E1ABED79E26E6AD76B;device_model=iPhone%2011;os=1;os_version=16.1.1;client_version=31524;network=1;platform=2;language=id;cpu_model=ARM64E",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

def send_like(sessionid):
    """Kirim like ke session live"""
    url = f"{live_url}/api/v1/session/{sessionid}/like"
    cookie = get_random_cookie()
    headers = {**headers_live, "Cookie": cookie}
    payload = {"like_cnt": 20}
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def send_komen(sessionid, message):
    """Kirim komentar ke session live"""
    url = f"{live_url}/api/v1/session/{sessionid}/message"
    cookie = get_random_cookie()
    headers = {**headers_live, "Cookie": cookie}
    payload = {
        "content": '{"content":"' + message + '","type":100}',
        "usersig": "",
        "uuid": "AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns="
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_trending_live(page=1, offset=0):
    """Dapatkan livestream yang sedang trending"""
    url = f"{live_url}/api/v1/topscroll"
    params = {
        "offset": offset,
        "limit": 20,
        "device_id": "AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns=",
        "ctx_id": f"AiMSLbAvYy1d2pTViKSdeW1Ld64f5HIwOW4ylNbzxns=-{int(time.time())}-808594",
        "page_no": page
    }
    cookie = get_random_cookie()
    headers = {**headers_live, "Cookie": cookie}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
