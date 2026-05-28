import cv2
import numpy as np
import os
import streamlit as st
import pandas as pd
import time
import sqlite3
from localization import LOCALIZED_UI_ELEMENTS
from puzzles import QDB
from sqlalchemy import text
from datetime import datetime

# ==============================================================================
# 1. GLOBAL INTERFACE SETUP & SYSTEM CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="MBV 140Y Treasure Hunt", page_icon="🧭", layout="centered")

# Hardcode the configuration directly to eliminate secrets.toml path mismatches
DB_URI = "sqlite:///streamlit_app.db"

conn = st.connection(
    "treasure_hunt_db",
    type="sql",
    url=DB_URI
)

def init_db():
    """Forces a physical database layout file reset to wipe cached schema mismatches"""
    db_file = "streamlit_app.db"

    FORCE_WIPE_OUT = False

    if FORCE_WIPE_OUT and os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass

    # Initialize via native sqlite3 matching our explicit hardcoded URI target
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


# ==============================================================================
# 2. GLOBAL DIALOG FUNCTIONS (DEFINED AT ROOT LEVEL)
# ==============================================================================
@st.dialog("⚠️ Confirm Account Purge")
def confirm_purge_modal(target_player):
    st.write(
        f"Are you absolutely sure you want to permanently delete **{target_player}**? This will wipe all records and log history from the system.")

    clean_key = "".join(c for c in target_player if c.isalnum())

    if st.button("🔴 Yes, Purge Completely", type="primary", use_container_width=True,
                 key=f"modal_confirm_delete_{clean_key}"):
        with conn.session as session:
            session.execute(text("DELETE FROM hunt_logs WHERE team_name = :team;"), {"team": target_player})
            session.commit()
        st.success(f"Purged {target_player} completely from active servers!")
        time.sleep(1)
        st.rerun()

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

# Mercedes-Benz 140Y Corporate Asset Background
BG_URL = "https://group.mercedes-benz.com/bilder/innovationen/specials/140-years-of-innovation/140-years-of-innovation-visual-3-2-w1680xh945-cutout.jpg"

# QUESTS DB INITIATION
total_quests = len(QDB)

# LOCALIZATION
col_space, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox("🌐 Language", ["en", "vi", "de"], key="global_lang_selector")
ui = LOCALIZED_UI_ELEMENTS[selected_lang]

# ==============================================================================
# 3. PREMIUM DESIGN SCHEME (DARK/LIGHT THEME ADAPTIVE)
# ==============================================================================
st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">

    <style>
    /* 2. Global Font Overrides */
    html, body, [data-testid="stWidgetLabel"], .stApp, p, blockquote, div {{
        font-family: 'Roboto Condensed', sans-serif !important;
        font-size: 1.15rem; 
    }}

    /* Target headings */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 400;
    }}

    /* 3. Existing Adaptive Background Logic */
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
# 5. GLOBAL ROUTING PIPELINE ENGINE
# ==============================================================================

# ROUTE 1: FULL ADMIN OPERATIONS SUITE
if st.session_state.admin_override:
    st.title("Administrator Dashboard")
    if st.button("⬅️ Exit Admin Dashboard", type="secondary", use_container_width=True):
        st.session_state.admin_override = False
        st.rerun()

    tab_leaderboard, tab_management = st.tabs(["🏆 Leaderboard", "👥 User Management"])

    with tab_leaderboard:
        st.subheader("Leaderboard Summary")
        summary_df = conn.query("""
            SELECT 
                team_name as 'Team/Player',
                COUNT(DISTINCT case when status = 'COMPLETED' then step end) as 'Steps Completed',
                SUM(attempts) as 'Total Attempts',
                (strftime('%s', MAX(case when status = 'COMPLETED' then end_time end)) - strftime('%s', MIN(case when status = 'REGISTERED' then start_time end))) / 60.0 as 'Total Duration (min)'
            FROM hunt_logs
            GROUP BY team_name;
        """, ttl=0)
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Participants' Activities")
        logs_df = conn.query("SELECT * FROM hunt_logs ORDER BY timestamp DESC;", ttl=0)
        st.dataframe(logs_df, use_container_width=True)

    with tab_management:
        st.subheader("Manage Active System Profiles")

        # Get unique list of registered users
        users_df = conn.query(
            "SELECT DISTINCT team_name FROM hunt_logs WHERE team_name IS NOT NULL AND team_name != '';", ttl=0)

        if not users_df.empty:
            selected_user = st.selectbox(
                "Select Profile to Modify",
                users_df['team_name'].tolist(),
                key="admin_selected_user"
            )

            st.markdown(f"### Actions for **{selected_user}**")

            # --- ACTION 1: PROGRESS RESET ---
            st.markdown("#### Progress Control")
            clean_key = "".join(c for c in selected_user if c.isalnum())

            if st.button("🔄 Reset User Progress", type="secondary", use_container_width=True,
                         key=f"btn_reset_{clean_key}"):
                with conn.session as session:
                    session.execute(text("DELETE FROM hunt_logs WHERE team_name = :team AND status != 'REGISTERED';"),
                                    {"team": selected_user})
                    session.commit()
                st.success(f"Progress reset completed for {selected_user}!")
                time.sleep(1)
                st.rerun()

            st.markdown("---")

            # --- ACTION 2: ACCOUNT PURGE ---
            st.markdown("#### Danger Zone")

            if st.button("❌ Completely Purge User from System", type="secondary", use_container_width=True,
                         key=f"btn_trigger_purge_{clean_key}"):
                confirm_purge_modal(selected_user)

        else:
            st.info("No registered users found.")

