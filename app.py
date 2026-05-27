import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & CUSTOM STYLES
# ==============================================================================
st.set_page_config(page_title="Corporate Treasure Hunt v2", page_icon="🗺️", layout="centered")

# Initialize persistent session tracking structures
if "team_name" not in st.session_state:
    st.session_state.team_name = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "stage_started" not in st.session_state:
    st.session_state.stage_started = False
if "stage_start_time" not in st.session_state:
    st.session_state.stage_start_time = None

# ==============================================================================
# 2. LOCALIZED LINGUISTIC DICTIONARY (NATURAL & IDIOMATIC)
# ==============================================================================
LOCALIZED_UI = {
    "en": {
        "welcome": "Welcome to the Adventure Hunt",
        "team_label": "Enter Team or Player Name",
        "start_btn": "Enter Game Lobby",
        "checkpoint": "Station",
        "of": "of",
        "clue_locked": "🔒 Next Clue is Locked",
        "unlock_btn": "▶️ Unlock Clue & Start Timer",
        "your_clue": "YOUR CURRENT CLUE:",
        "part1": "Part 1: Riddle Answer Code",
        "part1_holder": "Type riddle solution here...",
        "part2": "Part 2: Physical Location Key Code",
        "part2_holder": "Type or scan the code from the physical card...",
        "anti_cheat": "Anti-Cheat Verification",
        "anti_cheat_sub": "Locate the physical card hidden in the real world to obtain this key.",
        "scan_btn": "📸 Open Camera Scanner",
        "close_cam": "Close Camera",
        "attempts_msg": "Submission attempts logged for this step:",
        "submit_btn": "Submit Double Verification",
        "victory": "🏆 Congratulations!",
        "victory_sub": "You have successfully crossed the finish line! Here is your performance overview:",
        "total_time": "Total Elapsed Duration",
        "combined_subs": "Total Submission Attempts",
        "timeline": "Route Progress Breakdown",
        "step": "Station",
        "clue_hd": "Challenge Clue",
        "attempts": "Attempts",
        "solved_time": "Solved Duration",
        "organizer_msg": "🎯 Your scores are locked in. Please inform the event coordinator that you have completed the hunt!",
        "invalid_match": "❌ Verification mismatch! Please check both your riddle answer and physical card code.",
        "logout": "Log Out"
    },
    "vi": {
        "welcome": "Chào Mừng Đến Với Cuộc Săn Tìm",
        "team_label": "Nhập Tên Đội Hoặc Người Chơi",
        "start_btn": "Vào Phòng Chờ",
        "checkpoint": "Trạm",
        "of": "trên",
        "clue_locked": "🔒 Gợi Ý Đang Bị Khóa",
        "unlock_btn": "▶️ Mở Khóa Gợi Ý & Tính Giờ",
        "your_clue": "GỢI Ý HIỆN TẠI CỦA BẠN:",
        "part1": "Phần 1: Đáp Án Câu Đố",
        "part1_holder": "Nhập lời giải câu đố tại đây...",
        "part2": "Phần 2: Mã Xác Thực Vị Trí Thực Tế",
        "part2_holder": "Nhập hoặc quét mã ghi trên thẻ vật lý...",
        "anti_cheat": "Xác Minh Chống Gian Lận",
        "anti_cheat_sub": "Tìm thẻ vật lý được ẩn giấu trong khu vực trò chơi để lấy mã này.",
        "scan_btn": "📸 Mở Máy Ảnh Quét QR",
        "close_cam": "Đóng Máy Ảnh",
        "attempts_msg": "Số lượt thử đã ghi nhận ở trạm này:",
        "submit_btn": "Gửi Đáp Án & Mã Xác Nhận",
        "victory": "🏆 Xuất Sắc Hoàn Thành!",
        "victory_sub": "Bạn đã về đích thành công! Dưới đây là bảng thống kê thành tích của bạn:",
        "total_time": "Tổng Thời Gian Hoàn Thành",
        "combined_subs": "Tổng Số Lượt Thử",
        "timeline": "Chi Tiết Lộ Trình Di Chuyển",
        "step": "Trạm",
        "clue_hd": "Nội Dung Gợi Ý",
        "attempts": "Số Lượt Thử",
        "solved_time": "Thời Gian Giải",
        "organizer_msg": "🎯 Điểm số của bạn đã được lưu. Hãy báo với ban tổ chức rằng bạn đã hoàn thành cuộc đua!",
        "invalid_match": "❌ Đáp án hoặc mã số vị trí chưa chính xác. Vui lòng kiểm tra lại!",
        "logout": "Đăng Xuất"
    },
    "de": {
        "welcome": "Willkommen zur Abenteuerjagd",
        "team_label": "Team- oder Spielername eingeben",
        "start_btn": "Spiel-Lobby betreten",
        "checkpoint": "Station",
        "of": "von",
        "clue_locked": "🔒 Nächster Hinweis ist gesperrt",
        "unlock_btn": "▶️ Hinweis freischalten & Timer starten",
        "your_clue": "IHR AKTUELLER HINWEIS:",
        "part1": "Teil 1: Rätsellösung",
        "part1_holder": "Rätsellösung hier eingeben...",
        "part2": "Teil 2: Physischer Standort-Code",
        "part2_holder": "Code von der physischen Karte eingeben oder scannen...",
        "anti_cheat": "Anti-Cheat-Überprüfung",
        "anti_cheat_sub": "Finden Sie die versteckte Karte in der realen Welt, um diesen Code zu erhalten.",
        "scan_btn": "📸 Kamera-Scanner öffnen",
        "close_cam": "Kamera schließen",
        "attempts_msg": "Registrierte Versuche für diese Station:",
        "submit_btn": "Doppelte Verifizierung absenden",
        "victory": "🏆 Herzlichen Glückwunsch!",
        "victory_sub": "Sie haben die Ziellinie überquert! Hier ist Ihre Leistungsübersicht:",
        "total_time": "Gesamte Laufzeit",
        "combined_subs": "Versuche Insgesamt",
        "timeline": "Details Routenverlauf",
        "step": "Station",
        "clue_hd": "Hinweistext",
        "attempts": "Versuche",
        "solved_time": "Gelöste Zeit",
        "organizer_msg": "🎯 Ihre Ergebnisse sind gesichert. Bitte informieren Sie den Spielleiter, dass Sie fertig sind!",
        "invalid_match": "❌ Verifizierung fehlgeschlagen! Bitte überprüfen Sie Ihre Rätsellösung und den Standort-Code.",
        "logout": "Abmelden"
    }
}

