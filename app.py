import streamlit as st
import pandas as pd
import io
import re

# === SET PAGE CONFIG ===
st.set_page_config(page_title="Filter Produk Shopee", layout="wide")

# === PANGGIL CSS ===
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)

# === PILIH OPSI ===
option = st.sidebar.selectbox("🎯 Pilih Mode Aplikasi", [
    "Filter Produk Extension Xyra", 
    "Filter Produk Shoptik"
])

# === FUNGSI UMUM ===
def read_and_validate_file(uploaded_file, delimiter='\t'):
    try:
        content = uploaded_file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content), delimiter=delimiter, on_bad_lines='skip')
        df['source_file'] = uploaded_file.name
        return df
    except Exception as e:
        st.error(f"Gagal membaca {uploaded_file.name}: {e}")
        return None

# === FUNGSI PREPROCESSING SHOPTIK ===
def preprocess_shoptik(df):
    required_cols = ['productLink', 'Peringkat', 'Penjualan (30 Hari)', 'Harga', 'Stok', 'trendPercentage']
    for col in required_cols:
        if col not in df.columns:
            st.warning(f"Kolom '{col}' tidak ditemukan dalam file.")
            df[col] = None
    # Bersihkan data
    df['trendPercentage'] = pd.to_numeric(df['trendPercentage'].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    df['Harga'] = pd.to_numeric(df['Harga'].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
    df['Penjualan (30 Hari)'] = pd.to_numeric(df['Penjualan (30 Hari)'], errors='coerce').fillna(0)
    df['Stok'] = pd.to_numeric(df['Stok'], errors='coerce').fillna(0)
    df['Peringkat'] = pd.to_numeric(
        df['Peringkat'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)', expand=False),
        errors='coerce'
    ).fillna(0)
    df['isAd'] = df['isAd'].astype(str).str.contains('True|1|Ya|Yes', case=False, na=False)
    return df

# === FUNGSI APPLY FILTER SHOPTIK ===
def apply_shoptik_filters(df, trend_percentage_min, harga_min_shoptik, penjualan_30_hari_min, stok_min_shoptik, rating_min, is_ad):
    filtered_df = df[
        (df['trendPercentage'] >= trend_percentage_min) &
        (df['Harga'] >= harga_min_shoptik) &
        (df['Penjualan (30 Hari)'] >= penjualan_30_hari_min) &
        (df['Stok'] >= stok_min_shoptik) &
        (df['Peringkat'] >= rating_min)
    ]
    if is_ad:
        filtered_df = filtered_df[filtered_df['isAd']]
    return filtered_df

# === OPSI 1: FILTER PRODUK EXTENSION XYRA ===
if option == "Filter Produk Extension Xyra":
    st.title("🛒 Filter Produk Extension Xyra")
    st.markdown("Hanya Support File Export Extensi Xyra v4.2.")
    # Input filter
    st.sidebar.title("🚬 Filter Black")
    stok_min = st.sidebar.number_input("Batas minimal stok", min_value=0, value=10,
                                       help="Produk dengan stok kurang dari nilai ini akan diabaikan")
    harga_min = st.sidebar.number_input("Batas minimal harga produk", min_value=0.0, value=0.0,
                                       help="Hanya produk di atas harga ini yang akan diproses")
     # Filter Batas minimal terjual per bulan Min & Max dalam kolom
    col1, col2 = st.sidebar.columns(2)
    with col1:
        terjual_min = st.number_input(
            "Min terjual per bulan", 
            min_value=0, 
            value=5,
            help="Produk dengan penjualan bulanan kurang dari nilai ini tidak akan diproses"
        )
    with col2:
        terjual_max = st.number_input(
            "Min terjual per bulan", 
            min_value=0, 
            value=100,
            help="Produk dengan penjualan bulanan lebih dari nilai ini tidak akan diproses"
        )
    # Filter Batas minimal komisi (%) Min & Max dalam kolom
    col1, col2 = st.sidebar.columns(2)
    with col1:
        komisi_persen_min = st.number_input(
            "Min komisi (%)", 
            min_value=0.0, 
            value=0.0,
            help="Produk dengan komisi kurang dari persentase ini tidak akan diproses"
        )
    with col2:
        komisi_persen_max = st.number_input(
            "Max komisi (%)", 
            min_value=0.0, 
            value=8.0,
            help="Produk dengan komisi lebih dari persentase ini tidak akan diproses"
        )
    # Filter Batas minimal komisi (Rp) Min & Max dalam kolom
    col1, col2 = st.sidebar.columns(2)
    with col1:
        komisi_rp_min = st.number_input(
            "Min komisi (Rp)", 
            min_value=0.0,
            value=500.0,
            help="Produk dengan komisi kurang dari nilai ini tidak akan diproses"
        )
    with col2:
        komisi_rp_max = st.number_input(
            "Max komisi (Rp)", 
            min_value=0.0,
            value=5000.0,
            help="Produk dengan komisi lebih dari nilai ini tidak akan diproses"
        )
    # Filter Jumlah Live Min & Max dalam kolom
    col1, col2 = st.sidebar.columns(2)
    with col1:
        jumlah_live_min = st.number_input(
            "Min jumlah live",
            min_value=0,
            value=0,
            help="Minimum jumlah live listing untuk produk"
        )
    with col2:
        jumlah_live_max = st.number_input(
            "Max jumlah live",
            min_value=0,
            value=0,
            help="Maksimum jumlah live listing untuk produk"
        )
    # Checkbox untuk pengacakan urutan produk
    shuffle_products = st.sidebar.checkbox("Acak produk", value=False, 
                                           help="Centang maka produk anda akan morat-morat.")
    # Upload hanya file .txt
    uploaded_files = st.file_uploader("Masukkan File di Sini", type=["txt"], accept_multiple_files=True)
    def preprocess_data(df):
        df['Harga'] = pd.to_numeric(df['Harga'].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
        df['Stock'] = pd.to_numeric(df['Stock'].astype(str), errors='coerce').fillna(0)
        df['Terjual(Bulanan)'] = pd.to_numeric(df['Terjual(Bulanan)'].astype(str), errors='coerce').fillna(0)
        df['Komisi(%)'] = pd.to_numeric(df['Komisi(%)'].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
        df['Komisi(Rp)'] = pd.to_numeric(df['Komisi(Rp)'].astype(str), errors='coerce').fillna(0)
        df['Jumlah Live'] = pd.to_numeric(df['Jumlah Live'].astype(str), errors='coerce').fillna(0)
        return df
    def apply_filters(df):
        return df[
            (df['Stock'] >= stok_min) &
            (df['Harga'] >= harga_min) &
            (df['Terjual(Bulanan)'] >= terjual_min) &
            (df['Terjual(Bulanan)'] <= terjual_max) &
            (df['Komisi(%)'] >= komisi_persen_min) &
            (df['Komisi(%)'] <= komisi_persen_max) &
            (df['Komisi(Rp)'] >= komisi_rp_min) &
            (df['Komisi(Rp)'] <= komisi_rp_max) &
            (df['Jumlah Live'] >= jumlah_live_min) &
            (df['Jumlah Live'] <= jumlah_live_max)
        ]
    if uploaded_files:
        custom_filename = st.text_input("Masukkan nama file CSV untuk produk lolos filter", value="data_produk")
        custom_filename_sampah = st.text_input("Masukkan nama file CSV untuk produk tidak lolos filter", value="sampah")
        if st.button("🚀 Proses Data"):
            with st.spinner("⏳ Memproses data..."):
                combined_df = pd.DataFrame()
                for file in uploaded_files:
                    df = read_and_validate_file(file, delimiter='\t')
                    if df is not None:
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                if not combined_df.empty:
                    total_links = len(combined_df)
                    combined_df.drop_duplicates(subset=['Link Produk'], inplace=True)
                    deleted_dupes = total_links - len(combined_df)
                    combined_df = preprocess_data(combined_df)
                    filtered_df = apply_filters(combined_df)
                    removed_df = combined_df[~combined_df.index.isin(filtered_df.index)]
                    
                    # Pengacakan urutan produk
                    if shuffle_products:
                        filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)
                        removed_df = removed_df.sample(frac=1).reset_index(drop=True)
                    
                    avg_live = round(filtered_df['Jumlah Live'].mean(), 1) if not filtered_df.empty else 0
                    st.success("✅ Data berhasil diproses!")
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="section-title">📊 Statistik</div>
                        <ul>
                            <li>Total produk diproses: <strong>{total_links}</strong></li>
                            <li>Produk unik setelah hapus duplikat: <strong>{len(combined_df)}</strong></li>
                            <li>Produk lolos filter: <strong>{len(filtered_df)}</strong></li>
                            <li>Produk tidak lolos filter: <strong>{len(removed_df)}</strong></li>
                            <li>Duplikat yang dihapus: <strong>{deleted_dupes}</strong></li>
                            <li>Rata-rata jumlah live: <strong>{avg_live}</strong></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.subheader("✅ Final Produk")
                    st.dataframe(filtered_df)
                    st.download_button(
                        "⬇️ Download Data Produk",
                        filtered_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"{sanitize_filename(custom_filename)}.csv",
                        mime='text/csv'
                    )
                    st.subheader("🗑️ Produk Sampah")
                    st.dataframe(removed_df)
                    st.download_button(
                        "⬇️ Download Sampah",
                        removed_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"{sanitize_filename(custom_filename_sampah)}.csv",
                        mime='text/csv'
                    )
                else:
                    st.warning("Tidak ada data valid yang bisa diproses.")
    else:
        st.info("📁 Silakan upload file terlebih dahulu.")

# === OPSI 2: FILTER PRODUK SHOPTIK ===
elif option == "Filter Produk Shoptik":
    st.title("📱 Filter Produk Shoptik")
    st.markdown("Gunakan filter di bawah ini untuk menganalisis produk dari Shoptik.")
    # Sidebar filter tambahan
    st.sidebar.title("⚙️ Filter Shoptik")
    trend_percentage_min = st.sidebar.number_input("Tren minimum (%)", min_value=0.0, value=50.0,
                                                 help="Persentase tren minimum untuk produk")
    harga_min_shoptik = st.sidebar.number_input("Harga minimum", min_value=0.0, value=0.0,
                                              help="Hanya produk dengan harga di atas nilai ini yang akan diproses")
    penjualan_30_hari_min = st.sidebar.number_input("Penjualan minimum (30 Hari)", min_value=0, value=100,
                                                  help="Produk dengan penjualan kurang dari nilai ini tidak lolos")
    stok_min_shoptik = st.sidebar.number_input("Minimal stok", min_value=0, value=10,
                                             help="Produk dengan stok di bawah nilai ini tidak lolos")
    rating_min = st.sidebar.slider("Rating minimum", min_value=0.0, max_value=5.0, value=4.0, step=0.1,
                                   help="Rating minimum produk")
    is_ad = st.sidebar.checkbox("Tampilkan hanya produk beriklan", value=False,
                                help="Selain produk ber add tidak akan di proses")
    shuffle_products = st.sidebar.checkbox("Acak produk", value=False, 
                                           help="Centang maka produk anda akan morat-morat.")
    uploaded_files = st.file_uploader("Masukkan File", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        custom_filename = st.text_input("Masukkan nama file CSV untuk produk lolos filter", value="data_shoptik")
        custom_filename_sampah = st.text_input("Masukkan nama file CSV untuk produk tidak lolos filter", value="sampah_shoptik")
        if st.button("🔎 Analisis Data"):
            with st.spinner("⏳ Menganalisis data Shoptik..."):
                combined_df = pd.DataFrame()
                for file in uploaded_files:
                    df = read_and_validate_file(file, delimiter=',')
                    if df is not None:
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                if not combined_df.empty:
                    total_products = len(combined_df)
                    combined_df.drop_duplicates(subset=['productLink'], keep='first', inplace=True)
                    deleted_dupes = total_products - len(combined_df)
                    combined_df = preprocess_shoptik(combined_df)
                    filtered_df = apply_shoptik_filters(
                        combined_df,
                        trend_percentage_min,
                        harga_min_shoptik,
                        penjualan_30_hari_min,
                        stok_min_shoptik,
                        rating_min,
                        is_ad
                    )
                    removed_df = combined_df[~combined_df.index.isin(filtered_df.index)]
                    
                    # Pengacakan urutan produk
                    if shuffle_products:
                        filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)
                        removed_df = removed_df.sample(frac=1).reset_index(drop=True)
                    
                    avg_rating = round(filtered_df['Peringkat'].mean(), 1) if not filtered_df.empty else 0
                    avg_trend = round(filtered_df['trendPercentage'].mean(), 1) if not filtered_df.empty else 0
                    st.success("✅ Analisis selesai!")
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="section-title">📊 Statistik Shoptik</div>
                        <ul>
                            <li>Total produk diproses: <strong>{total_products}</strong></li>
                            <li>Produk unik setelah hapus duplikat: <strong>{len(combined_df)}</strong></li>
                            <li>Produk lolos filter: <strong>{len(filtered_df)}</strong></li>
                            <li>Produk tidak lolos filter: <strong>{len(removed_df)}</strong></li>
                            <li>Duplikat berdasarkan link: <strong>{deleted_dupes}</strong></li>
                            <li>Rata-rata rating: <strong>{avg_rating}</strong></li>
                            <li>Rata-rata tren (%): <strong>{avg_trend}%</strong></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.subheader("✅ Produk Lolos Filter")
                    st.dataframe(filtered_df)
                    st.download_button(
                        "⬇️ Download Data Shoptik",
                        filtered_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"{sanitize_filename(custom_filename)}.csv",
                        mime='text/csv'
                    )
                    st.subheader("🗑️ Produk Dihapus")
                    st.dataframe(removed_df)
                    st.download_button(
                        "⬇️ Download Sampah",
                        removed_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"{sanitize_filename(custom_filename_sampah)}.csv",
                        mime='text/csv'
                    )
                else:
                    st.warning("Tidak ada data valid untuk dianalisis.")
    else:
        st.info("📁 Silakan upload file")

# === FOOTER ===
st.markdown("""
    <div class="footer">
        &copy; 2025 - Dibuat oleh Wong Sukses
    </div>
""", unsafe_allow_html=True)
