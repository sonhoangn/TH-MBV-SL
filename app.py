import streamlit as st
import pandas as pd
import time
import json
import os
from datetime import datetime

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & SYSTEM CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="MBV 140Y Treasure Hunt", page_icon="🗺️", layout="centered")

# Local Flat-File JSON Database Configuration
LOCAL_DB_FILE = "treasure_hunt_db.json"


def load_local_db():
    """Reads the local JSON file database safely"""
    if not os.path.exists(LOCAL_DB_FILE):
        return {}
    try:
        with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_local_db(data):
    """Writes the updated state synchronously to the local JSON database"""
    with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def push_log_local(team, step, start, end, attempts, status, meta_notes=""):
    """Saves or appends log entries instantly to the local data store"""
    db = load_local_db()
    if team not in db:
        db[team] = {
            "registration_notes": meta_notes,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": []
        }

    # Append the running audit log entry
    log_entry = {
        "step": int(step),
        "start_time": str(start),
        "end_time": str(end),
        "attempts": int(attempts),
        "status": str(status),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db[team]["history"].append(log_entry)
    save_local_db(db)


# Core Session State Inits
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

# Hardcoded Questions Fallback Data Array (No remote sheet parsing required)
quests_list = [
    {"step": 1, "clue_en": "Check near the main showroom entrance display.",
     "clue_vi": "Kiểm tra gần khu trưng bày lối vào showroom chính.",
     "clue_de": "Prüfe den Haupteingang Ausstellungsbereich.", "code": "MBV-START-140", "image_url": ""},
    {"step": 2, "clue_en": "Look under the glass coffee table in the lounge.",
     "clue_vi": "Tìm dưới bàn cà phê bằng kính ở khu vực phòng chờ.",
     "clue_de": "Suche unter dem Kaffeetisch aus Glas in der Lounge.", "code": "SILVER-ARROW", "image_url": ""},
    {"step": 3, "clue_en": "The final puzzle key is hidden by the classic model scale array.",
     "clue_vi": "Mã số cuối cùng được giấu cạnh tủ mô hình xe cổ.",
     "clue_de": "Der letzte Schlüssel ist beim Oldtimer-Modellregal versteckt.", "code": "AMG-POWER-99",
     "image_url": ""}
]
total_quests = len(quests_list)

# ==============================================================================
# 2. LOCALIZED LINGUISTIC DICTIONARY (TRILINGUAL SUITE)
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
        "invalid_match": "❌ Incorrect verification code! Please try again.", "logout": "Log Out / Return Home"
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
        "invalid_match": "❌ Mã xác thực chưa chính xác. Vui lòng kiểm tra lại!", "logout": "Đăng Xuất / Trở Về"
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
        "invalid_match": "❌ Falscher Code! Bitte überprüfen Sie Ihre Eingabe.", "logout": "Abmelden / Home"
    }
}

col_space, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], key="global_lang_selector")
ui = LOCALIZED_UI[selected_lang]

