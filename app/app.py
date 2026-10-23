import streamlit as st
from pathlib import Path

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.database.config import is_supabase_configured

from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.ui.base_layout import style_base_layout

def render_optional_supabase_setup():
    with st.expander("⚙️ Database Settings (Running on Local SQLite — Click to connect Cloud Supabase)", expanded=False):
        st.info(
            "SnapClass is currently running in **Local SQLite mode**. All features (face recognition, "
            "teacher portal, subjects, and attendance) are fully functional locally.\n\n"
            "If you want to sync with a **Cloud Supabase** project:\n"
            "1. Create a project at [supabase.com](https://supabase.com) and run `schema.sql`.\n"
            "2. Enter your credentials below and click **Connect Cloud Database**."
        )

        with st.form("supabase_setup_form"):
            url_input = st.text_input("Supabase Project URL", placeholder="https://xxxxxxxx.supabase.co")
            key_input = st.text_input("Supabase Anon / Service Key", type="password", placeholder="eyJhbGciOiJIUzI1NiIsInR5c...")
            app_url_val = st.text_input("Application URL", value="http://localhost:8501")
            submitted = st.form_submit_button("🚀 Connect Cloud Database", type="primary")

            if submitted:
                if not url_input.strip() or not key_input.strip() or "xxxxxxxx" in url_input.lower():
                    st.error("Please enter a valid Supabase URL and Key.")
                else:
                    env_text = (
                        f"SUPABASE_URL={url_input.strip()}\n"
                        f"SUPABASE_KEY={key_input.strip()}\n"
                        f"APP_URL={app_url_val.strip()}\n"
                    )
                    for target_dir in [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]]:
                        try:
                            env_file = target_dir / ".env"
                            env_file.write_text(env_text, encoding="utf-8")
                        except Exception:
                            pass
                    st.success("✅ Supabase credentials saved! Connecting to cloud database...")
                    st.rerun()

def main():
    st.set_page_config(
        page_title='SnapClass — AI Attendance System',
        page_icon= "https://i.ibb.co/YTYGn5qV/logo.png"
    )
    style_base_layout()

    if not is_supabase_configured():
        render_optional_supabase_setup()

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()
        
        case None:
            home_screen()

    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)

main()
