import json
import base64
import urllib.request
import requests
import streamlit as st

st.set_page_config(page_title="Ujian E-Learning Yulia", layout="centered")

# ======================================
# 🔗 KONFIGURASI GITHUB (REPO KAMU)
# ======================================

REPO_NAME = "Ilhamrhmdni/keyword-trend-checker"
BRANCH = "main"

# 🎓 DAFTAR MATA KULIAH & NAMA FILE JSON
# key = kode internal, label = tampilan di UI, filename = nama file di repo
MATKULS = {
    "pkn": {
        "label": "Pancasila",
        "filename": "pkn.json",
    },
    "bindo": {
        "label": "Bahasa Indonesia",
        "filename": "bahasaindonesia.json",
    },
    # contoh kalau mau nambah:
    # "ekonomi": {
    #     "label": "Ekonomi Makro",
    #     "filename": "ekonomi.json",
    # },
}


def get_raw_url(filename: str) -> str:
    """Bikin RAW URL GitHub dari nama file."""
    return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{filename}"


# ======================================
# 📥 FUNGSI LOAD SOAL DARI GITHUB (READ)
# ======================================
def load_questions_from_github(matkul_key: str):
    cfg = MATKULS.get(matkul_key)
    if not cfg:
        st.error(f"Matkul '{matkul_key}' tidak dikenal.")
        return []

    raw_url = get_raw_url(cfg["filename"])
    try:
        with urllib.request.urlopen(raw_url) as response:
            data = response.read().decode("utf-8")
        questions = json.loads(data)
        if isinstance(questions, list):
            return questions
        else:
            st.warning(
                f"Format JSON {cfg['filename']} tidak berupa list []. Periksa file di GitHub."
            )
            return []
    except Exception as e:
        st.error(f"Gagal memuat soal {cfg['filename']} dari GitHub (read): {e}")
        return []


