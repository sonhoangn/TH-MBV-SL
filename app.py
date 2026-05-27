import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & SYSTEM CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="MBV 140Y Treasure Hunt", page_icon="🗺️", layout="centered")

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

# 🖼️ Mercedes-Benz 140Y Corporate Asset Background
BG_URL = "https://group.mercedes-benz.com/bilder/innovationen/specials/140-years-of-innovation/140-years-of-innovation-visual-3-2-w1680xh945-cutout.jpg"

# ==============================================================================
# 2. TARGET DATABASE CREDENTIAL CONFIGURATION
# ==============================================================================
SHEET_ID = "1zcsOhwx9L3-B7D2l4T5oZCZkxlw-Rd9YiUh0gXidG2Y"

#
FORM_URL = "https://docs.google.com/forms/d/18LuS6HSdv8UUEAKWwjwc0RdnGrg2mtn2lOuH6cFs6Lo/formResponse"

# Mapping keys to match your Form field entry components
FORM_ENTRIES = {
    "team_name": "entry.2043334045",
    "step": "entry.353841835",
    "start_time": "entry.426777136",
    "end_time": "entry.2116062077",
    "attempts": "entry.616482534",
    "status": "entry.970564586"
}

# ==============================================================================
# 3. DIRECT BULLETPROOF WRITE PIPELINE
# ==============================================================================
def push_log_to_cloud(team, step, start, end, attempts, status):
    """Sends log telemetry straight to Google Sheets via native web requests"""
    payload = {
        FORM_ENTRIES["team_name"]: str(team),
        FORM_ENTRIES["step"]: str(step),
        FORM_ENTRIES["start_time"]: str(start),
        FORM_ENTRIES["end_time"]: str(end),
        FORM_ENTRIES["attempts"]: str(attempts),
        FORM_ENTRIES["status"]: str(status)
    }
    try:
        # 🛡️ Point verify to your corporate root certificate file
        response = requests.post(
            FORM_URL,
            data=payload,
            timeout=5,
            verify="corp_root.crt"
        )
        print(f"Form submission response: {response.status_code}")
    except Exception as e:
        print(f"Network request failed: {e}")

# ==============================================================================
# 4. LIGHTWEIGHT LIVE CONFIG FETCH
# ==============================================================================
try:
    config_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=config"
    quests_df = pd.read_csv(config_url)
    quests_list = quests_df.to_dict(orient="records")
except Exception as e:
    quests_list = [
        {"step": 1, "clue_en": "Check the coffee table.", "clue_vi": "Kiểm tra bàn cà phê.",
         "clue_de": "Prüfe den Kaffeetisch.", "code": "CONF-992", "image_url": ""}
    ]

