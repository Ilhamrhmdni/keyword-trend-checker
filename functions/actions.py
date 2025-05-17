import requests
from functions.utils import get_random_cookie

headers_live = {
    "Host": "live.shopee.co.id",
    "User-Agent": "ShopeeID/3.15.24 (com.beeasy.shopee.id; build:3.15.24; iOS 16.1.1) Alamofire/5.0.5 language=id app_type=1 Cronet/102.0.5005.61",
    "X-Livestreaming-Auth": "ls_ios_v1_20001_1706619410_05731F9E-487C-47FC-8A6B-293731FDF110|HPBHsukBXAj1fu10omr0UqDWfOE65FnfQemUKWPlyM4=",
    "X-Ls-Sz-Token": "9QhPkALUJ1I7QQNoYoErEg==|7XRVuxPN20df7VqgcGssUsRESRkX/NYlNv4CcELDTndobXUJR4jWhC2JEy8d7uKMPjZb6zMKg8WYfTx5NrDS+L9b16BZMg==|M2F8y1gIdLZicwT5|08|1",
    "Client-Info": "device_id=B71CEC41A1AB42E1ABED79E26E6AD76B;device_model=iPhone%2011;os=1;os_version=16.1.1;client_version=31524;network=1;platform=2;language=id;cpu_model=ARM64E",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

def bot_like(sessionid):
    url = f"{liveURL}/api/v1/session/{sessionid}/like"
    cookie = get_random_cookie()
    payload = {"like_cnt": 20}
    try:
        response = requests.post(url, json=payload, headers={
            **headers_live,
            "Cookie": cookie
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}