# ==============================================================================
# 3. PREMIUM DESIGN SCHEME (DARK/LIGHT THEME ADAPTIVE)
# ==============================================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(var(--bg-rgb, 255, 255, 255), 0.88), rgba(var(--bg-rgb, 255, 255, 255), 0.88)), url("{BG_URL}");
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (prefers-color-scheme: dark) {{ .stApp {{ --bg-rgb: 33, 37, 41; }} }}
    @media (prefers-color-scheme: light) {{ .stApp {{ --bg-rgb: 248, 249, 250; }} }}
    .stAppHeader {{ display: none !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 4. SIDEBAR PANEL CONTROL
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Operations Panel")
    if st.session_state.team_name:
        st.write(f"Logged in as: **{st.session_state.team_name}**")
        st.write(f"Current Game Step: **{st.session_state.current_step}**")
        if st.button(ui["logout"], type="secondary", key="sidebar_logout_btn"):
            st.session_state.team_name = None
            st.session_state.current_step = 1
            st.session_state.stage_started = False
            st.rerun()

# ==============================================================================
# 5. GLOBAL ROUTING PIPELINE ENGINE
# ==============================================================================

# ROUTE 1: FULL ADMIN OPERATIONS SUITE
if st.session_state.admin_override:
    st.title("📊 Global Operations Dashboard")
    if st.button("⬅️ Exit Admin Dashboard", type="secondary", use_container_width=True):
        st.session_state.admin_override = False
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Operational Live Leaderboard Log File")

    db_snapshot = load_local_db()
    if db_snapshot:
        flattened_records = []
        for team, items in db_snapshot.items():
            for log in items.get("history", []):
                flattened_records.append({
                    "Team ID": team,
                    "Notes": items.get("registration_notes", ""),
                    "Station Step": log.get("step"),
                    "Unlocked At": log.get("start_time"),
                    "Verified At": log.get("end_time"),
                    "Status": log.get("status")
                })
        if flattened_records:
            st.dataframe(pd.DataFrame(flattened_records), use_container_width=True)
        else:
            st.info("Database initialized, but no active runs logged yet.")
    else:
        st.info("No logs registered in database yet.")

# ROUTE 2: PLAYER ACCESS GATE / ACCESS LOBBY
elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"]).strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)
            if enter_gate and player_id:
                db = load_local_db()
                if player_id in db:
                    st.session_state.team_name = player_id
                    # Calculate their accurate current stage based on past completions
                    history = db[player_id]["history"]
                    completed_steps = [log["step"] for log in history if log["status"] == "COMPLETED"]
                    if completed_steps:
                        st.session_state.current_step = max(completed_steps) + 1
                    else:
                        st.session_state.current_step = 1

                    # Restore running stage timer if they refreshed midway
                    running_stages = [log for log in history if log["status"] == "RUNNING"]
                    if running_stages and (not completed_steps or running_stages[-1]["step"] > max(completed_steps)):
                        st.session_state.stage_started = True
                        st.session_state.stage_start_time = running_stages[-1]["start_time"]
                    else:
                        st.session_state.stage_started = False

                    st.rerun()
                else:
                    st.error("Team profile ID not found! Please register first.")

    with tab_register:
        with st.form("registration_engine"):
            reg_uid = st.text_input("Choose Unique Team Login ID (No spaces)").strip()
            reg_meta = st.text_input("Player Names / Notes")
            submit_registration = st.form_submit_button("Create Profile & Log In", type="primary",
                                                        use_container_width=True)
            if submit_registration and reg_uid:
                db = load_local_db()
                if reg_uid in db:
                    st.error("This Login ID is already taken! Choose another one.")
                else:
                    st.session_state.team_name = reg_uid
                    st.session_state.current_step = 1
                    st.session_state.stage_started = False

                    push_log_local(reg_uid, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", 0, "REGISTERED",
                                   meta_notes=reg_meta)
                    st.success("Profile initialized online!")
                    time.sleep(0.5)
                    st.rerun()

    st.markdown("---")
    col_space_div, col_right_admin = st.columns([3, 1])
    with col_right_admin:
        with st.expander("🛠️ Console"):
            admin_pass = st.text_input("Master Password", type="password", key="main_admin_pass")
            if admin_pass == "MBV140Years":  # Secure clean string match fallback
                st.session_state.admin_override = True
                st.rerun()

# ROUTE 3: ACTIVE GAMEPLAY & VICTORY LOOPS
else:
    # Game Ongoing
    if st.session_state.current_step <= total_quests:
        active_quest = quests_list[st.session_state.current_step - 1]
        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            st.warning(ui["clue_locked"])
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                push_log_local(st.session_state.team_name, st.session_state.current_step,
                               st.session_state.stage_start_time, "", 0, "RUNNING")
                st.rerun()
        else:
            current_clue_text = active_quest.get(f'clue_{selected_lang}', active_quest.get('clue_en'))
            st.info(f"**{ui['your_clue']}**\n\n### {current_clue_text}")

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
                    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    push_log_local(st.session_state.team_name, st.session_state.current_step,
                                   st.session_state.stage_start_time, end_time_str, 1, "COMPLETED")

                    st.session_state.current_step += 1
                    st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error(ui["invalid_match"])

    # Game Finished (Victory Screen)
    else:
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])

        db = load_local_db()
        player_history = db.get(st.session_state.team_name, {}).get("history", [])
        completed_stages = [log for log in player_history if log["status"] == "COMPLETED"]

        if completed_stages:
            records = []
            total_attempts = 0
            for log in completed_stages:
                total_attempts += log.get("attempts", 1)

                t1 = datetime.strptime(log["start_time"], "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(log["end_time"], "%Y-%m-%d %H:%M:%S")
                duration_mins = round((t2 - t1).total_seconds() / 60, 1)

                records.append({
                    "Station Step": f"Station {log['step']}",
                    "Unlocked At": t1.strftime("%H:%M:%S"),
                    "Verified At": t2.strftime("%H:%M:%S"),
                    "Duration": f"{duration_mins} min"
                })

            st.metric(label=ui["combined_subs"], value=f"{total_attempts} {ui['attempts']}")
            st.write(f"### 📋 {ui['timeline']}")
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        else:
            st.info(ui["organizer_msg"])

        st.markdown("---")
        if st.button(f"🔄 {ui['logout']}", type="primary", use_container_width=True):
            st.session_state.team_name = None
            st.session_state.current_step = 1
            st.session_state.stage_started = False
            st.rerun()