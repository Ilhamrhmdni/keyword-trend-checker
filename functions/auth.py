const got = require("got");

// --- Base URLs ---
const webURL = "https://shopee.co.id ";
const liveURL = "https://live.shopee.co.id ";

// --- Headers ---
const header_web = {
  authority: "shopee.co.id",
  accept: "application/json, text/plain, */*",
  "accept-language": "en-US,en;q=0.9,id;q=0.8",
  "Content-Type": "application/json",
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0 Safari/537.36",
  "client-info": "platform=9",
  "X-Shopee-Language": "id",
  "X-Requested-With": "XMLHttpRequest"
};

/**
 * Generate QR Code untuk login
 */
async function generateQR() {
  const url = `${webURL}/api/v2/authentication/gen_qrcode`;
  try {
    const response = await got.get(url, { headers: header_web });
    return JSON.parse(response.body);
  } catch (error) {
    console.error("[generateQR] Error:", error.message);
    return { error: error.message };
  }
}

/**
 * Cek status QR Code
 * @param {string} qrcode_id - ID QR Code
 */
async function checkQRStatus(qrcode_id) {
  const url = `${webURL}/api/v2/authentication/qrcode_status?qrcode_id=${encodeURIComponent(qrcode_id)}`;
  try {
    const response = await got.get(url, { headers: header_web });
    return JSON.parse(response.body);
  } catch (error) {
    console.error("[checkQRStatus] Error:", error.message);
    return { error: error.message };
  }
}

module.exports = {
  generateQR,
  checkQRStatus
};