# ======================================
# 💾 FUNGSI SAVE SOAL KE GITHUB (WRITE)
# ======================================
def save_questions_to_github(questions, matkul_key: str) -> bool:
    """
    Meng-overwrite file JSON matkul di GitHub dengan isi dari 'questions'.
    Return True kalau sukses, False kalau gagal.
    """
    token = st.secrets.get("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN belum diset di secrets. Set dulu di Streamlit secrets.")
        return False

    cfg = MATKULS.get(matkul_key)
    if not cfg:
        st.error(f"Matkul '{matkul_key}' tidak dikenal.")
        return False

    filename = cfg["filename"]
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{filename}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Ambil sha file lama (kalau ada)
    sha = None
    get_r = requests.get(api_url, headers=headers)
    if get_r.status_code == 200:
        sha = get_r.json().get("sha")
    elif get_r.status_code == 404:
        sha = None  # file belum ada, nanti dibuat baru
    else:
        st.error(
            f"Gagal mengambil info {filename} dari GitHub: {get_r.status_code} {get_r.text}"
        )
        return False

    new_content = json.dumps(questions, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": f"Update soal {filename} via Streamlit app",
        "content": encoded_content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put_r = requests.put(api_url, headers=headers, json=payload)

    if put_r.status_code in (200, 201):
        st.success(f"✔ {filename} berhasil disimpan ke GitHub.")
        return True
    else:
        st.error(f"Gagal menyimpan soal ke GitHub: {put_r.status_code} {put_r.text}")
        return False


# ============================
# 🔁 INISIALISASI STATE
# ============================
if "selected_subject" not in st.session_state:
    # default matkul = yang pertama di MATKULS
    st.session_state["selected_subject"] = next(iter(MATKULS.keys()))

if "questions" not in st.session_state:
    st.session_state["questions"] = load_questions_from_github(
        st.session_state["selected_subject"]
    )

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "editing_id" not in st.session_state:
    st.session_state["editing_id"] = None  # ID soal yang sedang diedit


def reset_submit_flag():
    st.session_state["submitted"] = False


def change_subject(new_key: str):
    st.session_state["selected_subject"] = new_key
    st.session_state["questions"] = load_questions_from_github(new_key)
    st.session_state["submitted"] = False
    st.session_state["editing_id"] = None


# ============================
# 🧭 SIDEBAR MENU
# ============================
st.sidebar.title("Menu")

# Pilih mata kuliah dulu
subject_labels = {k: v["label"] for k, v in MATKULS.items()}
current_subject = st.sidebar.selectbox(
    "Pilih Mata Kuliah:",
    options=list(subject_labels.keys()),
    format_func=lambda k: subject_labels[k],
    index=list(subject_labels.keys()).index(st.session_state["selected_subject"]),
    on_change=lambda: None,
)

# Kalau berubah, kita panggil manually
if current_subject != st.session_state["selected_subject"]:
    change_subject(current_subject)

matkul_label = subject_labels[st.session_state["selected_subject"]]

menu = st.sidebar.radio(
    "Pilih halaman:",
    ("Kerjakan Soal", "Setelan Tambahan"),
    on_change=reset_submit_flag,
)

if st.sidebar.button("🔄 Muat ulang soal"):
    st.session_state["questions"] = load_questions_from_github(
        st.session_state["selected_subject"]
    )
    st.session_state["submitted"] = False
    st.sidebar.success(f"Soal {matkul_label} berhasil dimuat ulang.")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(
    f"Matkul aktif: **{matkul_label}**\n\nJumlah soal di session: **{len(st.session_state['questions'])}**"
)
st.sidebar.caption("Perubahan disimpan ke GitHub saat kamu tambah/hapus/edit soal.")


# ============================
# 📄 HALAMAN 1: KERJAKAN SOAL
# ============================
def page_kerjakan_soal():
    matkul_key = st.session_state["selected_subject"]
    matkul_label_local = MATKULS[matkul_key]["label"]

    st.title(f"Kerjakan Soal – {matkul_label_local} 🧠")
    st.write(
        f"Sumber soal: **{MATKULS[matkul_key]['filename']}** di GitHub.\n\n"
        "Kerjakan semua soal dulu, lalu klik **Periksa Jawaban** "
        "untuk melihat mana yang benar/salah dan nilai akhirnya."
    )

    questions = st.session_state["questions"]
    if not questions:
        st.warning(
            "Belum ada soal yang dimuat untuk matkul ini. "
            "Coba klik 'Muat ulang soal.' "
        )
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
                key=f"{matkul_key}-q{q_id}",
                index=None,
            )
        else:  # short
            user_answer = st.text_area(
                "Jawabanmu:",
                key=f"{matkul_key}-q{q_id}",
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
# ✏ HALAMAN 2: TAMBAH / HAPUS / EDIT SOAL
# ============================
def page_tambah_hapus_edit_soal():
    matkul_key = st.session_state["selected_subject"]
    matkul_label_local = MATKULS[matkul_key]["label"]

    st.title(f"Kelola Soal – {matkul_label_local} ✍️")
    st.write(
        "Perubahan di sini akan:\n"
        f"1. Mengubah soal di session untuk matkul **{matkul_label_local}**.\n"
        f"2. **Langsung menyimpan ulang {MATKULS[matkul_key]['filename']} ke GitHub (auto-save).**"
    )

    questions = st.session_state["questions"]

    # =====================
    # 🔁 FORM EDIT SOAL (JIKA ADA YANG SEDANG DIEDIT)
    # =====================
    editing_id = st.session_state.get("editing_id")
    if editing_id is not None:
        q_edit = next((q for q in questions if q.get("id") == editing_id), None)
        st.markdown("---")
        st.subheader(f"Edit Soal (ID {editing_id})")

        if q_edit is None:
            st.warning("Soal yang mau diedit tidak ditemukan.")
        else:
            q_type = q_edit.get("type", "mc")
            jenis_label = "Pilihan Ganda" if q_type == "mc" else "Jawaban Singkat"
            st.caption(f"Jenis soal: **{jenis_label}** (tidak bisa diubah)")

            with st.form("form_edit_soal"):
                question_text = st.text_area(
                    "Teks soal",
                    value=q_edit.get("question", ""),
                    height=80,
                )
                explanation = st.text_area(
                    "Penjelasan (opsional)",
                    value=q_edit.get("explanation", ""),
                    height=60,
                )

                options = []
                correct_answer = ""

                if q_type == "mc":
                    old_opts = q_edit.get("options", [])
                    opt_a = st.text_input(
                        "Opsi A", value=old_opts[0] if len(old_opts) > 0 else ""
                    )
                    opt_b = st.text_input(
                        "Opsi B", value=old_opts[1] if len(old_opts) > 1 else ""
                    )
                    opt_c = st.text_input(
                        "Opsi C", value=old_opts[2] if len(old_opts) > 2 else ""
                    )
                    opt_d = st.text_input(
                        "Opsi D", value=old_opts[3] if len(old_opts) > 3 else ""
                    )

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

                else:  # short
                    correct_answer = st.text_input(
                        "Jawaban yang benar (ideal)",
                        value=q_edit.get("correct_answer", ""),
                    )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    submit_edit = st.form_submit_button("💾 Simpan Perubahan")
                with col_cancel:
                    cancel_edit = st.form_submit_button("Batal Edit")

                if cancel_edit:
                    st.session_state["editing_id"] = None
                    st.info("Edit dibatalkan.")
                    st.rerun()

                if submit_edit:
                    if not question_text.strip():
                        st.error("Teks soal tidak boleh kosong.")
                    else:
                        if q_type == "mc":
                            if len(options) < 2:
                                st.error("Minimal isi dua opsi jawaban.")
                                return
                            if not correct_answer:
                                st.error(
                                    "Jawaban benar tidak valid (periksa kembali opsi dan pilihan huruf)."
                                )
                                return

                            updated = {
                                "id": editing_id,
                                "type": "mc",
                                "question": question_text.strip(),
                                "options": options,
                                "correct_answer": correct_answer.strip(),
                                "explanation": explanation.strip(),
                            }
                        else:
                            if not correct_answer.strip():
                                st.error("Jawaban benar tidak boleh kosong.")
                                return
                            updated = {
                                "id": editing_id,
                                "type": "short",
                                "question": question_text.strip(),
                                "correct_answer": correct_answer.strip().lower(),
                                "explanation": explanation.strip(),
                            }

                        for i, qq in enumerate(questions):
                            if qq.get("id") == editing_id:
                                questions[i] = updated
                                break

                        if save_questions_to_github(questions, matkul_key):
                            st.session_state["questions"] = questions
                            st.session_state["editing_id"] = None
                            st.success(f"Soal ID {editing_id} berhasil diupdate.")
                            st.rerun()

    st.markdown("---")

    # =====================
    # ➕ FORM TAMBAH SOAL BARU
    # =====================
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
                        st.error(
                            "Jawaban benar tidak valid (periksa kembali opsi dan pilihan huruf)."
                        )
                        return

                    new_question = {
                        "id": max(
                            [q.get("id", 0) for q in questions]
                        ) + 1 if questions else 1,
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
                        "id": max(
                            [q.get("id", 0) for q in questions]
                        ) + 1 if questions else 1,
                        "type": "short",
                        "question": question_text.strip(),
                        "correct_answer": correct_answer.strip().lower(),
                        "explanation": explanation.strip(),
                    }

                questions.append(new_question)
                if save_questions_to_github(questions, matkul_key):
                    st.session_state["questions"] = questions
                    st.success(
                        f"Soal baru berhasil ditambahkan (ID {new_question['id']})."
                    )

    st.markdown("---")

    # =====================
    # 📋 DAFTAR SOAL + EDIT/HAPUS
    # =====================
    st.subheader("Daftar Soal Saat Ini")

    if not questions:
        st.info("Belum ada soal.")
        return

    for q in questions:
        q_id = q.get("id", "?")
        col1, col2, col3, col4 = st.columns([6, 2, 1.5, 1.5])
        with col1:
            text = q.get("question", "")
            potong = (text[:90] + "…") if len(text) > 90 else text
            st.markdown(f"**ID {q_id}** – {potong}")
        with col2:
            jenis = "Pilihan Ganda" if q.get("type") == "mc" else "Jawaban Singkat"
            st.markdown(f"_{jenis}_")
        with col3:
            if st.button("Edit", key=f"edit-{matkul_key}-{q_id}"):
                st.session_state["editing_id"] = q_id
                st.rerun()
        with col4:
            if st.button("Hapus", key=f"hapus-{matkul_key}-{q_id}"):
                st.session_state["questions"] = [
                    qq for qq in questions if qq.get("id") != q_id
                ]
                if save_questions_to_github(st.session_state["questions"], matkul_key):
                    st.success(f"Soal dengan ID {q_id} telah dihapus.")
                    st.rerun()


# ============================
# 🚦 ROUTING HALAMAN
# ============================
if menu == "Kerjakan Soal":
    page_kerjakan_soal()
elif menu == "Tambah / Hapus / Edit Soal":
    page_tambah_hapus_edit_soal()
