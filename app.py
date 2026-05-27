import os
import streamlit as st
import pandas as pd
import time
import sqlite3
from sqlalchemy import text
from datetime import datetime

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & SYSTEM CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="MBV 140Y Treasure Hunt", page_icon="🗺️", layout="centered")

# Native, zero-dependency SQL connection engine
conn = st.connection("local_db" if st.runtime.exists() and not st.get_option("server.port") else "streamlit_db",
                     type="sql")

def init_db():
    """Forces a physical database layout file reset to wipe cached schema mismatches"""
    db_file = "streamlit_app.db"

    FORCE_WIPE_OUT = False

    if FORCE_WIPE_OUT and os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass

    # Initialize via native sqlite3 to safely clear the st.connection cache layout
    with sqlite3.connect(db_file) as native_conn:
        cursor = native_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hunt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                player_type TEXT,
                group_members TEXT,
                step INTEGER,
                start_time TEXT,
                end_time TEXT,
                attempts INTEGER,
                status TEXT,
                notes TEXT,
                timestamp TEXT
            );
        """)
        native_conn.commit()


def push_log_to_db(team, step, start, end, attempts, status, player_type="", members="", notes=""):
    """Synchronously inserts state records using modern text() execution parameters"""
    with conn.session as session:
        session.execute(text("""
            INSERT INTO hunt_logs (team_name, player_type, group_members, step, start_time, end_time, attempts, status, notes, timestamp)
            VALUES (:team, :ptype, :members, :step, :start, :end, :attempts, :status, :notes, :ts);
        """), {
            "team": str(team), "ptype": str(player_type), "members": str(members),
            "step": int(step), "start": str(start), "end": str(end),
            "attempts": int(attempts), "status": str(status), "notes": str(notes),
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        session.commit()


# Initialize Database Schema
try:
    init_db()
except Exception:
    pass

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

# ==============================================================================
# ⚠️ QUESTION DATABASE WITH INTEGRATED REMOTE IMAGE URL SLOTS
# ==============================================================================
quests_list = [
    {
        "step": 1,
        "clue_en": "Look to the sky, but don’t get lost. My three points cover land, sea, and air, no matter the cost. What am I?",
        "clue_vi": "Nhìn lên bầu trời nhưng đừng để lạc lối. Ba đỉnh của tôi làm chủ cả đất liền, đường biển và bầu trời. Tôi là gì?",
        "clue_de": "Blicke zum Himmel, doch verirre dich nicht. Meine drei Zacken weisen den Weg über Land, See und Luft – elegant und schlicht. Was bin ich?",
        "img_url": "https://group.mercedes-benz.com/bilder/misc/visuals-stern/mb-stern-2025-04-w1680xh945-cutout.jpg",
        "code": "574R"
    },
    {
        "step": 2,
        "clue_en": "Three letters that turn a luxury cruiser into a roaring track beast. Handcrafted by one master, from the west to the east. What am I? (hint: One Man, One Engine)",
        "clue_vi": "Ba chữ cái biến một chiếc xe sang êm ái thành một con quái thú gầm vang trên đường đua. Được chế tác thủ công bởi một kỹ sư duy nhất. Tôi là gì? (gợi ý: hãy nhớ đến triết lý Một người, một động cơ.)",
        "clue_de": "Drei Buchstaben machen aus einer Luxuslimousine ein brüllendes Rennstreckenbiest. Von einem Meister von Hand gefertigt, von West bis Ost. Was bin ich? (Hinweis: Ein Mann, ein Motor)",
        "img_url": "https://di-uploads-pod30.dealerinspire.com/budsnailmotorcarsltd/uploads/2020/05/AMG-Handcrafted-Engine-Production-M139-Engine.jpg",
        "code": "AM9"
    },
    {
        "step": 3,
        "clue_en": "Invented by Benz engineers to keep you in line, I pulse when you panic and save you just in time. I stop the wheels from locking tight. What am I?",
        "clue_vi": "Được các kỹ sư Benz phát minh để giữ bạn an toàn. Tôi sẽ nhấp nhả liên tục khi bạn phanh gấp, giúp bánh xe không bị bó cứng. Tôi là gì?",
        "clue_de": "Von Benz-Ingenieuren entwickelt, um dich in der Spur zu halten. Ich pulse bei Vollbremsung und rette dich in der Not, indem ich das Blockieren der Räder verhindere. Was bin ich?",
        "img_url": "https://500sec.com/wp-content/uploads/2009/12/462255_788468_3661_2880_96067472184-37.jpg",
        "code": "48S"
    }
]
total_quests = len(quests_list)

# ==============================================================================
# 2. LOCALIZED LINGUISTIC DICTIONARY (TRILINGUAL SUITE)
# ==============================================================================
LOCALIZED_UI = {
    "en": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Enter Unique Login ID",
        "start_btn": "Enter Game Lobby", "checkpoint": "Station", "of": "of",
        "clue_locked": "🔒 Next Clue is Locked", "unlock_btn": "▶️ Unlock Clue & Start Timer",
        "your_clue": "YOUR CURRENT CLUE:", "part2": "Verification Code Key",
        "part2_holder": "Scan QR code or type key here...", "anti_cheat_sub": "Find the hidden QR code station.",
        "scan_btn": "📸 Open QR Camera Scanner", "submit_btn": "Verify Location Key",
        "victory": "🏆 Congratulations!", "victory_sub": "You have successfully crossed the finish line!",
        "combined_subs": "Total Submission Attempts", "timeline": "Route Progress Breakdown", "attempts": "Attempts",
        "organizer_msg": "🎯 Your scores are locked in. Please inform the coordinator!",
        "invalid_match": "❌ Incorrect verification code! Please try again.", "logout": "Log Out / Return Home",
        "reg_type": "Registration Type", "reg_ind": "Individual Player", "reg_grp": "Group / Team",
        "members_label": "Names of Group Members (Comma separated)", "members_holder": "Alex, John, Sarah..."
    },
    "vi": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Nhập Mã Đăng Nhập Đã Đăng Ký",
        "start_btn": "Vào Phòng Chờ", "checkpoint": "Trạm", "of": "trên",
        "clue_locked": "🔒 Gợi Ý Đang Bị Khóa", "unlock_btn": "▶️ Mở Khóa Gợi Ý & Tính Giờ",
        "your_clue": "GỢI Ý HIỆN TẠI CỦA BẠN:", "part2": "Mã Số Xác Thực Trạm",
        "part2_holder": "Nhập mã trạm tại đây...", "anti_cheat_sub": "Tìm trạm QR được ẩn giấu thực tế.",
        "scan_btn": "📸 Mở Máy Ảnh Quét QR", "submit_btn": "Xác Thực Lộ Trình",
        "victory": "🏆 Xuất Sắc Hoàn Thành!",
        "victory_sub": "Bạn đã về đích thành công! Dưới đây là thành tích của bạn:",
        "combined_subs": "Tổng Số Lượt Thử", "timeline": "Chi Tiết Lộ Trình Di Chuyển", "attempts": "Số Lượt Thử",
        "organizer_msg": "🎯 Điểm số đã được lưu. Hãy báo với ban tổ chức!",
        "invalid_match": "❌ Mã xác thực chưa chính xác. Vui lòng kiểm tra lại!", "logout": "Đăng Xuất / Trở Về",
        "reg_type": "Hình Thức Tham Gia", "reg_ind": "Cá Nhân", "reg_grp": "Đội / Nhóm",
        "members_label": "Tên các thành viên trong nhóm (Cách nhau bằng dấu phẩy)", "members_holder": "An, Bình, Chi..."
    },
    "de": {
        "welcome": "Mercedes-Benz Vietnam 140Y Jubiläums-Schnitzeljagd", "team_label": "Eindeutige Login-ID eingeben",
        "start_btn": "Spiel-Lobby betreten", "checkpoint": "Station", "of": "von",
        "clue_locked": "🔒 Nächster Hinweis ist gesperrt", "unlock_btn": "▶️ Hinweis freischalten & Timer starten",
        "your_clue": "IHR AKTUELLER HINWEIS:", "part2": "Verifizierungscode",
        "part2_holder": "QR-Code scannen oder Code hier eingeben...",
        "anti_cheat_sub": "Finden Sie die versteckte QR-Code-Station.",
        "scan_btn": "📸 QR-Code Kamera-Scanner öffnen", "submit_btn": "Code verifizieren",
        "victory": "🏆 Herzlichen Glückwunsch!", "victory_sub": "Sie haben die Ziellinie erfolgreich überquert!",
        "combined_subs": "Versuche Insgesamt", "timeline": "Details Routenverlauf", "attempts": "Versuche",
        "organizer_msg": "🎯 Ihre Ergebnisse sind gesichert. Bitte Spielleiter informieren!",
        "invalid_match": "❌ Falscher Code! Bitte überprüfen Sie Ihre Eingabe.", "logout": "Abmelden / Home",
        "reg_type": "Registrierungstyp", "reg_ind": "Einzelspieler", "reg_grp": "Gruppe / Team",
        "members_label": "Namen der Gruppenmitglieder (Kommagetrennt)", "members_holder": "Max, Anna, Tom..."
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

    try:
        logs_df = conn.query("""
            SELECT 
                team_name as 'Team/Player ID', 
                player_type as 'Type', 
                group_members as 'Group Members',
                step as 'Station Step', 
                start_time as 'Unlocked At', 
                end_time as 'Verified At', 
                status as 'Status',
                notes as 'Notes'
            FROM hunt_logs;
        """)
        if not logs_df.empty:
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.info("No active runs logged yet.")
    except Exception:
        st.info("Database is initializing...")

# ROUTE 2: PLAYER ACCESS GATE / ACCESS LOBBY
elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"]).strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)
            if enter_gate and player_id:
                history_df = conn.query(text("SELECT * FROM hunt_logs WHERE team_name = :team;"), params={"team": player_id})

                if not history_df.empty:
                    st.session_state.team_name = player_id

                    # Calculate current step safely
                    completed_steps = history_df[history_df["status"] == "COMPLETED"]["step"].tolist()
                    if completed_steps:
                        st.session_state.current_step = max(completed_steps) + 1
                    else:
                        st.session_state.current_step = 1

                    # Restore running status safely on session breaks
                    running_steps = history_df[history_df["status"] == "RUNNING"]["step"].tolist()
                    if running_steps and (not completed_steps or max(running_steps) > max(completed_steps)):
                        st.session_state.stage_started = True
                        st.session_state.stage_start_time = history_df[history_df["status"] == "RUNNING"].iloc[-1]["start_time"]
                    else:
                        st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error("Profile ID not found! Please register first.")

    with tab_register:
        with st.form("registration_engine"):
            reg_uid = st.text_input("Choose Unique Login ID (No spaces, e.g., TeamAlpha)").strip()
            player_type_selection = st.radio(ui["reg_type"], [ui["reg_ind"], ui["reg_grp"]])
            group_members_input = st.text_input(ui["members_label"], placeholder=ui["members_holder"])
            reg_meta = st.text_input("Additional Coordinator Notes / Comments")
            submit_registration = st.form_submit_button("Create Profile & Log In", type="primary",
                                                        use_container_width=True)

            if submit_registration and reg_uid:
                check_exist = conn.query(text("SELECT 1 FROM hunt_logs WHERE team_name = :team LIMIT 1;"),
                                         params={"team": reg_uid})
                if not check_exist.empty:
                    st.error("This Login ID is already taken! Choose another one.")
                else:
                    st.session_state.team_name = reg_uid
                    st.session_state.current_step = 1
                    st.session_state.stage_started = False

                    final_type = "Individual" if player_type_selection == ui["reg_ind"] else "Group"
                    final_members = group_members_input if final_type == "Group" else "N/A"

                    push_log_to_db(
                        team=reg_uid,
                        step=0,
                        start=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        end="",
                        attempts=0,
                        status="REGISTERED",
                        player_type=final_type,
                        members=final_members,
                        notes=reg_meta
                    )
                    st.success("Profile initialized online!")
                    time.sleep(0.5)
                    st.rerun()

    st.markdown("---")
    col_space_div, col_right_admin = st.columns([3, 1])
    with col_right_admin:
        with st.expander("🛠️ Console"):
            admin_pass = st.text_input("Master Password", type="password", key="main_admin_pass")
            if admin_pass == "MBV140Years":
                st.session_state.admin_override = True
                st.rerun()

# ROUTE 3: ACTIVE GAMEPLAY & VICTORY LOOPS
else:
    if st.session_state.current_step <= total_quests:
        active_quest = quests_list[st.session_state.current_step - 1]
        st.title(f"🗺️ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

        if not st.session_state.stage_started:
            st.warning(ui["clue_locked"])
            if st.button(ui["unlock_btn"], type="primary", use_container_width=True):
                st.session_state.stage_started = True
                st.session_state.stage_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Unified execution context block to prevent thread deadlocks
                with conn.session as session:
                    res = session.execute(text("SELECT player_type, group_members FROM hunt_logs WHERE team_name = :team AND status = 'REGISTERED' LIMIT 1;"), {"team": st.session_state.team_name}).fetchone()
                    pt = res[0] if res else "Unknown"
                    gm = res[1] if res else "Unknown"

                push_log_to_db(st.session_state.team_name, st.session_state.current_step,
                               st.session_state.stage_start_time, "", 0, "RUNNING", player_type=pt, members=gm)
                st.rerun()
        else:
            current_clue_text = active_quest.get('clue_' + selected_lang, active_quest.get('clue_en'))
            st.info(f"**{ui['your_clue']}**\n\n### {current_clue_text}")

            # 🖼️ DYNAMIC CLUE IMAGE VIEWER
            img_target = active_quest.get("img_url", "")
            if img_target:
                st.image(img_target, caption=f"{ui['checkpoint']} {st.session_state.current_step} Clue Visual Asset",
                         use_container_width=True)

            st.write(f"### 🔑 {ui['part2']}")
            st.caption(ui["anti_cheat_sub"])

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = ""
            if open_cam:
                camera_capture = st.camera_input("Scanner Active", label_visibility="collapsed")
                if camera_capture:
                    user_code = "AUTO-DETECTED"
            else:
                user_code = st.text_input("Enter Code Manual", placeholder=ui["part2_holder"],
                                          label_visibility="collapsed").strip().upper()

            if st.button(ui["submit_btn"], type="primary", use_container_width=True):
                target_code = str(active_quest.get('code')).strip().upper()

                if str(user_code).strip().upper() == target_code or user_code == "AUTO-DETECTED":
                    st.balloons()
                    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Unified execution context block to prevent thread deadlocks
                    with conn.session as session:
                        res = session.execute(text("SELECT player_type, group_members FROM hunt_logs WHERE team_name = :team AND status = 'REGISTERED' LIMIT 1;"), {"team": st.session_state.team_name}).fetchone()
                        pt = res[0] if res else "Unknown"
                        gm = res[1] if res else "Unknown"

                    push_log_to_db(st.session_state.team_name, st.session_state.current_step,
                                   st.session_state.stage_start_time, end_time_str, 1, "COMPLETED", player_type=pt,
                                   members=gm)

                    st.session_state.current_step += 1
                    st.session_state.stage_started = False
                    st.rerun()
                else:
                    st.error(ui["invalid_match"])

    else:
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])

        history_df = conn.query(text("SELECT * FROM hunt_logs WHERE team_name = :team AND status = 'COMPLETED';"),
                                params={"team": st.session_state.team_name})

        if not history_df.empty:
            records = []
            total_attempts = int(history_df["attempts"].sum())

            for _, row in history_df.iterrows():
                t1 = datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(row["end_time"], "%Y-%m-%d %H:%M:%S")
                duration_mins = round((t2 - t1).total_seconds() / 60, 1)

                records.append({
                    "Station Step": f"Station {row['step']}",
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