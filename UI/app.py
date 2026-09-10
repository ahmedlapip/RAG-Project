from datetime import datetime
import streamlit as st
from Processing import upload_and_process_ui, find_user_projects
from Register import register, login
from Chat import chatbot_ui
import json


def init_session_state():

    defaults = {
        "logged_in": False,
        "user_info": None,
        "upload_done": False,
        "current_project_id": None,
        "chat_open": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def auth_screen():

    menu = ["Login", "Register"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        login()

    elif choice == "Register":
        register()


def upload_flow():
    st.title("Upload Documents")
    if not st.session_state.current_project_id:
        now = datetime.now()

        st.session_state.current_project_id = str(now.strftime("%Y%m%d%H%M%S"))

    uploaded = upload_and_process_ui(
        proj_id=st.session_state.current_project_id,
        user_name=st.session_state.user_info["name"],
    )

    if uploaded:
        st.session_state.upload_done = True
        st.session_state.chat_open = True

        st.rerun()


def chat_screen():

    st.title("ChatBot")

    chatbot_ui()


def sidebar_projects():

    user = st.session_state.user_info
    related_projects = user.get("related_projects", [])

    projects = find_user_projects(related_projects)
    project_list = projects.get("Projects", [])

    seen = set()
    unique_projects = []
    for p in project_list:
        key = (p.get("project_id"), p.get("project_name"))
        if key not in seen:
            seen.add(key)
            unique_projects.append(p)
    project_list = unique_projects

    st.sidebar.divider()

    if st.sidebar.button("➕ New Project", key="btn_new_project"):
        now = datetime.now()
        st.session_state.current_project_id = str(now.strftime("%Y%m%d%H%M%S"))
        st.session_state.upload_done = False
        st.rerun()

    st.sidebar.subheader("Your Projects")

    if not project_list:
        st.sidebar.info("No projects yet")
    else:
        for idx, project in enumerate(project_list):
            if st.sidebar.button(
                project["project_name"], key=f"btn_{project['project_id']}_{idx}"
            ):
                st.session_state.current_project_id = project["project_id"]
                st.success(f"Opened {project['project_name']}")


def main():

    init_session_state()

    if not st.session_state.logged_in:
        auth_screen()

        return

    sidebar_projects()

    if st.sidebar.button("Logout"):
        st.session_state.clear()

        st.rerun()

    if not st.session_state.upload_done:
        upload_flow()

    chat_screen()


if __name__ == "__main__":
    main()
