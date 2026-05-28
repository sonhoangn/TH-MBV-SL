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

    # CRITICAL: Keep this False so your production data is never wiped!
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
# GLOBAL DIALOG FUNCTIONS (DEFINED AT ROOT LEVEL)
# ==============================================================================
@st.dialog("⚠️ Confirm Account Purge")
def confirm_purge_modal(target_player):
    st.write(
        f"Are you absolutely sure you want to permanently delete **{target_player}**? This will wipe all records and log history from the system.")

    clean_key = "".join(c for c in target_player if c.isalnum())

    # 🛠️ FIXED: Changed type="danger" to type="primary"
    if st.button("🔥 Yes, Purge Completely", type="primary", use_container_width=True,
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

# 🖼️ Mercedes-Benz 140Y Corporate Asset Background
BG_URL = "https://group.mercedes-benz.com/bilder/innovationen/specials/140-years-of-innovation/140-years-of-innovation-visual-3-2-w1680xh945-cutout.jpg"

# ==============================================================================
# ⚠️ QUESTION DATABASE WITH INTEGRATED REMOTE IMAGE URL SLOTS
# ==============================================================================
# quests_list = [
#     {
#         "step": 1,
#         "clue_en": "Look to the sky, but don’t get lost. My three points cover land, sea, and air, no matter the cost. What am I?",
#         "clue_vi": "Ngước nhìn tinh tú giữa trời,"
#                    "Ba phương chinh phục, chẳng rời bước chân."
#                    "Đất, sông, không phận bước gần,"
#                    "Biểu tượng tỏa sáng, vạn lần uy nghi."
#                    "Tôi là gì?",
#         "clue_de": "Blicke zum Himmel, doch verirre dich nicht. Meine drei Zacken weisen den Weg über Land, See und Luft – elegant und schlicht. Was bin ich?",
#         "img_url": "https://group.mercedes-benz.com/bilder/misc/visuals-stern/mb-stern-2025-04-w1680xh945-cutout.jpg",
#         "caption_en": "Visual Clue for station 1.",
#         "caption_vi": "Hình ảnh gợi ý Trạm số 1.",
#         "caption_de": "Visualisierungshilfe für Station 1.",
#         "code": "STAR"
#     },
#     {
#         "step": 2,
#         "clue_en": "Three letters that turn a luxury cruiser into a roaring track beast. Handcrafted by one master, from the west to the east. What am I? (hint: One Man, One Engine)",
#         "clue_vi": "Ba chữ tạo nên uy quyền,"
#                    "Một người, một máy, trọn miền khát khao."
#                    "Đường đua gầm thét vút cao,"
#                    "Khắc ghi đẳng cấp, tự hào gọi tên."
#                    "Tôi là gì? (gợi ý: hãy nhớ đến triết lý Một người, một động cơ - One Man, One Engine.)",
#         "clue_de": "Drei Buchstaben machen aus einer Luxuslimousine ein brüllendes Rennstreckenbiest. Von einem Meister von Hand gefertigt, von West bis Ost. Was bin ich? (Hinweis: Ein Mann, ein Motor)",
#         "img_url": "https://di-uploads-pod30.dealerinspire.com/budsnailmotorcarsltd/uploads/2020/05/AMG-Handcrafted-Engine-Production-M139-Engine.jpg",
#         "caption_en": "Visual Clue for station 2.",
#         "caption_vi": "Hình ảnh gợi ý Trạm số 2.",
#         "caption_de": "Visualisierungshilfe für Station 2.",
#         "code": "AMG"
#     },
#     {
#         "step": 3,
#         "clue_en": "Invented by Benz engineers to keep you in line, I pulse when you panic and save you just in time. I stop the wheels from locking tight. What am I?",
#         "clue_vi": "Benz dành tâm huyết tạo nên,"
#                    "Giúp người cầm lái vững bền trên xe."
#                    "Phanh gấp bánh chẳng hề tê,"
#                    "Giữ cho vững lái, tràn trề niềm vui. "
#                    "Tôi là gì?",
#         "clue_de": "Von Benz-Ingenieuren entwickelt, um dich in der Spur zu halten. Ich pulse bei Vollbremsung und rette dich in der Not, indem ich das Blockieren der Räder verhindere. Was bin ich?",
#         "img_url": "https://500sec.com/wp-content/uploads/2009/12/462255_788468_3661_2880_96067472184-37.jpg",
#         "caption_en": "Visual Clue for station 3.",
#         "caption_vi": "Hình ảnh gợi ý Trạm số 3.",
#         "caption_de": "Visualisierungshilfe für Station 3.",
#         "code": "ABS"
#     }
# ]
quests_list = [
    {
        "step": 1,
        "clue_en": "Where the first breath of ownership is taken, and the journey begins under the silver sign.",
        "clue_vi": "Nơi đây đón khách phương xa, - Nhận xe vừa xuất xưởng nhà M B.",
        "clue_de": "Wo der erste Atemzug des Eigentums genommen wird und die Reise unter dem silbernen Zeichen beginnt.",
        "img_url": "https://www.mercedes-benz.com.vn/content/dam/hq/passengercars/services/contact/Stage_picture_ContactUs.jpeg/1740017038197.jpg",
        "caption_en": "Visual Clue for station 1.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 1.",
        "caption_de": "Visualisierungshilfe für Station 1.",
        "code": "CUSTOMERCENTER-WELCOME"
    },
    {
        "step": 2,
        "clue_en": "I have no skin, only joints of steel welded by light. Find me.",
        "clue_vi": "Thân không lớp áo bao quanh, - Khung xương thép cứng, lửa xanh hàn liền. - Tìm nơi tạo tác cơ huyền, - Dáng hình định sẵn, vẹn nguyên đợi chờ.",
        "clue_de": "Ich habe keine Haut, nur stählerne Gelenke, geschweißt durch Licht. Finde mich.",
        "img_url": "https://cafebiz.cafebizcdn.vn/162123310254002176/2022/6/7/gab60151-1654577434630186194482.jpg",
        "caption_en": "Visual Clue for station 2.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 2.",
        "caption_de": "Visualisierungshilfe für Station 2.",
        "code": "BODYSHOP"
    },
    {
        "step": 3,
        "clue_en": "Enter the chamber of mist, where colors are locked in a cage and fire bakes the skin to a mirror finish.",
        "clue_vi": "Vào trong sương khói mịt mù, - Sắc màu giam giữ, thiên thu đợi chờ. - Lửa nung bóng mượt nên thơ, - Gương soi diện mạo, bất ngờ hiện lên.",
        "clue_de": "Tritt ein in die Kammer des Nebels, wo Farben gefangen sind und das Feuer die Haut zur Hochglanzpolitur bäckt.",
        "img_url": "https://www.theslshop.com/wp-content/uploads/2023/01/Paintshop-scaled.jpg",
        "caption_en": "Visual Clue for station 3.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 3.",
        "caption_de": "Visualisierungshilfe für Station 3.",
        "code": "PAINTSHOP"
    },
    {
        "step": 4,
        "clue_en": "I am the long, moving pulse of the factory. Millions of parts flow through me to become a machine.",
        "clue_vi": "Dòng đời chuyển động không ngừng, - Lắp từng linh kiện, lẫy lừng dáng xe.",
        "clue_de": "Ich bin der lange, pulsierende Schlag der Fabrik. Millionen Teile fließen durch mich, um zur Maschine zu werden.",
        "img_url": "https://cafebiz.cafebizcdn.vn/162123310254002176/2022/6/7/18-16545774359631726680478.png",
        "caption_en": "Visual Clue for station 4.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 4.",
        "caption_de": "Visualisierungshilfe für Station 4.",
        "code": "ASSEMBLYLINE"
    },
    {
        "step": 5,
        "clue_en": "I challenge the momentum of the beast. Where the wheels fight the floor to prove their stillness.",
        "clue_vi": "Tốc độ dừng lại tức thì, - Bánh xe không khóa, quản đi an toàn.",
        "clue_de": "Ich fordere den Schwung der Bestie heraus. Wo die Räder gegen den Boden kämpfen, um ihre Stille zu beweisen.",
        "img_url": "https://500sec.com/wp-content/uploads/2009/12/462255_788468_3661_2880_96067472184-37.jpg",
        "caption_en": "Visual Clue for station 5.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 5.",
        "caption_de": "Visualisierungshilfe für Station 5.",
        "code": "EOL-BRAKETEST-ABS"
    },
    {
        "step": 6,
        "clue_en": "I am the silent canyon of steel and rubber, holding the treasures that wait for their call to action.",
        "clue_vi": "Nơi lưu hàng hóa đợi chờ, - Phụ tùng xếp lớp, nằm chờ lên khung.",
        "clue_de": "Ich bin der stille Canyon aus Stahl und Gummi, der die Schätze birgt, die auf ihren Einsatz warten.",
        "img_url": "https://group.mercedes-benz.com/bilder/karriere/ueber-uns/standorte/logistic-center-ger-row/lc-germersheim/lc-germersheim-sperrigteile-w1920xh1080-cutout.jpg",
        "caption_en": "Visual Clue for station 6.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 6.",
        "caption_de": "Visualisierungshilfe für Station 6.",
        "code": "CKDWAREHOUSE"
    },
    {
        "step": 7,
        "clue_en": "The finish line that loops back to the start. Where time is reversed and youth is restored to the engine.",
        "clue_vi": "Sau ngày lăn bánh đường xa, - Chăm lo bảo dưỡng, mặn mà tình thân.",
        "clue_de": "Die Ziellinie, die zurück zum Anfang führt. Wo die Zeit umgekehrt und der Maschine ihre Jugend zurückgegeben wird.",
        "img_url": "https://mercedes-benz-mauritius.com/assets/img/afterSales/Service&Maintenance.jpg",
        "caption_en": "Visual Clue for station 7.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 7.",
        "caption_de": "Visualisierungshilfe für Station 7.",
        "code": "AFTERSALESERVICE"
    },
    {
        "step": 8,
        "clue_en": "When the silicon brain falters, I am the unseen hand that restores the flow. I bridge the divide between man and machine.",
        "clue_vi": "Bàn tay vô ảnh chuyển vòng, - Nối liền người, máy, dựng dòng tinh anh.",
        "clue_de": "Wenn das Siliziumhirn stockt, bin ich die unsichtbare Hand, die den Fluss wiederherstellt. Ich überbrücke die Kluft zwischen Mensch und Maschine.",
        "img_url": "https://www.mbusa.com/content/dam/mb-nafta/us/contact-us/XL-Custmer-Assistance-Compact-Tile-1.jpg",
        "caption_en": "Visual Clue for station 8.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 8.",
        "caption_de": "Visualisierungshilfe für Station 8.",
        "code": "ITS-INFRASTRUCTURE"
    },
    {
        "step": 9,
        "clue_en": "I capture the whispers of the driver. I am the mirror of the road, reflecting satisfaction or silent scorn.",
        "clue_vi": "Thay lời khách trải dặm xa, - Cầm vô lăng lái, bôn ba đường dài. - Tỉ mỉ soi lỗi từng bài, - Gương soi chân thực, đánh hài lòng ai.",
        "clue_de": "Ich fange das Flüstern des Fahrers ein. Ich bin der Spiegel der Straße, der Zufriedenheit oder stillen Spott reflektiert.",
        "img_url": "https://www.mercedes-benz.com.hk/content/dam/hq/passengercars/buy/storefront/help-faq/liveberatung-1200x1600.jpg/1740016196187.jpg",
        "caption_en": "Visual Clue for station 9.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 9.",
        "caption_de": "Visualisierungshilfe für Station 9.",
        "code": "VOCA-QUALITYASSURANCE"
    },
    {
        "step": 10,
        "clue_en": "Seek the architect of the motion. Find the name that holds 140 years of history in four letters.",
        "clue_vi": "Một trăm bốn chục năm rồi, - Tên người sáng lập, đời đời khắc ghi.",
        "clue_de": "Suche den Architekten der Bewegung. Finde den Namen, der 140 Jahre Geschichte in vier Buchstaben trägt.",
        "img_url": "https://cdn.24h.com.vn/upload/4-2024/images/2024-10-08/Nha-may-Mercedes-Benz-duoc-gia-han-them-5-nam-tai-Viet-Nam-f--2--1728322892-53-width740height495.jpg",
        "caption_en": "Visual Clue for station 10.",
        "caption_vi": "Hình ảnh gợi ý Trạm số 10.",
        "caption_de": "Visualisierungshilfe für Station 10.",
        "code": "KARL"
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
        "clue_locked": "🔒 Get ready for your next puzzle!", "unlock_btn": "▶️ Unlock Clue & Start Solving",
        "your_clue": "YOUR CURRENT CLUE:", "part2": "Verification Code Key",
        "part2_holder": "Scan QR code or type key here...", "anti_cheat_sub": "Find the QR code hidden somewhere in the area that the clue is hinting at.",
        "scan_btn": "📸 Open QR Camera Scanner", "submit_btn": "Submit Answer",
        "victory": "🏆 Congratulations!", "victory_sub": "You have successfully crossed the finish line!",
        "combined_subs": "Total Submission Attempts (Including failed attempts)", "timeline": "Route Progress Breakdown", "attempts": "Attempts",
        "organizer_msg": "🎯 Your scores are locked in. Please inform the coordinator!",
        "invalid_match": "❌ Incorrect answer! Please try again.", "logout": "Log Out / Return Home",
        "reg_type": "Registration Type", "reg_ind": "Individual Player", "reg_grp": "Group / Team",
        "members_label": "Names of Group Members (Comma separated)", "members_holder": "Alex, John, Sarah..."
    },
    "vi": {
        "welcome": "Mercedes-Benz Vietnam 140Y Anniversary Treasure Hunt", "team_label": "Điền Tên Đăng Nhập Đã Đăng Ký",
        "start_btn": "Vào Phòng Chờ", "checkpoint": "Trạm", "of": "trên",
        "clue_locked": "🔒 Sẵn sàng vào câu đố tiếp theo", "unlock_btn": "▶️ Bắt đầu giải đố",
        "your_clue": "GỢI Ý:", "part2": "Câu trả lời/Mã QR",
        "part2_holder": "Nhập mã ...", "anti_cheat_sub": "Tìm và quét mã QR được giấu ở khu vực mà câu đố hướng đến.",
        "scan_btn": "📸 Mở Máy Ảnh Quét mã QR", "submit_btn": "Gửi câu trả lời",
        "victory": "🏆 Xuất Sắc, Bạn đã hoàn thành thử thách này!",
        "victory_sub": "Cùng điểm lại thành tích của bạn nào!",
            "combined_subs": "Tổng Số lượt thực hiện (bao gồm cả lượt đoán sai)", "timeline": "Chi Tiết quá trình giải đố", "attempts": "Số Lượt Thử",
        "organizer_msg": "🎯 Điểm số của bạn đã được lưu. Hãy báo với ban tổ chức!",
        "invalid_match": "❌ câu trả lời chưa chính xác. Vui lòng thử lại!", "logout": "Đăng Xuất / Trở Về",
        "reg_type": "Hình Thức Tham Gia", "reg_ind": "Cá Nhân", "reg_grp": "Đội / Nhóm",
        "members_label": "Tên các thành viên trong nhóm (Cách nhau bằng dấu phẩy)", "members_holder": "An, Bình, Chi..."
    },
    "de": {
        "welcome": "Mercedes-Benz Vietnam 140Y Jubiläums-Schnitzeljagd", "team_label": "Eindeutige Login-ID eingeben",
        "start_btn": "Spiel-Lobby betreten", "checkpoint": "Station", "of": "von",
        "clue_locked": "🔒 Machen Sie sich bereit für das nächste Rätsel!", "unlock_btn": "▶️ Hinweis freischalten & Rätsel starten",
        "your_clue": "HINWEIS:", "part2": "Antwort / QR-Code",
        "part2_holder": "Code eingeben ...", "anti_cheat_sub": "Finden und scannen Sie den QR-Code, der in dem vom Hinweis angedeuteten Bereich versteckt ist.",
        "scan_btn": "📸 QR-Code Kamera-Scanner öffnen", "submit_btn": "Antwort senden",
        "victory": "🏆 Herzlichen Glückwunsch, Sie haben die Herausforderung gemeistert!",
        "victory_sub": "Lassen Sie uns einen Blick auf Ihre Ergebnisse werfen!",
        "combined_subs": "Versuche insgesamt (einschließlich falscher Antworten)", "timeline": "Details des Rätselverlaufs", "attempts": "Versuche",
        "organizer_msg": "🎯 Ihre Ergebnisse sind gesichert. Bitte Spielleiter informieren!",
        "invalid_match": "❌ Falsche Antwort! Bitte versuchen Sie es erneut.", "logout": "Abmelden / Home",
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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Italiana&display=swap" rel="stylesheet">

    <style>
    /* 2. Global Font Overrides */
    html, body, [data-testid="stWidgetLabel"], .stApp, p, blockquote, div {{
        font-family: 'Instrument Serif', serif !important;
        font-size: 1.15rem; /* Slightly scale up regular prose since serif fonts can look smaller */
    }}

    /* Target headings specifically for an elegant look */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Instrument Serif', serif !important;
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
    st.title("Administrator Dashboard")
    if st.button("⬅️ Exit Admin Dashboard", type="secondary", use_container_width=True):
        st.session_state.admin_override = False
        st.rerun()

    tab_leaderboard, tab_management = st.tabs(["🏆 Leaderboard", "👥 User Management"])

    with tab_leaderboard:
        st.subheader("Leaderboard Summary")
        # ttl=0 forces Streamlit to drop cache and read live rows
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
        st.subheader("📋 Raw Operational Logs")
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

            # 🛠️ FIXED: Changed type="danger" to type="secondary"
            if st.button("🗑️ Completely Purge User from System", type="secondary", use_container_width=True,
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
                localized_caption = active_quest.get(f"caption_{selected_lang}", active_quest.get("caption_en", ""))
                st.image(img_target, caption=localized_caption, use_container_width=True)

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