# ==============================================================================
# 5. LOCALIZED LINGUISTIC DICTIONARY (TRILINGUAL SUITE)
# ==============================================================================
LOCALIZED_UI = {
    "en": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Enter Team or Player Name",
        "start_btn": "Enter Game Lobby", "checkpoint": "Station", "of": "of",
        "clue_locked": "🔒 Next Clue is Locked", "unlock_btn": "▶️ Unlock Clue & Start Timer",
        "your_clue": "YOUR CURRENT CLUE:", "part2": "Verification Code Key",
        "part2_holder": "Scan QR code or type key here...", "anti_cheat_sub": "Find the hidden QR code station.",
        "scan_btn": "📸 Open QR Camera Scanner", "submit_btn": "Verify Location Key",
        "victory": "🏆 Congratulations!", "victory_sub": "You have successfully crossed the finish line!",
        "combined_subs": "Total Submission Attempts", "timeline": "Route Progress Breakdown", "attempts": "Attempts",
        "organizer_msg": "🎯 Your scores are locked in. Please inform the coordinator!",
        "invalid_match": "❌ Incorrect verification code! Please try again.", "logout": "Log Out"
    },
    "vi": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Nhập Tên Đội / Người chơi",
        "start_btn": "Vào Phòng Chờ", "checkpoint": "Trạm", "of": "trên",
        "clue_locked": "🔒 Gợi Ý Đang Bị Khóa", "unlock_btn": "▶️ Mở Khóa Gợi Ý & Tính Giờ",
        "your_clue": "GỢI Ý HIỆN TẠI CỦA BẠN:", "part2": "Mã Số Xác Thực Trạm",
        "part2_holder": "Nhập mã trạm tại đây...", "anti_cheat_sub": "Tìm trạm QR được ẩn giấu thực tế.",
        "scan_btn": "📸 Mở Máy Ảnh Quét QR", "submit_btn": "Xác Thực Lộ Trình",
        "victory": "🏆 Xuất Sắc Hoàn Thành!",
        "victory_sub": "Bạn đã về đích thành công! Dưới đây là thành tích của bạn:",
        "combined_subs": "Tổng Số Lượt Thử", "timeline": "Chi Tiết Lộ Trình Di Chuyển", "attempts": "Số Lượt Thử",
        "organizer_msg": "🎯 Điểm số đã được lưu. Hãy báo với ban tổ chức!",
        "invalid_match": "❌ Mã xác thực chưa chính xác. Vui lòng kiểm tra lại!", "logout": "Đăng Xuất"
    },
    "de": {
        "welcome": "Mercedes-Benz Vietnam 140Y Jubiläums-Schnitzeljagd",
        "team_label": "Team- oder Spielername eingeben",
        "start_btn": "Spiel-Lobby betreten", "checkpoint": "Station", "of": "von",
        "clue_locked": "🔒 Nächster Hinweis ist gesperrt", "unlock_btn": "▶️ Hinweis freischalten & Timer starten",
        "your_clue": "IHR AKTUELLER HINWEIS:", "part2": "Verifizierungscode",
        "part2_holder": "QR-Code scannen oder Code hier eingeben...",
        "anti_cheat_sub": "Finden Sie die versteckte QR-Code-Station.",
        "scan_btn": "📸 QR-Code Kamera-Scanner öffnen", "submit_btn": "Code verifizieren",
        "victory": "🏆 Herzlichen Glückwunsch!", "victory_sub": "Sie haben die Ziellinie erfolgreich überquert!",
        "combined_subs": "Versuche Insgesamt", "timeline": "Details Routenverlauf", "attempts": "Versuche",
        "organizer_msg": "🎯 Ihre Ergebnisse sind gesichert. Bitte Spielleiter informieren!",
        "invalid_match": "❌ Falscher Code! Bitte überprüfen Sie Ihre Eingabe.", "logout": "Abmelden"
    }
}

# Language Setup Selection Row layout
col_space, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], key="global_lang_selector")
ui = LOCALIZED_UI[selected_lang]

# ==============================================================================
# 6. RESTORED PREMIUM DESIGN SCHEME (DARK/LIGHT THEME ADAPTIVE)
# ==============================================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(var(--bg-rgb, 255, 255, 255), 0.88), rgba(var(--bg-rgb, 255, 255, 255), 0.88)), 
                    url("{BG_URL}");
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
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 7. SIDEBAR MANAGEMENT PANEL
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Operations Panel")
    if st.session_state.team_name:
        st.write(f"Logged in as: **{st.session_state.team_name}**")
        if st.button(ui["logout"], type="secondary"):
            st.session_state.team_name = None
            st.session_state.current_step = 1
            st.session_state.stage_started = False
            st.rerun()

# ==============================================================================
# 8. GLOBAL ROUTING PIPELINE ENGINE
# ==============================================================================
total_quests = len(quests_list)

# ROUTE 1: FULL ADMIN OPERATIONS SUITE RESTORED
if st.session_state.admin_override:
    st.title("📊 Global Operations Dashboard")

    if st.button("⬅️ Exit Admin Dashboard & Return to Lobby", type="secondary", use_container_width=True):
        st.session_state.admin_override = False
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Operational Live Leaderboard logs")
    try:
        logs_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
        st.dataframe(pd.read_csv(logs_url), use_container_width=True)
    except:
        st.info("No logs registered in database yet.")

    st.subheader("🛠️ Active System Layout Configuration (Questions list)")
    if 'quests_df' in locals() or 'quests_df' in globals():
        st.dataframe(quests_df, use_container_width=True)

# ROUTE 2: PLAYER ACCESS GATE / ACCESS LOBBY
elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"]).strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)
            if enter_gate and player_id:
                st.session_state.team_name = player_id
                try:
                    logs_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
                    history = pd.read_csv(logs_url)
                    team_history = history[history["team_name"] == player_id]
                    if not team_history.empty:
                        completed_steps = team_history[team_history["status"] == "COMPLETED"]["step"].max()
                        if not pd.isna(completed_steps):
                            st.session_state.current_step = int(completed_steps) + 1
                except:
                    pass
                st.rerun()

    with tab_register:
        with st.form("registration_engine"):
            reg_uid = st.text_input("Choose Unique Team Login ID (No spaces)").strip()
            reg_meta = st.text_input("Player Names / Notes")
            submit_registration = st.form_submit_button("Create Profile & Log In", type="primary",
                                                        use_container_width=True)
            if submit_registration and reg_uid:
                st.session_state.team_name = reg_uid
                st.session_state.current_step = 1
                st.session_state.stage_started = False

                # Register team profile response line row to sheet matrix via form engine
                push_log_to_cloud(reg_meta, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reg_meta, 0, "REGISTERED")

                st.success("Profile initialized online!")
                time.sleep(0.5)
                st.rerun()

    # System console wrapper anchored neatly below landing modules
    st.markdown("---")
    col_left, col_right = st.columns([3, 1])
    with col_right:
        with st.expander("🛠️ System Console"):
            admin_pass = st.text_input("Master Password", type="password", key="main_admin_pass")
            if admin_pass == st.secrets["admin_password"]:
                st.session_state.admin_override = True
                st.rerun()

