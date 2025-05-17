import streamlit as st
from functions.auth import generate_qr, check_qr_status
from functions.actions import bot_like

st.title("📱 Shopee Livestream Bot")
st.write("Gunakan menu di bawah ini untuk menjalankan aksi")

menu = ["Generate QR", "Cek Status QR", "Kirim Like"]
choice = st.sidebar.selectbox("Pilih Aksi", menu)

if choice == "Generate QR":
    if st.button("Generate QR Code"):
        result = generate_qr()
        st.json(result)

elif choice == "Cek Status QR":
    qrcode_id = st.text_input("Masukkan ID QR")
    if st.button("Cek Status QR"):
        result = check_qr_status(qrcode_id)
        st.json(result)

elif choice == "Kirim Like":
    sessionid = st.text_input("Session ID")
    if st.button("Kirim Like"):
        result = bot_like(sessionid)
        st.json(result)
