# 🧭 Treasure Hunt Framework

A premium, localized, mobile-responsive progressive web application engineered for interactive corporate events. This framework leverages **Streamlit** and a state-persisted **SQLite/SQLAlchemy** engine to deliver an automated multi-stage puzzle-solving experience featuring live QR code verification, trilingual localization, and full administrative telemetry tracking.

---

## 🚀 Core Features & Architecture

* **Linear Progression Tracking:** Prevents sequence skipping. Players must solve the active station puzzle to unlock subsequent stages.
* **Live Checkpoint Persistence:** Player sessions are tracked securely inside a localized SQLite instance. If a player loses cellular connection or reloads their mobile browser, logging back in instantly restores their latest incomplete station step with zero data loss.
* **Physical QR Code Decoding Engine:** Integrated direct-capture camera scanning module utilizing stateless `OpenCV` image matrix decoding to verify unguessable station string keys on the shopfloor.
* **Trilingual UI localization Suite:** Fluidly swaps UI labels, visual asset captions, and riddle texts between **English (en)**, **Vietnamese (vi)**, and **German (de)** on the fly.
* **Admin Operations Control Center:** Secure backend console protected by a master authorization gate, featuring real-time leaderboard statistics, raw telemetry step-duration logs, progress reset controls, and account purge capabilities.

---

## 🛠️ Technology Stack & Requirements

* **Runtime Environment:** Python 3.9+
* **Web Framework:** Streamlit
* **Database Matrix:** SQLite via SQLAlchemy Engine Core
* **Computer Vision Pipeline:** OpenCV (`opencv-python-headless`)
* **Data Analysis Wrapper:** Pandas

---

## 📦 Project Directory Layout

```text
    ├── .streamlit/
    │   └── config.toml          # Custom theme configuration overrides
    ├── app.py                   # Global execution pipeline and routing engine
    ├── puzzles.py               # Centralized data storage matrix for the 10 stations
    ├── requirements.txt         # Production pip environment manifest
    └── streamlit_app.db         # Persistent local database instance (Auto-generated)
```

---

## 🔧 Installation & Deployment

1. Environment Initialization
* Clone the repository to your host server or local machine and navigate into the target workspace:
```bash
    git clone https://github.com/sonhoangn/TH-MBV-SL
    cd mbv-treasure-hunt
```

2. Dependency Resolution
* Install the required headless imaging modules, runtime drivers, and database bridges outlined in the deployment manifest:
```bash
    pip install -r requirements.txt
```
* requirements.txt file must include:
```bash
    streamlit
    pandas
    sqlalchemy
    opencv-python-headless
    numpy
```

3. Executing the System
* Launch the framework server locally using Streamlit's pipeline wrapper:
```bash
    streamlit run app.py
```

---

## 🧭 Operational Instruction Manual
### 👥 Player User Flow

1. Registration / Authentication: Players access the deployment URL on their mobile devices, select their preferred language, and either register a new unique Login ID (Individual or Group) or log back into an active account.
2. The Countdown/Unlock Phase: Players read a placeholder message indicating the station is locked. Clicking "Bắt đầu giải đố / Unlock Clue" records their specific station start time in the database logs and reveals the riddle and dynamic image asset.
3. The Search & Verification Loop: Players search the physical shopfloor for the area hinted at in the clue. Once they discover the printed QR Code card, they can either choose to open the QR Camera Scanner directly inside the web application to automatically parse the code, or manually type the verification text.
4. Completion Matrix: Upon submitting the correct key, a victory state is logged. The player progresses to the next station number, looping back until all 10 stations are checked off. The final screen displays their total attempt metrics and an elegant completion time timeline breakdown.

### 🛠️ Administrator Controls

1. Access Pathway: Scroll to the bottom of the landing page gate, expand the Console tray, and provide the secure Master Password.
2. Leaderboard Tab: Displays real-time game duration metrics calculated via precise database timestamps ($T_{end} - T_{start}$) alongside total guess attempt counters.
3. User Management Tab: Provides a non-destructive pipeline interface to selectively Reset User Progress (wiping step history but keeping account credentials intact for testing) or Completely Purge User Accounts from active production environments.

### 📋 Customization Guide
To adapt this framework architecture for alternative corporate events or different station structures, do not modify the routing machine in app.py. Instead, adjust the standalone data targets:
1. Modifying Puzzles: Open puzzles.py and adjust the dictionaries inside QUESTS_DATABASE. Update the clues, code targets (enforced uppercase string matches), and hosting destination image asset URLs matching your new venue layout.
2. Adjusting UI Phrasings: To change core translation text strings or button definitions, update the global trilingual nested dictionary matrix located under LOCALIZED_UI inside app.py.