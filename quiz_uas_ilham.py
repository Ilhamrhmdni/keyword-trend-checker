import streamlit as st

st.set_page_config(page_title="Ujian E-Learning Yulia", layout="centered")

# ============================
# 🔧 SOAL DEFAULT (bisa diedit di sini)
# ============================
default_questions = [
    {
        "id": 1,
        "type": "mc",  # multiple choice
        "question": "Ekspansi fiskal pemerintah biasanya dilakukan untuk...",
        "options": [
            "Menurunkan pendapatan nasional",
            "Meningkatkan permintaan agregat",
            "Mengurangi jumlah uang beredar",
            "Menurunkan tingkat inflasi"
        ],
        "correct_answer": "Meningkatkan permintaan agregat",
        "explanation": "Ekspansi fiskal (menaikkan belanja negara / menurunkan pajak) mendorong permintaan agregat."
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
        "type": "short",  # jawaban singkat
        "question": "Tuliskan urutan penyajian persediaan di neraca perusahaan manufaktur!",
        "correct_answer": "bahan baku - barang dalam proses - barang jadi",
        "explanation": "Jawaban ideal: Bahan baku – Barang dalam proses – Barang jadi."
    },
]


# ============================
# 🔁 INISIALISASI STATE
# ============================
if "questions" not in st.session_state:
    # copy default questions ke session
    st.session_state["questions"] = list(default_questions)

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False


def reset_submit_flag():
    st.session_state["submitted"] = False


# ============================
# 🧭 SIDEBAR MENU
# ============================
st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "Pilih halaman:",
    ("Kerjakan Soal", "Tambah Soal"),
    on_change=reset_submit_flag
)

st.sidebar.markdown("---")
st.sidebar.write(f"Jumlah soal saat ini: **{len(st.session_state['questions'])}**")


# ============================
# 📄 HALAMAN 1: KERJAKAN SOAL
# ============================
def page_kerjakan_soal():
    st.title("Kerjakan Soal Ujian 🧠")
    st.write(
        "Kerjakan semua soal dulu, lalu klik **Periksa Jawaban** "
        "untuk lihat mana yang benar/salah dan nilai akhirnya."
    )

    questions = st.session_state["questions"]
    correct_count = 0
    total_questions = len(questions)

    # Render semua soal
    for q in questions:
        st.markdown(f"### Soal {q['id']}")
        st.write(q["question"])

        user_answer = None

        # Pilihan ganda
        if q["type"] == "mc":
            user_answer = st.radio(
                "Pilih jawaban:",
                q["options"],
                key=f"q{q['id']}",
                index=None
            )

        # Jawaban singkat
        elif q["type"] == "short":
            user_answer = st.text_area(
                "Jawabanmu:",
                key=f"q{q['id']}",
                height=60
            )

        # Feedback setelah tombol ditekan
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
    if st.button("Periksa Jawaban"):
        st.session_state["submitted"] = True
        st.experimental_rerun()

    # Skor total
    if st.session_state["submitted"]:
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        st.success(
            f"Hasil: {correct_count} dari {total_questions} soal benar. "
            f"Nilai: {score:.2f}"
        )


# ============================
# ➕ HALAMAN 2: TAMBAH SOAL
# ============================
def page_tambah_soal():
    st.title("Tambah Soal ✍️")
    st.write(
        "Di sini kamu bisa nambah soal baru. "
        "Soal yang ditambahkan akan langsung muncul di menu **Kerjakan Soal** (selama app masih berjalan)."
    )

    with st.form("form_tambah_soal"):
        tipe = st.selectbox(
            "Jenis soal",
            ("Pilihan Ganda", "Jawaban Singkat")
        )
        question_text = st.text_area("Teks soal", height=80)

        explanation = st.text_area("Penjelasan (opsional)", height=60)

        options = []
        correct_answer = ""

        if tipe == "Pilihan Ganda":
            st.markdown("#### Opsi Jawaban")
            opt_a = st.text_input("Opsi A")
            opt_b = st.text_input("Opsi B")
            opt_c = st.text_input("Opsi C", value="")
            opt_d = st.text_input("Opsi D", value="")

            # Simpan hanya yang tidak kosong
            options = [o for o in [opt_a, opt_b, opt_c, opt_d] if o.strip()]

            kunci_huruf = st.selectbox(
                "Jawaban benar (pilih huruf)",
                ("A", "B", "C", "D")
            )

            # Tentukan correct_answer berdasarkan huruf & opsi
            index_mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
            idx = index_mapping[kunci_huruf]

            if idx < len(options):
                correct_answer = options[idx].strip()
            else:
                correct_answer = ""  # nanti dicek saat submit

        else:  # Jawaban singkat
            correct_answer = st.text_input(
                "Jawaban yang benar (ideal)",
                placeholder="Contoh: bahan baku - barang dalam proses - barang jadi"
            )

        submitted = st.form_submit_button("Tambah Soal")

        if submitted:
            if not question_text.strip():
                st.error("Teks soal tidak boleh kosong.")
                return

            if tipe == "Pilihan Ganda":
                if len(options) < 2:
                    st.error("Minimal isi dua opsi jawaban.")
                    return
                if not correct_answer:
                    st.error("Jawaban benar tidak valid (periksa kembali opsi dan pilihan huruf).")
                    return

                new_question = {
                    "id": max([q["id"] for q in st.session_state["questions"]]) + 1
                    if st.session_state["questions"] else 1,
                    "type": "mc",
                    "question": question_text.strip(),
                    "options": options,
                    "correct_answer": correct_answer.strip(),
                    "explanation": explanation.strip()
                }

            else:  # Jawaban singkat
                if not correct_answer.strip():
                    st.error("Jawaban benar tidak boleh kosong.")
                    return

                new_question = {
                    "id": max([q["id"] for q in st.session_state["questions"]]) + 1
                    if st.session_state["questions"] else 1,
                    "type": "short",
                    "question": question_text.strip(),
                    "correct_answer": correct_answer.strip().lower(),
                    "explanation": explanation.strip()
                }

            # Tambahkan ke session_state
            st.session_state["questions"].append(new_question)
            st.success(f"Soal baru berhasil ditambahkan (ID {new_question['id']}).")
            st.info("Coba buka menu **Kerjakan Soal** di sidebar untuk melihat soal yang baru.")


# ============================
# 🚦 ROUTING HALAMAN
# ============================
if menu == "Kerjakan Soal":
    page_kerjakan_soal()
elif menu == "Tambah Soal":
    page_tambah_soal()
