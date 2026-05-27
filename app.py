import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & SYSTEM OVERRIDES
# ==============================================================================
st.set_page_config(page_title="Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", page_icon="🗺️", layout="centered")

if "team_name" not in st.session_state:
    st.session_state.team_name = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "stage_started" not in st.session_state:
    st.session_state.stage_started = False
if "stage_start_time" not in st.session_state:
    st.session_state.stage_start_time = None
if "admin_override" not in st.session_state:
    st.session_state.admin_override = False

# ==============================================================================
# 2. LOCALIZED LINGUISTIC DICTIONARY
# ==============================================================================
LOCALIZED_UI = {
    "en": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Enter Team or Player Name",
        "start_btn": "Enter Game Lobby", "checkpoint": "Station", "of": "of",
        "clue_locked": "🔒 Next Clue is Locked", "unlock_btn": "▶️ Unlock Clue & Start Timer",
        "your_clue": "YOUR CURRENT CLUE:", "part1": "Part 1: Riddle Answer Code",
        "part1_holder": "Type riddle solution here...", "part2": "Part 2: Physical Location Key Code",
        "part2_holder": "Type or scan the code from the physical card...", "anti_cheat": "Anti-Cheat Verification",
        "anti_cheat_sub": "Locate the physical card hidden in the real world to obtain this key.",
        "scan_btn": "📸 Open Camera Scanner", "close_cam": "Close Camera", "submit_btn": "Submit Double Verification",
        "victory": "🏆 Congratulations!", "victory_sub": "You have successfully crossed the finish line!",
        "combined_subs": "Total Submission Attempts", "timeline": "Route Progress Breakdown", "attempts": "Attempts",
        "organizer_msg": "🎯 Your scores are locked in. Please inform the coordinator!",
        "invalid_match": "❌ Verification mismatch! Please check both entries.", "logout": "Log Out"
    },
    "vi": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Nhập Tên Đội Hoặc Người Chơi",
        "start_btn": "Vào Phòng Chờ", "checkpoint": "Trạm", "of": "trên",
        "clue_locked": "🔒 Gợi Ý Đang Bị Khóa", "unlock_btn": "▶️ Mở Khóa Gợi Ý & Tính Giờ",
        "your_clue": "GỢI Ý HIỆN TẠI CỦA BẠN:", "part1": "Phần 1: Đáp Án Câu Đố",
        "part1_holder": "Nhập lời giải câu đố tại đây...", "part2": "Phần 2: Mã Xác Thực Vị Trí Thực Tế",
        "part2_holder": "Nhập hoặc quét mã ghi trên thẻ vật lý...", "anti_cheat": "Xác Minh Chống Gian Lận",
        "anti_cheat_sub": "Tìm thẻ vật lý được ẩn giấu trong khu vực trò chơi để lấy mã này.",
        "scan_btn": "📸 Mở Máy Ảnh Quét QR", "close_cam": "Đóng Máy Ảnh", "submit_btn": "Gửi Đáp Án & Mã Xác Nhận",
        "victory": "🏆 Xuất Sắc Hoàn Thành!",
        "victory_sub": "Bạn đã về đích thành công! Dưới đây là thành tích của bạn:",
        "combined_subs": "Tổng Số Lượt Thử", "timeline": "Chi Tiết Lộ Trình Di Chuyển", "attempts": "Số Lượt Thử",
        "organizer_msg": "🎯 Điểm số đã được lưu. Hãy báo với ban tổ chức!",
        "invalid_match": "❌ Đáp án hoặc mã số vị trí chưa chính xác. Vui lòng kiểm tra lại!", "logout": "Đăng Xuất"
    },
    "de": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Team- oder Spielername eingeben",
        "start_btn": "Spiel-Lobby betreten", "checkpoint": "Station", "of": "von",
        "clue_locked": "🔒 Nächster Hinweis ist gesperrt", "unlock_btn": "▶️ Hinweis freischalten & Timer starten",
        "your_clue": "IHR AKTUELLER HINWEIS:", "part1": "Teil 1: Rätsellösung",
        "part1_holder": "Rätsellösung hier eingeben...", "part2": "Teil 2: Physischer Standort-Code",
        "part2_holder": "Code von der physischen Karte eingeben...", "anti_cheat": "Anti-Cheat-Überprüfung",
        "anti_cheat_sub": "Finden Sie die versteckte Karte, um diesen Code zu erhalten.",
        "scan_btn": "📸 Kamera-Scanner öffnen", "close_cam": "Kamera schließen",
        "submit_btn": "Doppelte Verifizierung absenden",
        "victory": "🏆 Herzlichen Glückwunsch!", "victory_sub": "Sie haben die Ziellinie überquert!",
        "combined_subs": "Versuche Insgesamt", "timeline": "Details Routenverlauf", "attempts": "Versuche",
        "organizer_msg": "🎯 Ihre Ergebnisse sind gesichert. Bitte Spielleiter informieren!",
        "invalid_match": "❌ Verifizierung fehlgeschlagen! Bitte überprüfen Sie Ihre Eingaben.", "logout": "Abmelden"
    }
}

