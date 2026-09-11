import streamlit as st
from utils.data_service import get_notifications


def render_nav():
    if "user_id" not in st.session_state:
        return

    current_role = st.session_state.get("role", "elderly")
    user_name = st.session_state.get("name", "User")

    # Resolute Slate Navy Navigation Bar from DESIGN.md
    st.markdown("""
        <style>
        .apon-navbar {
            background-color: #1F3042;
            color: #FFFFFF;
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(31, 48, 66, 0.12);
        }
        .apon-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.4rem;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: -0.01em;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .apon-brand-icon {
            background-color: #176B4D;
            color: #FFFFFF;
            border-radius: 10px;
            padding: 6px 10px;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .apon-badge-wellness {
            background-color: rgba(255, 255, 255, 0.12);
            color: #A4F3CC;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-left: 12px;
        }
        </style>
        
        <div class="apon-navbar">
            <div style="display: flex; align-items: center;">
                <div class="apon-brand">
                    <span class="material-symbols-outlined apon-brand-icon">spa</span>
                    <span>APON</span>
                </div>
                <span class="apon-badge-wellness">Cognitive Wellness Platform</span>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; font-size: 0.95rem; color: #DDF5EC;">
                <span>Signed in: <strong style="color: #FFFFFF;">""" + str(user_name) + """</strong> (""" + str(current_role.capitalize()) + """)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Top Navigation Action Row
    col_nav, col_actions = st.columns([4, 2])
    with col_nav:
        n1, n2, n3, n4, n5 = st.columns(5)
        with n1:
            home_target = "pages/elderly_dashboard.py" if current_role == "elderly" else "pages/caregiver_dashboard.py"
            if st.button("Home", key="nav_home", use_container_width=True):
                st.switch_page(home_target)
        with n2:
            if st.button("Games", key="nav_games", use_container_width=True):
                st.switch_page("pages/games_menu.py")
        with n3:
            if st.button("Progress", key="nav_progress", use_container_width=True):
                st.switch_page("pages/progress.py")
        with n4:
            if st.button("Assistant", key="nav_assistant", use_container_width=True):
                st.switch_page("pages/memory_assistant.py")
        with n5:
            if st.button("Caregiver", key="nav_caregiver", use_container_width=True):
                st.switch_page("pages/caregiver_dashboard.py")

    with col_actions:
        a1, a2, a3 = st.columns(3)
        with a1:
            notif_label = "Notifications"
            if st.button(notif_label, key="nav_notifications", use_container_width=True):
                st.session_state.show_notifications = not st.session_state.get("show_notifications", False)
        with a2:
            if st.button("Settings", key="nav_settings", use_container_width=True):
                st.switch_page("pages/settings.py")
        with a3:
            if current_role == "elderly":
                if st.button("Caregiver View", key="nav_switch_caregiver", use_container_width=True):
                    st.session_state.role = "caregiver"
                    st.switch_page("pages/caregiver_dashboard.py")
            else:
                if st.button("Elderly View", key="nav_switch_elderly", use_container_width=True):
                    st.session_state.role = "elderly"
                    st.switch_page("pages/elderly_dashboard.py")

    # Working Notifications Drawer/Expander if toggled
    if st.session_state.get("show_notifications", False):
        with st.expander("Active Notifications", expanded=True):
            notifs = get_notifications()
            for n in notifs:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #E5E9EC;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 20px;">{n['icon']}</span>
                            <span style="font-weight: 500; color: #17212B;">{n['title']}</span>
                        </div>
                        <span style="font-size: 0.82rem; color: #6B7680;">{n['time']}</span>
                    </div>
                """, unsafe_allow_html=True)
            if st.button("Close Notifications", key="close_notifs", use_container_width=True):
                st.session_state.show_notifications = False
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Sidebar Navigation
    st.sidebar.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 26px;">spa</span>
            <h3 style="margin: 0; color: #1D2B3A; font-weight: 700;">APON</h3>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"<p style='color: #6B7680; font-size: 0.9rem; margin-bottom: 20px;'>Logged in: <strong>{user_name}</strong><br>Role: <strong>{current_role.capitalize()}</strong></p>", unsafe_allow_html=True)

    st.sidebar.page_link("pages/elderly_dashboard.py", label="Home (Elderly)")
    st.sidebar.page_link("pages/games_menu.py", label="Cognitive Games")
    st.sidebar.page_link("pages/progress.py", label="Your Progress")
    st.sidebar.page_link("pages/memory_assistant.py", label="Memory Assistant")
    st.sidebar.page_link("pages/reminders.py", label="Daily Routine & Reminders")
    st.sidebar.page_link("pages/caregiver_dashboard.py", label="Caregiver Overview")
    st.sidebar.page_link("pages/settings.py", label="Settings & Accessibility")

    st.sidebar.divider()
    if current_role == "elderly":
        if st.sidebar.button("Switch to Caregiver Dashboard", key="sidebar_switch_cg", use_container_width=True):
            st.session_state.role = "caregiver"
            st.switch_page("pages/caregiver_dashboard.py")
    else:
        if st.sidebar.button("Switch to Elderly Dashboard", key="sidebar_switch_eld", use_container_width=True):
            st.session_state.role = "elderly"
            st.switch_page("pages/elderly_dashboard.py")

    st.sidebar.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="sidebar_signout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")
