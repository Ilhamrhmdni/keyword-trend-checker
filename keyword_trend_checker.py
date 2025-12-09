import streamlit as st

st.set_page_config(page_title="Ujian E-Learning Ilham", layout="centered")

# ============================
# 🔧 BAGIAN SOAL – BISA KAMU EDIT
# ============================
# type: "mc" = pilihan ganda, "short" = jawaban singkat
# correct_answer:
#   - untuk "mc" => isi dengan TEKS opsi yang benar
#   - untuk "short" => isi dengan jawaban ideal (dicek lower-case & trim)
questions = [
    {
        "id": 1,
        "type": "mc",
        "question": "Ekspansi fiskal pemerintah biasanya dilakukan untuk...",
        "options": [
            "Menurunkan pendapatan nasional",
            "Meningkatkan permintaan agregat",
            "Mengurangi jumlah uang beredar",
            "Menurunkan tingkat inflasi"
        ],
        "correct_answer": "Meningkatkan permintaan agregat",
        "explanation": "Ekspansi fiskal (menaikkan belanja negara / menurunkan pajak) akan mendorong permintaan agregat."
    },
    {
        "id": 2,
        "type": "mc",
        "question": "Dalam neraca perusahaan manufaktur, urutan persediaan yang benar adalah...",
        "options": [
            "Barang jadi – Barang dalam proses – Bahan baku",
            "Bahan baku – Barang dalam proses – Barang jadi",
            "Barang dalam proses – Bahan baku – Barang jadi",
            "Barang jadi – Bahan baku – Barang dalam proses"
        ],
        "correct_answer": "Bahan baku – Barang dalam proses – Barang jadi",
        "explanation": "Urutan alur produksi: Bahan baku → Barang dalam proses → Barang jadi."
    },
    {
        "id": 3,
        "type": "mc",
        "question": "Tarif overhead pabrik di muka (predetermined overhead rate) dihitung dengan...",
        "options": [
            "BOP aktual / Jam mesin aktual",
            "BOP taksiran / Aktivitas operasional taksiran",
            "BOP aktual / Aktivitas taksiran",
            "Produksi aktual / BOP taksiran"
        ],
        "correct_answer": "BOP taksiran / Aktivitas operasional taksiran",
        "explanation": "Tarif di muka = BOP taksiran ÷ dasar pembebanan taksiran (jam TKL, jam mesin, dll)."
    },
    {
        "id": 4,
        "type": "short",
        "question": "Tuliskan urutan penyajian persediaan di neraca perusahaan manufaktur!",
        "correct_answer": "bahan baku - barang dalam proses - barang jadi",
        "explanation": "Jawaban ideal: Bahan baku – Barang dalam proses – Barang jadi."
    },
    # Tambah soal lagi di bawah ini kalau mau
    # {
    #     "id": 5,
    #     "type": "short",
    #     "question": "Contoh soal isian singkat...",
    #     "correct_answer": "isi jawaban di sini",
    #     "explanation": "Penjelasan singkat."
    # },
]

# ============================
# ⛔ DI BAWAH INI BIARKAN SAJA
# ============================

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False


def submit():
    st.session_state["submitted"] = True


st.title("Ujian E-Learning Ilham 🧠")
st.write(
    "Latihan UAS mandiri. Kerjakan dulu semua soal, lalu klik **Periksa Jawaban** "
    "untuk melihat benar/salah dan nilai."
)

correct_count = 0
total_questions = len(questions)

# Render soal
for q in questions:
    st.markdown(f"### Soal {q['id']}")
    st.write(q["question"])

    user_answer = None

    if q["type"] == "mc":
        user_answer = st.radio(
            "Pilih jawaban:",
            q["options"],
            key=f"q{q['id']}",
            index=None
        )
    elif q["type"] == "short":
        user_answer = st.text_area(
            "Jawabanmu:",
            key=f"q{q['id']}",
            height=60
        )

    # Tampilkan feedback jika sudah submit
    if st.session_state["submitted"]:
        ua = (user_answer or "").strip().lower()
        ca = (q["correct_answer"] or "").strip().lower()

        if ua == "":
            st.markdown("❗ **Belum dijawab.**")
        elif ua == ca:
            correct_count += 1
            st.markdown("✅ **Benar**")
        else:
            st.markdown("❌ **Salah**")

        if q.get("explanation"):
            st.markdown(f"> ℹ️ *{q['explanation']}*")

    st.markdown("---")

# Tombol submit
st.button("Periksa Jawaban", on_click=submit)

# Skor total
if st.session_state["submitted"]:
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    st.success(f"Hasil: {correct_count} dari {total_questions} soal benar. Nilai: {score:.2f}")
