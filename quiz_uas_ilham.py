import json
import urllib.request
import streamlit as st

st.set_page_config(page_title="Ujian E-Learning Ilham", layout="centered")

# ======================================
# 🔗 URL JSON GITHUB (GANTI DENGAN PUNYAMU)
# ======================================
URL_SOAL_GITHUB = (
    "https://raw.githubusercontent.com/USERNAME/NAMA_REPO/main/soal.json"
    # contoh: "https://raw.githubusercontent.com/ilhamdank/quiz-uas/main/soal.json"
)


# ======================================
# 📥 FUNGSI LOAD SOAL DARI GITHUB (JSON)
# ======================================
def load_questions_from_github():
    try:
        with urllib.request.urlopen(URL_SOAL_GITHUB) as response:
            data = response.read().decode("utf-8")
        questions = json.loads(data)
        # pastikan minimal struktur yang diharapkan
        if isinstance(questions, list):
            return questions
        else:
            st.warning("Format JSON soal tidak berupa list. Pastikan file soal.json berisi array [].")
            return []
    except Exception as e:
        st.error(f"Gagal memuat soal dari GitHub: {e}")
        return []


# ============================
# 🔁 INISIALISASI STATE
# ============================
if "questions" not in st.session_state:
    st.session_state["questions"] = load_questions_from_github()

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
    ("Kerjakan Soal", "Tambah / Hapus Soal"),
    on_change=reset_submit_flag,
)

if st.sidebar.button("🔄 Muat ulang soal dari GitHub"):
    st.session_state["questions"] = load_questions_from_github()
    st.session_state["submitted"] = False
    st.sidebar.success("Soal berhasil dimuat ulang dari GitHub.")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"Jumlah soal saat ini: **{len(st.session_state['questions'])}**")
st.sidebar.caption("Catatan: perubahan di sini tidak otomatis tersimpan ke GitHub.")


# ============================
# 📄 HALAMAN 1: KERJAKAN SOAL
# ============================
def page_kerjakan_soal():
    st.title("Kerjakan Soal Ujian 🧠")
    st.write(
        "Sumber soal: **JSON di GitHub**.\n\n"
        "Kerjakan semua soal dulu, lalu klik **Periksa Jawaban** "
        "untuk melihat mana yang benar/salah dan nilai akhirnya."
    )

    questions = st.session_state["questions"]
    if not questions:
        st.warning("Belum ada soal yang dimuat. Coba klik 'Muat ulang soal dari GitHub' di sidebar.")
        return

    correct_count = 0
    total_questions = len(questions)

    for q in questions:
        st.markdown(f"### Soal {q.get('id', '?')}")
        st.write(q.get("question", ""))

        q_type = q.get("type", "mc")
        user_answer = None

        if q_type == "mc":
            options = q.get("options", [])
            user_answer = st.radio(
                "Pilih jawaban:",
                options,
                key=f"q{q.get('id')}",
                index=None,
            )
        else:  # short
            user_answer = st.text_area(
                "Jawabanmu:",
                key=f"q{q.get('id')}",
                height=60,
            )

        if st.session_state["submitted"]:
            ua = (user_answer or "").strip().lower()
            ca = (q.get("correct_answer", "") or "").strip().lower()

            if ua == "":
                st.markdown("❗ **Belum dijawab.**")
            elif ua == ca:
                correct_count += 1
                st.markdown("✅ **Benar**")
            else:
                st.markdown("❌ **Salah**")

            explanation = q.get("explanation", "")
            if explanation:
                st.markdown(f"> ℹ️ *{explanation}*")

        st.markdown("---")

    if st.button("Periksa Jawaban"):
        st.session_state["submitted"] = True
        st.rerun()

    if st.session_state["submitted"]:
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        st.success(
            f"Hasil: {correct_count} dari {total_questions} soal benar. "
            f"Nilai: {score:.2f}"
        )


# ============================
# ➕ HALAMAN 2: TAMBAH & HAPUS SOAL (SESSION ONLY)
# ============================
def page_tambah_hapus_soal():
    st.title("Tambah / Hapus Soal ✍️")
    st.write(
        "Perubahan di halaman ini **hanya tersimpan di memori (session)**.\n"
        "Kalau mau permanen, kamu perlu mengedit file `soal.json` di GitHub secara manual."
    )

    # ---------- FORM TAMBAH SOAL ----------
    st.subheader("Tambah Soal Baru (session)")

    with st.form("form_tambah_soal"):
        tipe = st.selectbox(
            "Jenis soal",
            ("Pilihan Ganda", "Jawaban Singkat"),
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

            options = [o for o in [opt_a, opt_b, opt_c, opt_d] if o.strip()]

            kunci_huruf = st.selectbox(
                "Jawaban benar (pilih huruf)",
                ("A", "B", "C", "D"),
            )

            index_mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
            idx = index_mapping[kunci_huruf]

            if idx < len(options):
                correct_answer = options[idx].strip()
            else:
                correct_answer = ""

        else:  # Jawaban singkat
            correct_answer = st.text_input(
                "Jawaban yang benar (ideal)",
                placeholder="Contoh: bahan baku - barang dalam proses - barang jadi",
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
                    "id": max([q.get("id", 0) for q in st.session_state["questions"]]) + 1
                    if st.session_state["questions"]
                    else 1,
                    "type": "mc",
                    "question": question_text.strip(),
                    "options": options,
                    "correct_answer": correct_answer.strip(),
                    "explanation": explanation.strip(),
                }

            else:  # Jawaban singkat
                if not correct_answer.strip():
                    st.error("Jawaban benar tidak boleh kosong.")
                    return

                new_question = {
                    "id": max([q.get("id", 0) for q in st.session_state["questions"]]) + 1
                    if st.session_state["questions"]
                    else 1,
                    "type": "short",
                    "question": question_text.strip(),
                    "correct_answer": correct_answer.strip().lower(),
                    "explanation": explanation.strip(),
                }

            st.session_state["questions"].append(new_question)
            st.success(f"Soal baru berhasil ditambahkan (ID {new_question['id']}).")
            st.info("Soal ini hanya tersimpan di session. Untuk permanen, tambahkan juga ke soal.json di GitHub.")

    st.markdown("---")

    # ---------- DAFTAR SOAL + HAPUS ----------
    st.subheader("Daftar Soal Saat Ini (session)")

    if not st.session_state["questions"]:
        st.info("Belum ada soal.")
        return

    for q in st.session_state["questions"]:
        col1, col2, col3 = st.columns([6, 2, 2])
        with col1:
            text = q.get("question", "")
            potong = (text[:90] + "…") if len(text) > 90 else text
            st.markdown(f"**ID {q.get('id', '?')}** – {potong}")
        with col2:
            jenis = "Pilihan Ganda" if q.get("type") == "mc" else "Jawaban Singkat"
            st.markdown(f"_{jenis}_")
        with col3:
            if st.button("Hapus", key=f"hapus-{q.get('id')}"):
                st.session_state["questions"] = [
                    qq for qq in st.session_state["questions"] if qq.get("id") != q.get("id")
                ]
                st.success(f"Soal dengan ID {q.get('id')} telah dihapus (di session).")
                st.rerun()


# ============================
# 🚦 ROUTING HALAMAN
# ============================
if menu == "Kerjakan Soal":
    page_kerjakan_soal()
elif menu == "Tambah / Hapus Soal":
    page_tambah_hapus_soal()
