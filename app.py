import streamlit as st
from functions.auth import generate_qr, check_qr_status
from functions.actions import send_like, send_komen, get_trending_live

st.set_page_config(page_title="Shopee Livestream Bot", layout="centered")

st.title("📱 Shopee Livestream Bot")
st.write("Gunakan menu di bawah untuk memilih aksi.")

menu = ["Login via QR", "Kirim Like", "Kirim Komentar", "Lihat Trending Live"]
choice = st.sidebar.selectbox("Pilih Aksi", menu)

if choice == "Login via QR":
    st.subheader("🔐 Generate QR Code untuk Login")
    if st.button("Generate QR"):
        result = generate_qr()
        st.json(result)

    qrcode_id = st.text_input("Masukkan QR ID untuk cek status:")
    if st.button("Cek Status QR"):
        result = check_qr_status(qrcode_id)
        st.json(result)

elif choice == "Kirim Like":
    st.subheader("👍 Kirim Like ke Session Livestream")
    sessionid = st.text_input("Session ID")
    if st.button("Kirim Like"):
        result = send_like(sessionid)
        st.json(result)

elif choice == "Kirim Komentar":
    st.subheader("💬 Kirim Komentar ke Session Livestream")
    sessionid = st.text_input("Session ID")
    message = st.text_input("Isi Komentar")
    if st.button("Kirim Komentar"):
        result = send_komen(sessionid, message)
        st.json(result)

elif choice == "Lihat Trending Live":
    st.subheader("🔥 Lihat Livestream yang Sedang Trending")
    page = st.number_input("Halaman", min_value=1, value=1)
    offset = st.number_input("Offset", min_value=0, value=0)
    if st.button("Muat Data"):
        result = get_trending_live(page=page, offset=offset)
        st.json(result)
