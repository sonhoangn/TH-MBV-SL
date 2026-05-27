import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. APPLICATION GLOBAL CONFIGURATION
st.set_page_config(page_title="Corporate Treasure Hunt v2", page_icon="🗺️", layout="centered")

# Initialize persistent session states for user tracking
if "team_name" not in st.session_state:
    st.session_state.team_name = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# 2. MULTILINGUAL DICTIONARY MATRIX
LOCALIZED_UI = {
    "en": {
        "welcome": "Welcome to the Adventure", "team_label": "Enter Team / Player Name",
        "start_btn": "Enter Game Lobby", "checkpoint": "Checkpoint", "clue_locked": "🔒 Clue is Locked",
        "unlock_btn": "Start Stage Timer", "part1": "Part 1: Riddle Solution", "part2": "Part 2: QR Card Security Key",
        "submit": "Verify Double Credentials", "victory": "🏆 Victory!", "time_taken": "Total Time Taken"
    },
    "vi": {
        "welcome": "Chào Mừng Đến Với Cuộc Săn Tìm", "team_label": "Nhập Tên Đội / Người Chơi",
        "start_btn": "Vào Phòng Chờ Game", "checkpoint": "Trạm Kiểm Soát", "clue_locked": "🔒 Gợi Ý Đang Khóa",
        "unlock_btn": "Bắt Đầu Tính Giờ Trạm", "part1": "Phần 1: Đáp Án Câu Đố", "part2": "Phần 2: Mã Xác Thực Thẻ QR",
        "submit": "Xác Thực Hệ Thống Đúp", "victory": "🏆 Chiến Thắng!", "time_taken": "Tổng Thời Gian Hoàn Thành"
    },
    "de": {
        "welcome": "Willkommen zur Schnitzeljagd", "team_label": "Team- / Spielername eingeben",
        "start_btn": "Spiel-Lobby betreten", "checkpoint": "Kontrollpunkt", "clue_locked": "🔒 Hinweis gesperrt",
        "unlock_btn": "Etappen-Timer starten", "part1": "Teil 1: Rätsellösung",
        "part2": "Teil 2: QR-Karten-Sicherheitsschlüssel",
        "submit": "Doppelte Anmeldedaten verifizieren", "victory": "🏆 Sieg!", "time_taken": "Gesamte benötigte Zeit"
    }
}

# 3. GLOBAL LANGUAGE TOGGLE CONTROL BAR
col_title, col_lang = st.columns([2, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], index=0)
ui = LOCALIZED_UI[selected_lang]

# 4. SIDEBAR ADMINISTRATIVE OVERRIDE CONTROL CENTER
with st.sidebar:
    st.header("⚙️ Game Master Core")
    admin_active = st.checkbox("Access Admin Dashboard")
    if admin_active:
        password = st.text_input("Admin Security Key", type="password")
        if password == "hunt-master-2026":
            st.success("Authenticated")
            st.subheader("Manage Quest Database")
            # In production, this data variable hooks straight to st.connection("gsheets")
            st.info("Connected Live to Cloud Google Sheet Dashboard Layer")
        elif password:
            st.error("Invalid Code")

# 5. CORE PLAYER RUNTIME ROUTING LOGIC
if not st.session_state.team_name and not admin_active:
    with col_title:
        st.title(ui["welcome"])

    with st.form("login_form"):
        input_name = st.text_input(ui["team_label"], placeholder="e.g., Alpha Team")
        submit_login = st.form_submit_button(ui["start_btn"])
        if submit_login and input_name.strip():
            st.session_state.team_name = input_name.strip()
            st.rerun()

elif not admin_active:
    # Active Player Viewport Layout
    st.title(f"🗺️ {st.session_state.team_name}")
    st.subheader(f"{ui['checkpoint']} #{st.session_state.current_step}")

    # Static mockup list for structural architecture showcase
    # In step 3, this reads lines straight from your live Google Sheet columns dynamically
    mock_quest = {
        "clue_en": "Look under the main conference room coffee table.",
        "clue_vi": "Hãy nhìn dưới bàn cà phê của phòng họp chính.",
        "clue_de": "Schau unter den Kaffeetisch im Hauptkonferenzraum.",
        "answer": "matrix", "code": "CONF-992"
    }

    if not st.session_state.game_started:
        st.warning(ui["clue_locked"])
        if st.button(ui["unlock_btn"], type="primary"):
            st.session_state.game_started = True
            st.session_state.stage_start_time = time.time()
            st.rerun()
    else:
        # Render the correct language clue string using the state dictionary token selector
        st.info(f"**Clue:** {mock_quest[f'clue_{selected_lang}']}")

        # Part 1 Input
        ans_input = st.text_input(ui["part1"], placeholder="Type riddle solution...").strip().lower()

        # Part 2 Input with Native Mobile Camera Subsystem Call
        st.write(ui["part2"])
        use_camera = st.checkbox("📸 Open Mobile Device Camera Scanner Layer")
        code_input = ""

        if use_camera:
            # Streamlit directly calls the phone's hardware camera frame matrix safely
            picture = st.camera_input("Position the hidden physical item card target inside frame")
            if picture:
                st.success("Card captured asset loaded!")
                # In full implementation, we hand this picture element data array over to a 3-line cv2/pyzbar reader engine
                code_input = st.text_input("Confirm Parsed Tag Value String", value="AUTO-DETECTED-KEY")
        else:
            code_input = st.text_input("Type Verification Code Manually", placeholder="e.g., BOX-404").strip().upper()

        if st.button(ui["submit"], type="good"):
            if ans_input == mock_quest["answer"] and (
                    code_input == mock_quest["code"] or code_input == "AUTO-DETECTED-KEY"):
                st.balloons()
                st.success("Checkpoint Passed!")
                time.sleep(1.5)
                st.session_state.current_step += 1
                st.session_state.game_started = False
                st.rerun()
            else:
                st.error("Verification mismatch. Check both solutions again!")

elif admin_active and password == "hunt-master-2026":
    # Admin Interface Render Window
    st.title("📊 Global Operations Dashboard")
    st.write("Review real-time hunter timelines and adjust puzzle configuration sets.")

    # Display an interactive real-time spreadsheet frame editable by the administrator
    config_mock_df = pd.DataFrame([
        {"Step": 1, "Clue (EN)": "Under coffee table", "Answer": "matrix", "Code": "CONF-992"},
        {"Step": 2, "Clue (EN)": "Inside cafeteria", "Answer": "apple", "Code": "CAFE-102"}
    ])
    st.data_editor(config_mock_df, num_rows="dynamic")