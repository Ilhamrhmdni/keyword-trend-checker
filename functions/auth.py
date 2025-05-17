import requests

# --- Header untuk autentikasi ---
headers_web = {
    "authority": "shopee.co.id",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "client-info": "platform=9",
    "X-Shopee-Language": "id",
    "X-Requested-With": "XMLHttpRequest"
}

live_url = "https://live.shopee.co.id "
web_url = "https://shopee.co.id "

def generate_qr():
    """Generate QR Code untuk login"""
    url = f"{web_url}/api/v2/authentication/gen_qrcode"
    try:
        response = requests.get(url, headers=headers_web)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_qr_status(qrcode_id):
    """Cek status QR Code"""
    url = f"{web_url}/api/v2/authentication/qrcode_status"
    params = {"qrcode_id": qrcode_id}
    try:
        response = requests.get(url, headers=headers_web, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