# ROUTE 3: GAMEPLAY ENGINE LAYOUT PIPELINE
else:
    if st.session_state.current_step <= total_quests:
        active_quest = quests_list[st.session_state.current_step - 1]
        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            st.warning(ui["clue_locked"])
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Push execution timestamp trace string
                push_log_to_cloud(st.session_state.team_name, st.session_state.current_step,
                                  st.session_state.stage_start_time, "", 0, "RUNNING")
                st.rerun()
        else:
            # Multi-language tracking lookups for clue tabs (Fallback sequence: Selected -> EN)
            current_clue_text = active_quest.get(f'clue_{selected_lang}', active_quest.get('clue_en'))
            st.info(f"**{ui['your_clue']}**\n\n### {current_clue_text}")

            # Inline Clue Image Renders
            clue_img = str(active_quest.get('image_url', '')).strip()
            if clue_img and clue_img != "nan" and clue_img != "":
                st.image(clue_img, use_container_width=True)

            st.write(f"### 🔑 {ui['part2']}")
            st.caption(ui["anti_cheat_sub"])

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = ""
            if open_cam:
                camera_capture = st.camera_input("Scanner Active", label_visibility="collapsed")
                if camera_capture:
                    user_code = "AUTO-DETECTED"
            else:
                user_code = st.text_input("Enter Code Manually", placeholder=ui["part2_holder"],
                                          label_visibility="collapsed").strip().upper()

            if st.button(ui["submit_btn"], type="primary", use_container_width=True):
                target_code = str(active_quest.get('code')).strip().upper()

                if str(user_code).strip().upper() == target_code or user_code == "AUTO-DETECTED":
                    st.balloons()

                    push_log_to_cloud(st.session_state.team_name, st.session_state.current_step,
                                      st.session_state.stage_start_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                      1, "COMPLETED")

                    st.session_state.current_step += 1
                    st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error(ui["invalid_match"])
    else:
        # Victory screen timeline metric layout block
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])
        try:
            logs_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=logs"
            full_logs_df = pd.read_csv(logs_url)

            player_logs = full_logs_df[full_logs_df["team_name"] == st.session_state.team_name].copy()
            completed_stages = player_logs[player_logs["status"] == "COMPLETED"].copy()

            if not completed_stages.empty:
                completed_stages["attempts"] = pd.to_numeric(completed_stages["attempts"], errors="coerce").fillna(1)
                completed_stages["step"] = pd.to_numeric(completed_stages["step"], errors="coerce").astype(int)

                total_attempts = int(completed_stages["attempts"].sum())
                st.metric(label=ui["combined_subs"], value=f"{total_attempts} {ui['attempts']}")

                completed_stages["start_time"] = pd.to_datetime(completed_stages["start_time"], errors="coerce")
                completed_stages["end_time"] = pd.to_datetime(completed_stages["end_time"], errors="coerce")

                completed_stages["Duration"] = (completed_stages["end_time"] - completed_stages[
                    "start_time"]).dt.total_seconds() / 60
                completed_stages["Duration"] = completed_stages["Duration"].round(1).astype(str) + " min"

                completed_stages["Unlocked At"] = completed_stages["start_time"].dt.strftime("%H:%M:%S")
                completed_stages["Verified At"] = completed_stages["end_time"].dt.strftime("%H:%M:%S")

                st.write(f"### 📋 {ui['timeline']}")
                display_board = completed_stages[["step", "Unlocked At", "Verified At", "Duration"]].rename(
                    columns={"step": "Station Step"})
                st.dataframe(display_board.sort_values(by="Station Step"), use_container_width=True, hide_index=True)
            else:
                st.info(ui["organizer_msg"])
        except:
            st.info(ui["organizer_msg"])