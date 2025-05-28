import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
import time

st.set_page_config(page_title="Keyword Trend Checker", layout="wide")
st.title("📈 Keyword Trend Checker")

@st.cache_data(ttl=3600)
def get_trend_data(keywords, geo, timeframe, max_retries=3, delay=2):
    """
    Ambil data Google Trends dengan retry otomatis dan penanganan error.
    """
    pytrends = TrendReq(hl='id-ID', tz=360, retries=max_retries, backoff_factor=delay)
    tries = 0
    while tries < max_retries:
        try:
            pytrends.build_payload(keywords, geo=geo, timeframe=timeframe)
            data = pytrends.interest_over_time()
            related = pytrends.related_queries()
            return data, related
        except Exception as e:
            tries += 1
            if tries >= max_retries:
                raise e
            time.sleep(delay)  # tunggu sebelum coba ulang

with st.form("trend_form"):
    keywords_input = st.text_input("Masukkan kata kunci (pisahkan dengan koma, maksimal 5)", "kaos polos, kaos lengan panjang")
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

if submitted:
    keyword_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if len(keyword_list) == 0:
        st.warning("Masukkan minimal satu kata kunci.")
    elif len(keyword_list) > 5:
        st.warning("Maksimal 5 kata kunci per pencarian.")
    else:
        st.success(f"Menampilkan tren untuk: {', '.join(keyword_list)}")
        try:
            data, related_queries = get_trend_data(keyword_list, geo[1], time_range)
            if data.empty:
                st.error("Tidak ada data tren yang ditemukan untuk kata kunci tersebut.")
            else:
                data = data.drop(columns=["isPartial"], errors="ignore")

                st.subheader("📊 Grafik Tren Pencarian")
                fig, ax = plt.subplots()
                data.plot(ax=ax)
                plt.ylabel("Popularitas (%)")
                plt.xlabel("Tanggal")
                plt.legend(loc='upper left')
                st.pyplot(fig)

                st.subheader(f"🔎 Related Queries untuk: {keyword_list[0]}")
                related = related_queries.get(keyword_list[0], {}).get("top")
                if related is not None and not related.empty:
                    st.table(related.head(10))
                else:
                    st.write("Tidak ada related queries ditemukan.")
        except Exception as e:
            st.error(f"Gagal mengambil data Google Trends: {e}")

st.markdown("---")
st.markdown("📊 Data dari Google Trends | Dibuat dengan ❤️ oleh Kamu")
