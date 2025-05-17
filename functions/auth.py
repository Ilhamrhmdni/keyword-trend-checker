# auth.py

import requests
from urllib.parse import unquote

# Base URLs
WEB_URL = "https://shopee.co.id "
LIVE_URL = "https://live.shopee.co.id "

# Headers untuk autentikasi
HEADERS_WEB = {
    "authority": "shopee.co.id",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "client-info": "platform=9",
    "X-Shopee-Language": "id",
    "X-Requested-With": "XMLHttpRequest"
}

def generate_qr():
    """
    Generate QR Code untuk login ke Shopee
    """
    url = f"{WEB_URL}/api/v2/authentication/gen_qrcode"
    try:
        response = requests.get(url, headers=HEADERS_WEB)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_qr_status(qrcode_id):
    """
    Cek status QR Code apakah sudah discan atau belum
    """
    url = f"{WEB_URL}/api/v2/authentication/qrcode_status?qrcode_id={qrcode_id}"
    try:
        response = requests.get(url, headers=HEADERS_WEB)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
