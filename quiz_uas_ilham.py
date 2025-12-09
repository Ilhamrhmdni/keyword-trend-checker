import json
import base64
import urllib.request
import requests
import streamlit as st

st.set_page_config(page_title="Ujian E-Learning Ilham", layout="centered")

# ======================================
# 🔗 KONFIGURASI GITHUB (GANTI PUNYA MU)
# ======================================

# 1) RAW URL soal.json
URL_SOAL_GITHUB = (
    "https://raw.githubusercontent.com/Ilhamrhmdni/keyword-trend-checker/main/soal.json"
    # contoh: "https://raw.githubusercontent.com/ilhamdank/quiz-uas/main/soal.json"
)

# 2) Nama repo "username/repo"
REPO_NAME = "Ilhamrhmdni/keyword-trend-checker"  # contoh: "ilhamdank/quiz-uas"

# 3) Lokasi file soal di repo
FILE_PATH = "soal.json"  # kalau kamu taruh di folder, misal: "data/soal.json"

# 4) Branch yang dipakai
BRANCH = "main"


# ======================================
# 📥 FUNGSI LOAD SOAL DARI GITHUB (READ)
# ======================================
def load_questions_from_github():
    try:
        with urllib.request.urlopen(URL_SOAL_GITHUB) as response:
            data = response.read().decode("utf-8")
        questions = json.loads(data)
        if isinstance(questions, list):
            return questions
        else:
            st.warning("Format JSON soal tidak berupa list []. Periksa soal.json.")
            return []
    except Exception as e:
        st.error(f"Gagal memuat soal dari GitHub (read): {e}")
        return []


# ======================================
# 💾 FUNGSI SAVE SOAL KE GITHUB (WRITE)
# ======================================
def save_questions_to_github(questions):
    """Meng-overwrite file soal.json di GitHub dengan isi dari 'questions'."""
    token = st.secrets.get("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN belum diset di secrets. Set dulu di Streamlit secrets.")
        return

    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # ambil sha file lama (kalau ada)
    sha = None
    get_r = requests.get(api_url, headers=headers)
    if get_r.status_code == 200:
        sha = get_r.json().get("sha")

    # isi baru file
    new_content = json.dumps(questions, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Update soal via Streamlit app",
        "content": encoded_content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha  # diperlukan kalau overwrite file yang sudah ada

    put_r = requests.put(api_url, headers=headers, json=payload)

    if put_r.status_code in (200, 201):
        st.success("✔ soal.json berhasil disimpan ke GitHub.")
    else:
        st.error(f"Gagal menyimpan soal ke GitHub: {put_r.status_code} {put_r.text}")


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

if st.sidebar.button("🔄 Muat ulang soal dari GitHub (READ)"):
    st.session_state["questions"] = load_questions_from_github()
    st.session_state["submitted"] = False
    st.sidebar.success("Soal berhasil dimuat ulang dari GitHub.")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"Jumlah soal di session: **{len(st.session_state['questions'])}**")
st.sidebar.caption("Perubahan disimpan ke GitHub saat kamu tambah/hapus soal.")


# ============================
# 📄 HALAMAN 1: KERJAKAN SOAL
# ============================
def page_kerjakan_soal():
    st.title("Kerjakan Soal Ujian 🧠")
    st.write(
        "Sumber soal utama: **soal.json di GitHub**.\n\n"
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
        q_id = q.get("id", "?")
        q_type = q.get("type", "mc")

        st.markdown(f"### Soal {q_id}")
        st.write(q.get("question", ""))

        user_answer = None

        if q_type == "mc":
            options = q.get("options", [])
            user_answer = st.radio(
                "Pilih jawaban:",
                options,
                key=f"q{q_id}",
                index=None,
            )
        else:  # short
            user_answer = st.text_area(
                "Jawabanmu:",
                key=f"q{q_id}",
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
# ➕ HALAMAN 2: TAMBAH & HAPUS SOAL
# ============================
def page_tambah_hapus_soal():
    st.title("Tambah / Hapus Soal ✍️")
    st.write(
        "Perubahan di sini akan:\n"
        "1. Mengubah soal di session.\n"
        "2. **Langsung menyimpan ulang soal.json ke GitHub (auto-save).**"
    )

    # ---------- FORM TAMBAH SOAL ----------
    st.subheader("Tambah Soal Baru")

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
            else:
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
                # AUTO-SAVE ke GitHub
                save_questions_to_github(st.session_state["questions"])
                st.success(f"Soal baru berhasil ditambahkan & disimpan ke GitHub (ID {new_question['id']}).")

    st.markdown("---")

    # ---------- DAFTAR SOAL + HAPUS ----------
    st.subheader("Daftar Soal Saat Ini")

    if not st.session_state["questions"]:
        st.info("Belum ada soal.")
        return

    for q in st.session_state["questions"]:
        q_id = q.get("id", "?")
        col1, col2, col3 = st.columns([6, 2, 2])
        with col1:
            text = q.get("question", "")
            potong = (text[:90] + "…") if len(text) > 90 else text
            st.markdown(f"**ID {q_id}** – {potong}")
        with col2:
            jenis = "Pilihan Ganda" if q.get("type") == "mc" else "Jawaban Singkat"
            st.markdown(f"_{jenis}_")
        with col3:
            if st.button("Hapus", key=f"hapus-{q_id}"):
                st.session_state["questions"] = [
                    qq for qq in st.session_state["questions"] if qq.get("id") != q_id
                ]
                # AUTO-SAVE setelah hapus
                save_questions_to_github(st.session_state["questions"])
                st.success(f"Soal dengan ID {q_id} telah dihapus & disimpan ke GitHub.")
                st.rerun()


# ============================
# 🚦 ROUTING HALAMAN
# ============================
if menu == "Kerjakan Soal":
    page_kerjakan_soal()
elif menu == "Tambah / Hapus Soal":
    page_tambah_hapus_soal()
