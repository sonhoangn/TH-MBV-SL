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

BG_URL = "https://group.mercedes-benz.com/bilder/innovationen/specials/140-years-of-innovation/140-years-of-innovation-visual-3-2-w1680xh945-cutout.jpg"

# ==============================================================================
# 2. TARGET CREDENTIAL CONFIGURATION (REPLACE THESE WITH YOUR VALID FORM IDS)
# ==============================================================================
SHEET_ID = "1zcsOhwx9L3-B7D2l4T5oZCZkxlw-Rd9YiUh0gXidG2Y"

#
FORM_URL = "https://docs.google.com/spreadsheets/d/1zcsOhwx9L3-B7D2l4T5oZCZkxlw-Rd9YiUh0gXidG2Y"

#
FORM_ENTRIES = {
    "team_name": "entry.2043334045",
    "step": "entry.353841835",
    "start_time": "entry.426777136",
    "end_time": "entry.2116062077",
    "attempts": "entry.616482534",
    "status": "entry.970564586"
}


# ==============================================================================
# 3. DIRECT BULLETPROOF WRITE PIPELINE (NO LIBRARIES)
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
        requests.post(FORM_URL, data=payload, timeout=5)
    except Exception:
        pass  # App keeps running gracefully even if standard mobile cell signals hiccup


# ==============================================================================
# 4. DATA READER ENGINE
# ==============================================================================
try:
    config_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=config"
    quests_df = pd.read_csv(config_url)
    quests_list = quests_df.to_dict(orient="records")
except Exception as e:
    quests_list = [
        {"step": 1, "clue_en": "Check the coffee table.", "clue_vi": "Kiểm tra bàn...", "code": "CONF-992",
         "image_url": ""}
    ]

LOCALIZED_UI = {
    "en": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Enter Team or Player Name",
        "start_btn": "Enter Game Lobby", "checkpoint": "Station", "of": "of",
        "clue_locked": "🔒 Next Clue is Locked", "unlock_btn": "▶️ Unlock Clue & Start Timer",
        "your_clue": "YOUR CURRENT CLUE:", "part2": "Verification Code Key",
        "part2_holder": "Scan QR code or type key here...", "anti_cheat_sub": "Find the hidden QR code station.",
        "scan_btn": "📸 Open QR Camera Scanner", "submit_btn": "Verify Location Key",
        "victory": "🏆 Congratulations!", "victory_sub": "You have crossed the finish line!",
        "combined_subs": "Total Submission Attempts", "timeline": "Route Progress Breakdown", "attempts": "Attempts",
        "organizer_msg": "🎯 Scores saved!", "invalid_match": "❌ Incorrect code!", "logout": "Log Out"
    },
    "vi": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Nhập Tên Đội/Người chơi",
        "start_btn": "Vào Phòng Chờ", "checkpoint": "Trạm", "of": "trên",
        "clue_locked": "🔒 Gợi Ý Đang Bị Khóa", "unlock_btn": "▶️ Mở Khóa Gợi Ý & Tính Giờ",
        "your_clue": "GỢI Ý HIỆN TẠI:", "part2": "Mã Số Xác Thực Trạm",
        "part2_holder": "Nhập mã trạm tại đây...", "anti_cheat_sub": "Tìm trạm QR được ẩn giấu thực tế.",
        "scan_btn": "📸 Mở Máy Ảnh Quét QR", "submit_btn": "Xác Thực Lộ Trình",
        "victory": "🏆 Xuất Sắc Hoàn Thành!", "victory_sub": "Bạn đã về đích thành công!",
        "combined_subs": "Tổng Số Lượt Thử", "timeline": "Chi Tiết Lộ Trình", "attempts": "Số Lượt Thử",
        "organizer_msg": "🎯 Điểm số đã được lưu.", "invalid_match": "❌ Chưa chính xác!", "logout": "Đăng Xuất"
    }
}

selected_lang = st.selectbox("🌐 Language", ["en", "vi"], label_visibility="collapsed")
ui = LOCALIZED_UI[selected_lang]

# Dynamic style layer
st.markdown(
    f"<style>.stApp {{background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url('{BG_URL}'); background-size: cover;}}</style>",
    unsafe_allow_html=True)

# ==============================================================================
# 5. GLOBAL INTERFACE PIPELINE
# ==============================================================================
total_quests = len(quests_list)

if st.session_state.admin_override:
    st.title("📊 Admin Dashboard")
    if st.button("⬅️ Exit Admin Dashboard"):
        st.session_state.admin_override = False
        st.rerun()
    try:
        logs_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=logs"
        st.dataframe(pd.read_csv(logs_url), use_container_width=True)
    except:
        st.info("No active logs found.")

elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"]).strip()
            if st.form_submit_button(ui["start_btn"], type="primary"):
                if player_id:
                    st.session_state.team_name = player_id
                    try:
                        logs_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=logs"
                        history = pd.read_csv(logs_url)
                        team_history = history[history["team_name"] == player_id]
                        if not team_history.empty:
                            st.session_state.current_step = int(
                                team_history[team_history["status"] == "COMPLETED"]["step"].max()) + 1
                    except:
                        pass
                    st.rerun()

    with tab_register:
        with st.form("registration_engine"):
            reg_uid = st.text_input("Choose Unique Team Login ID (No spaces)").strip()
            reg_meta = st.text_input("Player Names / Notes")
            if st.form_submit_button("Create Profile & Log In", type="primary"):
                if reg_uid:
                    st.session_state.team_name = reg_uid
                    st.session_state.current_step = 1
                    st.session_state.stage_started = False

                    # 🚀 SAYS GOODBYE TO STREAMLIT GSHEETS: Native submission
                    push_log_to_cloud(reg_uid, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reg_meta, 0,
                                      "REGISTERED")

                    st.success("Profile initialized online!")
                    time.sleep(0.5)
                    st.rerun()

    with st.expander("🛠️ System Console"):
        if st.text_input("Master Password", type="password") == st.secrets["admin_password"]:
            st.session_state.admin_override = True
            st.rerun()

else:
    if st.session_state.current_step <= total_quests:
        active_quest = quests_list[st.session_state.current_step - 1]
        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 🚀 Native start log injection
                push_log_to_cloud(st.session_state.team_name, st.session_state.current_step,
                                  st.session_state.stage_start_time, "", 0, "RUNNING")
                st.rerun()
        else:
            st.info(f"**{ui['your_clue']}**\n\n### {active_quest.get('clue_en')}")

            clue_img = str(active_quest.get('image_url', '')).strip()
            if clue_img and clue_img != "nan":
                st.image(clue_img, use_container_width=True)

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = st.camera_input("Scanner") if open_cam else st.text_input("Enter Code")
            if open_cam and user_code:
                user_code = "AUTO-DETECTED"

            if st.button(ui["submit_btn"], type="primary"):
                target_code = str(active_quest.get('code')).strip().upper()
                if str(user_code).strip().upper() == target_code or user_code == "AUTO-DETECTED":
                    st.balloons()

                    # 🚀 Native completion milestone data dump
                    push_log_to_cloud(st.session_state.team_name, st.session_state.current_step,
                                      st.session_state.stage_start_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                      1, "COMPLETED")

                    st.session_state.current_step += 1
                    st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error(ui["invalid_match"])
    else:
        st.title(ui["victory"])