# ROUTE 2: PLAYER ACCESS GATE / ACCESS LOBBY
elif not st.session_state.team_name:
    st.title(ui["welcome"])
    tab_login, tab_register = st.tabs(["🔐 Log In", "📝 Register New Team/Player"])

    with tab_login:
        with st.form("lobby_entry"):
            player_id = st.text_input(ui["team_label"]).strip()
            enter_gate = st.form_submit_button(ui["start_btn"], type="primary", use_container_width=True)
            if enter_gate and player_id:
                history_df = conn.query("SELECT * FROM hunt_logs WHERE team_name = :team;", params={"team": player_id}, ttl=0)

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
                check_exist = conn.query("SELECT 1 FROM hunt_logs WHERE team_name = :team LIMIT 1;", params={"team": reg_uid}, ttl=0)
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
        with st.expander("🔵 Console"):
            admin_pass = st.text_input("Master Password", type="password", key="main_admin_pass")
            if admin_pass == st.secrets["admin_password"]:
                st.session_state.admin_override = True
                st.rerun()

# ROUTE 3: ACTIVE GAMEPLAY & VICTORY LOOPS
else:
    if st.session_state.current_step <= total_quests:
        active_quest = QDB[st.session_state.current_step - 1]
        st.title(f"❓ {ui['checkpoint']} {st.session_state.current_step} {ui['of']} {total_quests}")

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
                localized_caption = active_quest.get(f"caption_{selected_lang}", active_quest.get("caption_en", ""))
                st.image(img_target, caption=localized_caption, use_container_width=True)

            st.write(f"### 🔑 {ui['part2']}")
            st.caption(ui["anti_cheat_sub"])

            open_cam = st.checkbox(ui["scan_btn"])
            user_code = ""

            if open_cam:
                camera_capture = st.camera_input("Scanner Active", label_visibility="collapsed")
                if camera_capture:
                    # CONVERT FILE STREAM TO OPENCV IMAGE
                    file_bytes = np.asarray(bytearray(camera_capture.read()), dtype=np.uint8)
                    opencv_img = cv2.imdecode(file_bytes, 1)

                    # INITIALIZE OPENCV QR DETECTOR
                    detector = cv2.QRCodeDetector()
                    decoded_text, points, _ = detector.detectAndDecode(opencv_img)

                    if decoded_text:
                        user_code = str(decoded_text).strip().upper()
                        st.success(f"🟢 QR Code Scanned Successfully!")
                    else:
                        user_code = "NOT-FOUND"
                        st.error(
                            "🔴 No clear QR code detected in the photo. Please adjust your angle or lighting and try again!")
            else:
                user_code = st.text_input("Enter Code Manual", placeholder=ui["part2_holder"],
                                          label_visibility="collapsed").strip().upper()

            if st.button(ui["submit_btn"], type="primary", use_container_width=True):
                target_code = str(active_quest.get('code')).strip().upper()

                if str(user_code).strip().upper() == target_code:
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

            st.markdown("<br><br>", unsafe_allow_html=True)  # Adds nice breathing room
            if st.button(ui["logout"], type="secondary", use_container_width=True, key="gameplay_midgame_logout"):
                st.session_state.team_name = None
                st.session_state.current_step = 1
                st.session_state.stage_started = False
                st.rerun()

    else:
        st.title(ui["victory"])
        st.subheader(ui["victory_sub"])
        st.image("MB_W29_140YoI_2026.jpg", use_container_width=True)
        history_df = conn.query("SELECT * FROM hunt_logs WHERE team_name = :team AND status = 'COMPLETED';", params={"team": st.session_state.team_name}, ttl=0)

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