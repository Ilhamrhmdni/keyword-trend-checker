import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

# -----------------------------
# Konfigurasi Streamlit
# -----------------------------
st.set_page_config(page_title="Keyword Trend Checker", layout="wide")
st.title("📈 Keyword Trend Checker")

# -----------------------------
# Fungsi Caching Pytrends
# -----------------------------
@st.cache_data(ttl=3600)  # cache selama 1 jam
def get_trend_data(keywords, geo, timeframe):
    pytrends = TrendReq(hl='id-ID', tz=360)
    pytrends.build_payload(keywords, geo=geo, timeframe=timeframe)
    data = pytrends.interest_over_time()
    related = pytrends.related_queries()
    return data, related

# -----------------------------
# Form Input Pengguna
# -----------------------------
with st.form("trend_form"):
    keywords_input = st.text_input("Masukkan kata kunci (pisahkan dengan koma)", "kaos polos, kaos lengan panjang")

    geo = st.selectbox("Wilayah", options=[
        ("Indonesia", "ID"),
        ("Global", ""),
        ("Amerika Serikat", "US"),
        ("Malaysia", "MY"),
        ("Singapura", "SG")
    ])

    time_range = st.selectbox("Rentang waktu", options=[
        ("7 hari terakhir", "now 7-d"),
        ("30 hari terakhir", "now 30-d"),
        ("12 bulan terakhir", "today 12-m"),
        ("5 tahun terakhir", "today+5-y")
    ])

    submitted = st.form_submit_button("🔍 Cek Tren")

# -----------------------------
# Logika Proses dan Output
# -----------------------------
if submitted:
    keyword_list = [k.strip() for k in keywords_input.split(",") if k.strip()]

    if not keyword_list:
        st.warning("Masukkan minimal satu kata kunci.")
    else:
        st.success(f"Menampilkan tren untuk: {', '.join(keyword_list)}")

        data, related_queries = get_trend_data(keyword_list, geo[1], time_range)

        if data.empty:
            st.error("Tidak ada data tren yang ditemukan untuk kata kunci tersebut.")
        else:
            # Hapus kolom isPartial jika ada
            data = data.drop(columns=["isPartial"], errors="ignore")

            # Grafik tren
            st.subheader("📊 Grafik Tren Pencarian")
            fig, ax = plt.subplots()
            data.plot(ax=ax)
            plt.ylabel("Popularitas (%)")
            plt.xlabel("Tanggal")
            plt.legend(loc='upper left')
            st.pyplot(fig)

            # Related queries
            st.subheader(f"🔎 Related Queries untuk: {keyword_list[0]}")
            related = related_queries.get(keyword_list[0], {}).get("top")
            if related is not None and not related.empty:
                st.table(related.head(10))
            else:
                st.write("Tidak ada related queries ditemukan.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("📊 Data dari Google Trends | Dibuat dengan ❤️ oleh [Nama Kamu]")
