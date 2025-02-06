import streamlit as st
import json
import os
from datetime import datetime, timedelta

# --- Simple Authentication with Persistent Session --- #
USERS = {
    'kothasaikrishna': 'mypassword',
    'coder': 'password'
}
SESSION_TIMEOUT_DAYS = 10
SESSION_FILE = 'session.json'

# Save session to file
def save_session():
    session_data = {
        'logged_in': st.session_state.get('logged_in', False),
        'username': st.session_state.get('username', ''),
        'login_time': st.session_state.get('login_time', '')
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

# Load session from file
def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            session_data = json.load(f)
            st.session_state.update(session_data)

# Clear session file
def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# Login Function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['login_time'] = datetime.now().isoformat()
            save_session()
            st.query_params.clear()
        else:
            st.error("Invalid username or password")

# Check login state and session expiration
def is_session_valid():
    if 'logged_in' in st.session_state and 'login_time' in st.session_state:
        login_time = datetime.fromisoformat(st.session_state['login_time'])
        if datetime.now() - login_time < timedelta(days=SESSION_TIMEOUT_DAYS):
            return True
    return False

# Load session from file at startup
load_session()

# Main logic
if not is_session_valid():
    login()
else:
    username = st.session_state.get('username', 'default_user')  # Ensure username is initialized
    st.sidebar.write(f"Logged in as: {username}\n\n Hello!! {username}\n\n Your progress is saved in your local storage only")
    
    if st.sidebar.button("Logout"):
        for key in ['logged_in', 'username', 'login_time']:
            st.session_state.pop(key, None)
        clear_session()
        st.query_params.clear()
    # Load grouped problem data
    plan_file = 'problems.json'
    progress_file = f"progress_{username}.json"  # Save progress per user

    def load_plan():
        with open(plan_file, 'r') as f:
            return json.load(f)

    def load_progress():
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
        return {}

    def save_progress(progress):
        with open(progress_file, 'w') as f:
            json.dump(progress, f)

    # Initialize
    plan_data = load_plan()
    progress = load_progress()

    st.title("Love Babbar DSA 450 sheet")

    # Day selection
    day_list = [day['Day'] for day in plan_data]
    selected_day = st.selectbox("Select Day", day_list)

    # Filter the selected day data
    day_data = next(day for day in plan_data if day['Day'] == selected_day)
    topics = day_data['Topic']
    prerequisites = day_data['Prerequisites']
    problems = day_data['Problems']

    # Display Topic and Prerequisites
    st.header(f"{selected_day}: {topics}")

    st.subheader("Prerequisites")
    st.write(prerequisites)

    # Display Problems with Checkboxes and Links
    st.subheader("Problems")

    # Load or initialize progress for the selected day
    if selected_day not in progress:
        progress[selected_day] = {problem['name']: False for problem in problems}

    for problem in problems:
        col1, col2 = st.columns([4, 1])
        with col1:
            checked = st.checkbox(problem['name'], value=progress[selected_day].get(problem['name'], False))
            progress[selected_day][problem['name']] = checked
        with col2:
            if problem['link']:
                st.markdown(f"[Solve it]({problem['link']})", unsafe_allow_html=True)
            else:
                st.write("No link available")

    # Save progress button
    if st.button("Save Progress"):
        save_progress(progress)
        st.success("Progress saved successfully!")