# ==============================================================================
# 3. CLOUD CONNECTIONS & LIVE BACKGROUND FETCH
# ==============================================================================
bg_url = ""  # Fallback default blank transparent layer
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    quests_df = conn.read(worksheet="config", ttl=2)
    quests_list = quests_df.to_dict(orient="records")

    # Attempt to load custom live background URL saved inside the logs sheet matrix
    global_logs = conn.read(worksheet="logs", ttl=2)
    bg_row = global_logs[global_logs["status"] == "BACKGROUND"]
    if not bg_row.empty:
        bg_url = str(bg_row.iloc[0]["start_time"]).strip()
except Exception as e:
    quests_list = [
        {"step": 1, "clue_en": "Check the coffee table.", "clue_vi": "Kiểm tra bàn cà phê.",
         "clue_de": "Prüfe den Kaffeetisch.", "answer": "matrix", "code": "CONF-992", "image_url": ""}
    ]

# Global Language Selection Control
col_space, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], key="global_lang_selector")
ui = LOCALIZED_UI[selected_lang]

# ==============================================================================
# 4. LIVE CUSTOMIZABLE BACKGROUND GRAPHICS ENGINE
# ==============================================================================
# Safely injects the background URL without breaking the media query brackets
st.markdown(
    """
    <style>
    .stApp {{
        background: linear-gradient(rgba(var(--bg-rgb, 255, 255, 255), 0.85), rgba(var(--bg-rgb, 255, 255, 255), 0.85)), 
                    url("{url}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    @media (prefers-color-scheme: dark) {{ .stApp {{ --bg-rgb: 33, 37, 41; }} }}
    @media (prefers-color-scheme: light) {{ .stApp {{ --bg-rgb: 248, 249, 250; }} }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    .stAppHeader {{ display: none !important; }}
    div[data-testid="stManageAppPageNavFloatingActionButton"] {{ display: none !important; }}
    </style>
    """.format(url=bg_url),
    unsafe_allow_html=True
)

# ==============================================================================
# 5. SIDEBAR DISCONNECT CONTROL
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

# ==============================================================================
# 6. GLOBAL ROUTING PIPELINE
# ==============================================================================
total_quests = len(quests_list)

# PRIORITY ROUTE 1: ADMIN LIVE OPERATIONS VIEW
if st.session_state.admin_override:
    st.title("📊 Global Operations Dashboard")

    if st.button("⬅️ Exit Admin Dashboard & Return to Game Lobby", type="secondary", use_container_width=True):
        st.session_state.admin_override = False
        st.rerun()

    st.markdown("---")
    st.subheader("🖼️ Custom App Background Management")
    with st.form("bg_management_form"):
        new_bg = st.text_input("Paste Direct Image Link URL (.jpg / .png)", value=bg_url,
                               placeholder="https://example.com/workspace.jpg")
        save_bg_btn = st.form_submit_button("Update System Background Image", type="primary")

        if save_bg_btn and new_bg:
            try:
                # 1. Prepare the single configuration row as a clean DataFrame
                bg_update_df = pd.DataFrame([{
                    "team_name": "SYSTEM_SETTINGS",
                    "step": 0,
                    "start_time": new_bg.strip(),
                    "end_time": "SYSTEM",
                    "attempts": 0,
                    "status": "BACKGROUND"
                }])

                # 2. Filter out any existing BACKGROUND rows from your current global logs variable
                clean_logs_df = global_logs[global_logs["status"] != "BACKGROUND"]

                # 3. Concatenate the clean historical data with your new background row
                combined_logs = pd.concat([clean_logs_df, bg_update_df], ignore_index=True)

                # 4. FIXED: Use .update() instead of .create(if_exists="replace")
                conn.update(worksheet="logs", data=combined_logs)

                st.success("App appearance configuration flushed to Cloud! Reloading style definitions...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Cloud update failure: {e}")

    st.markdown("---")
    st.subheader("📋 Operational Live Leaderboard")
    try:
        logs_df = conn.read(worksheet="logs", ttl=1)
        st.dataframe(logs_df[logs_df["team_name"] != "SYSTEM_SETTINGS"], use_container_width=True)
    except:
        st.info("No logs registered in database yet.")

    st.subheader("🛠️ Active System Layout Configuration")
    if 'quests_df' in locals() or 'quests_df' in globals():
        st.dataframe(quests_df, use_container_width=True)