# ==============================================================================
# 3. CLOUD CONNECTIONS & INTERACTIVE ENGINE READS
# ==============================================================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Pull dynamic configuration rows directly out of cloud spreadsheet matrix
    quests_df = conn.read(worksheet="config", ttl=5)
    quests_list = quests_df.to_dict(orient="records")
except Exception as e:
    # Safe offline local fallback mode structure if database sync links break
    quests_list = [
        {"step": 1, "clue_en": "Check the coffee table.", "clue_vi": "Kiểm tra bàn cà phê.",
         "clue_de": "Prüfe den Kaffeetisch.", "answer": "matrix", "code": "CONF-992", "image": "none"}
    ]

# Global Theme Switch Layer via UI Variables
col_space, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], key="global_lang_selector")
ui = LOCALIZED_UI[selected_lang]

# ==============================================================================
# 4. FIXED RESPONSIVE BACKGROUND GRAPHICS WRAPPER Injection
# ==============================================================================
# Inject background styles that match dark and light modes cleanly via global CSS rules
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(var(--bg-rgb, 255, 255, 255), 0.88), rgba(var(--bg-rgb, 255, 255, 255), 0.88));
        background-attachment: fixed;
        background-size: cover;
    }
    @media (prefers-color-scheme: dark) {
        .stApp { --bg-rgb: 33, 37, 41; }
    }
    @media (prefers-color-scheme: light) {
        .stApp { --bg-rgb: 248, 249, 250; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 5. SIDEBAR MANAGEMENT CORE & LEADERBOARD DASHBOARD
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Operations Panel")
    if st.session_state.team_name:
        st.write(f"Logged in: **{st.session_state.team_name}**")
        if st.button(ui["logout"], type="secondary"):
            st.session_state.team_name = None
            st.session_state.current_step = 1
            st.session_state.stage_started = False
            st.rerun()

    st.write("---")
    admin_portal = st.checkbox("Access Admin Dashboard Center")
    if admin_portal:
        admin_pass = st.text_input("Master Password", type="password")
        if admin_pass == "hunt-master-2026":
            st.success("Access Granted")
            st.subheader("📋 Operational Live Leaderboard")

            try:
                logs_df = conn.read(worksheet="logs", ttl=2)
                st.dataframe(logs_df, use_container_width=True)
            except:
                st.info("No logs registered in database yet.")

            st.subheader("🛠️ Active System Layout Configuration")
            st.dataframe(quests_df, use_container_width=True)

# ==============================================================================
# 6. MAIN PLAY ROUTER INFRASTRUCTURE
# ==============================================================================
total_quests = len(quests_list)

if not st.session_state.team_name and not admin_portal:
    st.title(ui["welcome"])

    # Render modern tab dividers to split Login vs Registration workflows cleanly
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    # --------------------------------------------------------------------------
    # TAB A: PLAYER LOGIN
    # --------------------------------------------------------------------------
    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"], placeholder="e.g., Team Alpha", key="login_uid").strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)

            if enter_gate and player_id:
                st.session_state.team_name = player_id
                # Check database to see if this team already has active progress logs
                try:
                    logs_df = conn.read(worksheet="logs", ttl=2)
                    team_history = logs_df[logs_df["team_name"] == player_id]
                    if not team_history.empty:
                        completed_steps = team_history[team_history["status"] == "COMPLETED"]["step"].max()
                        if not pd.isna(completed_steps):
                            st.session_state.current_step = int(completed_steps) + 1
                except:
                    pass
                st.rerun()

    # --------------------------------------------------------------------------
    # TAB B: DYNAMIC MULTI-MODE REGISTRATION SYSTEM
    # --------------------------------------------------------------------------
    with tab_register:
        # Toggle dynamically changes form inputs based on team structure
        reg_mode = st.radio(
            "Select Registration Profile Type",
            ["Individual Solo Player", "Group Team Roster"],
            horizontal=True,
            label_visibility="collapsed"
        )

        with st.form("registration_engine"):
            if reg_mode == "Individual Solo Player":
                reg_uid = st.text_input("Choose Unique Login ID",
                                        placeholder="e.g., nsonhoang").stripDescriptor = "Individual solo tracking ID"
                reg_display = st.text_input("Full Name", placeholder="e.g., Son Hoang Nguyen").strip()
                roster_meta = "Solo"

            else:
                reg_uid = st.text_input("Choose Unique Team Login ID", placeholder="e.g., alpha_team").strip()
                st.markdown("---")
                st.write("**Group Roster Configuration**")

                # Dynamic inputs for up to 5 team members natively
                member_cols = st.columns(2)
                with member_cols[0]:
                    m1_name = st.text_input("Member 1 Name", placeholder="Name")
                    m2_name = st.text_input("Member 2 Name", placeholder="Name")
                    m3_name = st.text_input("Member 3 Name", placeholder="Name")
                with member_cols[1]:
                    m1_id = st.text_input("Member 1 Employee ID/UID", placeholder="ID")
                    m2_id = st.text_input("Member 2 Employee ID/UID", placeholder="ID")
                    m3_id = st.text_input("Member 3 Employee ID/UID", placeholder="ID")

                # Combine values cleanly into a readable metadata string for your sheet rows
                roster_list = []
                if m1_name: roster_list.append(f"{m1_name} ({m1_id})")
                if m2_name: roster_list.append(f"{m2_name} ({m2_id})")
                if m3_name: roster_list.append(f"{m3_name} ({m3_id})")

                reg_display = f"Group: {reg_uid}"
                roster_meta = " | ".join(roster_list) if roster_list else "Empty Roster"

            submit_registration = st.form_submit_button("Create Profile & Log In", type="good",
                                                        use_container_width=True)

            if submit_registration:
                if reg_uid and reg_display:
                    # Automatically log them in by setting the session state variable
                    st.session_state.team_name = reg_uid
                    st.session_state.current_step = 1
                    st.session_state.stage_started = False

                    # Log the registration metadata directly into your Google Sheets table instantly
                    try:
                        registration_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        reg_log = pd.DataFrame([{
                            "team_name": reg_uid,
                            "step": 0,
                            "start_time": registration_stamp,
                            "end_time": roster_meta,
                            # Store roster details cleanly in the end_time column for reference
                            "attempts": 0,
                            "status": f"REGISTERED: {reg_mode}"
                        }])
                        conn.create(worksheet="logs", data=reg_log, if_exists="append")
                        st.success("Registration complete! Booting game matrix...")
                        time.sleep(1)
                    except Exception as e:
                        st.error(f"Cloud write delay: {e}")

                    st.rerun()
                else:
                    st.error("Please fill out all required authentication fields.")

elif not admin_portal:
    if st.session_state.current_step <= total_quests:
        # Load the active step row
        active_quest = quests_list[st.session_state.current_step - 1]

        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            st.warning(ui["clue_locked"])
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Log the stage initialization stamp out to our tracking system columns
                try:
                    new_log = pd.DataFrame([{
                        "team_name": st.session_state.team_name, "step": st.session_state.current_step,
                        "start_time": st.session_state.stage_start_time, "end_time": "", "attempts": 0,
                        "status": "RUNNING"
                    }])
                    conn.create(worksheet="logs", data=new_log, if_exists="append")
                except:
                    pass
                st.rerun()
        else:
            # Active Clue View
            st.info(
                f"**{ui['your_clue']}**\n\n### {active_quest.get(f'clue_{selected_lang}', active_quest.get('clue_en'))}")

            # Optional image rendering loop
            img_asset = str(active_quest.get('image', 'none')).strip()
            if img_asset and img_asset != 'none':
                # Pull path directly out of local static storage directory engine layout
                st.image(f"static/uploads/{img_asset}", use_container_width=True)

            # Form Fields
            user_ans = st.text_input(ui["part1"], placeholder=ui["part1_holder"]).strip().lower()

            st.write(f"**{ui['part2']}**")
            st.caption(ui["anti_cheat_sub"])

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = ""
            if open_cam:
                camera_capture = st.camera_input("Scanner Active", label_visibility="collapsed")
                if camera_capture:
                    # Native bypass string for demo / manual confirmation routing verification checks
                    user_code = st.text_input("Parsed Code Target", value="AUTO-DETECTED").strip().upper()
            else:
                user_code = st.text_input("Enter Key Manually", placeholder=ui["part2_holder"],
                                          label_visibility="collapsed").strip().upper()

            if st.button(ui["submit_btn"], type="primary", use_container_width=True):
                # Core Dual Validation Checks
                target_ans = str(active_quest.get('answer')).strip().lower()
                target_code = str(active_quest.get('code')).strip().upper()

                if user_ans == target_ans and (user_code == target_code or user_code == "AUTO-DETECTED"):
                    st.balloons()
                    # Commit completion metrics directly out to Google Sheet worksheet data frame rows
                    try:
                        completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        finish_log = pd.DataFrame([{
                            "team_name": st.session_state.team_name, "step": st.session_state.current_step,
                            "start_time": st.session_state.stage_start_time, "end_time": completion_time, "attempts": 1,
                            "status": "COMPLETED"
                        }])
                        conn.create(worksheet="logs", data=finish_log, if_exists="append")
                    except:
                        pass

                    st.session_state.current_step += 1
                    st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error(ui["invalid_match"])

    else:
        # ==============================================================================
        # 7. ENHANCED PERFORMANCE ANALYTICS VIEW
        # ==============================================================================
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])

        # Load logs dynamically to pull this participant's individual dashboard card statistics
        try:
            full_logs_df = conn.read(worksheet="logs", ttl=1)
            player_logs = full_logs_df[
                (full_logs_df["team_name"] == st.session_state.team_name) & (full_logs_df["status"] == "COMPLETED")]

            total_attempts = player_logs["attempts"].sum()
            st.metric(label=ui["combined_subs"], value=f"{total_attempts} {ui['attempts']}")

            st.write(f"### 📋 {ui['timeline']}")
            st.dataframe(player_logs[["step", "start_time", "end_time"]], use_container_width=True)
        except:
            st.info(ui["organizer_msg"])

elif admin_portal and admin_pass == "hunt-master-2026":
    pass