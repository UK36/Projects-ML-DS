# SnapClass — AI Attendance System

Take class attendance with **face recognition** (classroom photos) or **voice recognition** (students say "I am present").

```
snapclass-project/
├── app/                  # Main application (Streamlit + Supabase + dlib + resemblyzer)
│   ├── .streamlit/       # Streamlit config & secrets
│   ├── src/              # App source code (components, database, pipelines, screens)
│   ├── app.py            # Streamlit entry point
│   ├── requirements.txt  # Python dependencies
│   ├── schema.sql        # Supabase database schema
│   ├── .env.example      # Example environment variables
│   └── venv/             # Dedicated Python virtual environment
├── landing/              # Landing page (Flask)
│   ├── static/           # CSS, JS, fonts, demo images
│   ├── templates/        # Landing page HTML
│   ├── app.py            # Flask entry point
│   └── requirements.txt  # Flask dependencies
├── .env.example          # Root environment template
├── run_app.bat           # Quick launcher for Main Application
├── run_landing.bat       # Quick launcher for Landing Page
└── README.md
```

## How It Works
| Component | Technology | Description |
|---|---|---|
| Face detection & embeddings | `dlib` (`face_recognition_models`) | Generates 128-dimensional face embedding vectors |
| Face identification | `scikit-learn` (SVC) + Euclidean distance (threshold 0.6) | Classifies student identities in multi-face classroom photos |
| Voice embeddings | `resemblyzer` + `librosa` | Splits audio stream and extracts 256-d voice embeddings (cosine similarity threshold 0.65) |
| Database | Supabase (PostgreSQL) | Stores teachers, students, subjects, embeddings, and attendance logs |
| Passwords | `bcrypt` | Secure hashing for teacher passwords |
| Student Join Link / QR | `segno` | Generates QR codes and join URLs |

**Workflow:**
1. **Teacher Registration & Login:** Teacher registers or logs in.
2. **Subject Creation:** Teacher creates a subject (e.g., `CS101`) and generates a shareable QR code or link.
3. **Student Registration:** Students sign up by capturing their face (and optional voice) biometrics, then enroll into the subject.
4. **Attendance Session:**
   - **Photo Mode:** Teacher uploads / captures photo(s) of the classroom. The AI pipeline detects all faces, identifies enrolled students, and generates an attendance sheet.
   - **Voice Mode:** Students say "I am present" sequentially; the system identifies student voices and marks attendance.
5. **Review & Save:** Teacher reviews attendance results and confirms to persist to Supabase.

---

## Quick Start Guide

### 1. Configure Supabase (Database)
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. In Supabase Dashboard, open **SQL Editor** -> **New query**.
3. Copy the contents of `app/schema.sql`, paste into the query editor, and click **Run**.
4. Go to **Project Settings** -> **API**.
5. Copy your **Project URL** and **API Key** (anon public key).

### 2. Set Up Environment Variables
Create a `.env` file inside the `app/` folder (or at project root), or copy from `.env.example`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
APP_URL=http://localhost:8501
```
*(Alternatively, you can also place them in `app/.streamlit/secrets.toml`)*

### 3. Run Main Application
**Option A: Windows Quick Launcher**
Simply double-click `run_app.bat`.

**Option B: Terminal (PowerShell / Command Prompt)**
```bash
cd app
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
App opens in browser at: `http://localhost:8501`

---

## Setup — Landing Page (`landing/`)
**Option A: Windows Quick Launcher**
Simply double-click `run_landing.bat`.

**Option B: Terminal**
```bash
cd landing
pip install -r requirements.txt
python app.py
```
Landing page opens in browser at: `http://localhost:5002`

---

## Enhancements & Fixes Included
- **Flexible Config:** Supports both `.env` (python-dotenv / os.environ) and Streamlit's `st.secrets` (`.streamlit/secrets.toml`).
- **Graceful Error Handling:** Shows helpful configuration guidance instead of crashing if keys are missing.
- **Fixed Manage Subjects:** Fixed loop closure bug so all created subjects display properly in teacher dashboard.
- **Fixed Voice Attendance:** Added validation to prevent crash if Analyze is clicked before recording.
- **Configurable Share URL:** QR and join links use configured `APP_URL` instead of a hardcoded domain.
- **Schema Included:** Ready-to-run `schema.sql` for 1-click database initialization.
- **Windows Launchers:** `run_app.bat` and `run_landing.bat` for one-click startup.