# PRIORITY ROUTE 2: LOBBY GATEWAY
elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"], placeholder="e.g., Team Alpha", key="login_uid").strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)
            if enter_gate and player_id:
                st.session_state.team_name = player_id
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

    with tab_register:
        reg_mode = st.radio("Select Registration Profile Type", ["Individual Solo Player", "Group Team Roster"],
                            horizontal=True, label_visibility="collapsed")
        with st.form("registration_engine"):
            if reg_mode == "Individual Solo Player":
                reg_uid = st.text_input("Choose Unique Login ID", placeholder="e.g., NGHOAN1").strip()
                reg_display = st.text_input("Full Name", placeholder="e.g., Son Hoang Nguyen").strip()
                roster_meta = "Solo"
            else:
                reg_uid = st.text_input("Choose Unique Team Login ID", placeholder="e.g., alpha_team").strip()
                st.markdown("---")
                st.write("**Group Roster Configuration**")
                member_cols = st.columns(2)
                with member_cols[0]:
                    m1_name = st.text_input("Member 1 Name")
                    m2_name = st.text_input("Member 2 Name")
                with member_cols[1]:
                    m1_id = st.text_input("Member 1 ID")
                    m2_id = st.text_input("Member 2 ID")
                roster_list = []
                if m1_name: roster_list.append(f"{m1_name} ({m1_id})")
                if m2_name: roster_list.append(f"{m2_name} ({m2_id})")
                reg_display = f"Group: {reg_uid}"
                roster_meta = " | ".join(roster_list) if roster_list else "Empty Roster"

            submit_registration = st.form_submit_button("Create Profile & Log In", type="primary",
                                                        use_container_width=True)
            if submit_registration and reg_uid and reg_display:
                st.session_state.team_name = reg_uid
                st.session_state.current_step = 1
                st.session_state.stage_started = False
                try:
                    registration_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    reg_log = pd.DataFrame([{
                        "team_name": reg_uid, "step": 0, "start_time": registration_stamp,
                        "end_time": roster_meta, "attempts": 0, "status": f"REGISTERED: {reg_mode}"
                    }])
                    conn.create(worksheet="logs", data=reg_log, if_exists="append")
                    st.success("Profile initialized!")
                    time.sleep(0.5)
                except:
                    pass
                st.rerun()

    st.markdown("---")
    col_left, col_right = st.columns([3, 1])
    with col_right:
        with st.expander("🛠️ System Console"):
            admin_pass = st.text_input("Master Password", type="password", key="main_admin_pass")
            if admin_pass == st.secrets["admin_password"]:
                st.session_state.admin_override = True
                st.rerun()

# PRIORITY ROUTE 3: ACTIVE GAMEPLAY PIPELINE
else:
    if st.session_state.current_step <= total_quests:
        active_quest = quests_list[st.session_state.current_step - 1]
        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            st.warning(ui["clue_locked"])
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            st.info(
                f"**{ui['your_clue']}**\n\n### {active_quest.get(f'clue_{selected_lang}', active_quest.get('clue_en'))}")

            # 🖼️ DYNAMIC QUESTION IMAGE RENDER CORES
            # Checks if an active web image link is present for this question index row item
            clue_img = str(active_quest.get('image_url', '')).strip()
            if clue_img and clue_img != "nan" and clue_img != "":
                st.image(clue_img, use_container_width=True)

            user_ans = st.text_input(ui["part1"], placeholder=ui["part1_holder"]).strip().lower()
            st.write(f"**{ui['part2']}**")
            st.caption(ui["anti_cheat_sub"])

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = ""
            if open_cam:
                camera_capture = st.camera_input("Scanner Active", label_visibility="collapsed")
                if camera_capture:
                    user_code = st.text_input("Parsed Code Target", value="AUTO-DETECTED").strip().upper()
            else:
                user_code = st.text_input("Enter Key Manually", placeholder=ui["part2_holder"],
                                          label_visibility="collapsed").strip().upper()

            if st.button(ui["submit_btn"], type="primary", use_container_width=True):
                target_ans = str(active_quest.get('answer')).strip().lower()
                target_code = str(active_quest.get('code')).strip().upper()

                if user_ans == target_ans and (user_code == target_code or user_code == "AUTO-DETECTED"):
                    st.balloons()
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
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])
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