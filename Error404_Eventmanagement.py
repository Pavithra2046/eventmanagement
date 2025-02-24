import streamlit as st
import pandas as pd
import datetime
import sqlite3

# Initialize Database
def init_db():
    conn = sqlite3.connect('eventsm.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, organizer TEXT, date TEXT, start_time TEXT, end_time TEXT, description TEXT, capacity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, user_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS registrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, name TEXT, email TEXT, phone TEXT)''')
    conn.commit()
    conn.close()

init_db()

def main():
    st.set_page_config(layout="wide")

    # Custom CSS for styling
    st.markdown("""
        <style>
            .main { background-color: #e0ffff; }
            .stTextInput > div > div > input, 
            .stTextArea > div > textarea, 
            .stDateInput > div > input, 
            .stNumberInput > div > input, 
            .stSelectbox > div > div > div, 
            .stTimeInput > div > input {
                background-color: #b2d8d8;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Event Management</h1>", unsafe_allow_html=True)

    # Initialize session state variables
    if "user_type" not in st.session_state:
        st.session_state["user_type"] = None
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None

    # Role Selection and Authentication
    if not st.session_state["logged_in"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            creator_button = st.button("🎨 Join as Event Creator", use_container_width=True)
            joiner_button = st.button("🚀 Join as Event Joiner", use_container_width=True)

            if creator_button:
                st.session_state["user_type"] = "Event Creator"
            if joiner_button:
                st.session_state["user_type"] = "Event Joiner"

            if st.session_state["user_type"]:
                st.subheader(f"Sign Up or Login as {st.session_state['user_type']}")
                action = st.radio("Choose Action", ["Login", "Sign Up"])
                username_input = st.text_input("Username", key="username_input")
                password_input = st.text_input("Password", type="password", key="password_input")
                action_button = st.button(action, use_container_width=True, key="action_button")

                if action_button:
                    conn = sqlite3.connect('eventsm.db')
                    c = conn.cursor()
                    if action == "Sign Up":
                        try:
                            c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
                                      (username_input, password_input, st.session_state["user_type"]))
                            conn.commit()
                            st.success("Account created successfully! Please login.")
                        except sqlite3.IntegrityError:
                            st.error("Username already exists. Please choose another.")
                    else:  # Login
                        c.execute("SELECT * FROM users WHERE username=? AND password=? AND user_type=?",
                                  (username_input, password_input, st.session_state["user_type"]))
                        user = c.fetchone()
                        if user:
                            st.session_state["logged_in"] = True
                            st.session_state["current_user"] = username_input
                            st.success(f"Welcome, {username_input}! 🎉")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")
                    conn.close()

                # Back Button
                if st.button("🔙 Back", use_container_width=True, key="back_button"):
                    st.session_state["user_type"] = None

    # Logged-in User Interface
    if st.session_state["logged_in"]:
        st.sidebar.success(f"Logged in as {st.session_state.get('user_type', 'User')}")

        # Event Creator Interface
        if st.session_state.get("user_type") == "Event Creator":
            st.title("Create an Event")
            event_name = st.text_input("Event Name")
            event_organizer = st.text_input("Event Organizer")
            event_date = st.date_input("Event Date", min_value=datetime.date.today())
            event_start_time = st.time_input("Start Time")
            event_end_time = st.time_input("End Time")
            event_capacity = st.number_input("Capacity", min_value=1, step=1)
            event_description = st.text_area("Event Description")
            create_event = st.button("Create Event")

            if create_event:
                if event_name and event_organizer and event_description:
                    conn = sqlite3.connect('eventsm.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO events (name, organizer, date, start_time, end_time, description, capacity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (event_name, event_organizer, event_date, event_start_time.strftime("%H:%M"), event_end_time.strftime("%H:%M"), event_description, event_capacity))
                    conn.commit()
                    conn.close()
                    st.success("🎉 Event Created Successfully!")
                else:
                    st.error("⚠️ Please fill out all fields before creating an event.")

        # Event Joiner Interface
        elif st.session_state.get("user_type") == "Event Joiner":
            st.title("Join an Event")
            st.write("Browse and join events!")

            # Load events from database
            conn = sqlite3.connect('eventsm.db')
            c = conn.cursor()
            c.execute("SELECT id, name, organizer, date, start_time, end_time, capacity FROM events")
            events = pd.DataFrame(c.fetchall(), columns=["ID", "Event Name", "Organizer", "Date", "Start Time", "End Time", "Capacity"])
            conn.close()

            st.write("### Available Events")
            for idx, row in events.iterrows():
                with st.expander(f"{row['Event Name']} | {row['Date']} {row['Start Time']} - {row['End Time']} | Capacity: {row['Capacity']}"):
                    st.write(f"**Event:** {row['Event Name']}")
                    st.write(f"**Organizer:** {row['Organizer']}")
                    st.write(f"**Date:** {row['Date']}")
                    st.write(f"**Start Time:** {row['Start Time']}")
                    st.write(f"**End Time:** {row['End Time']}")
                    st.write(f"**Capacity:** {row['Capacity']}")

                    # Use st.form to handle registration
                    with st.form(key=f"register_form_{idx}"):
                        st.write("### Register for this Event")
                        name = st.text_input("Your Name", key=f"name_{idx}")
                        email = st.text_input("Your Email", key=f"email_{idx}")
                        phone = st.text_input("Your Phone Number", key=f"phone_{idx}")
                        submit_button = st.form_submit_button("Register")

                        if submit_button:
                            if name and email and phone:
                                conn = sqlite3.connect('eventsm.db')
                                c = conn.cursor()
                                c.execute("INSERT INTO registrations (event_id, name, email, phone) VALUES (?, ?, ?, ?)",
                                          (row['ID'], name, email, phone))
                                conn.commit()
                                conn.close()
                                st.success("🎉 Successfully registered for the event!")
                            else:
                                st.error("⚠️ Please fill out all registration fields.")

        # Logout Button
        if st.sidebar.button("Logout"):
            for key in ["user_type", "logged_in", "current_user"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
