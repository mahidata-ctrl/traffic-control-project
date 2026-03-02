import streamlit as st
import pandas as pd

# Set the page configuration
st.set_page_config(page_title="Railway Management System", page_icon="🚆")

# Initialize session state to keep track of user login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
# Only show the Dashboard if the user is logged in
pages = ["Home", "Train Timings", "Login", "Signup"]
if st.session_state["logged_in"]:
    pages.append("Dashboard")

choice = st.sidebar.radio("Go to:", pages)

# --- PAGES ---

if choice == "Home":
    st.title("🚆 Railway Management System")
    st.write("Your one-stop solution for train management and timings.")

elif choice == "Train Timings":
    st.title("Train Timings (Mumbai Region)")
    
    # Using a dictionary and Pandas DataFrame to manage table data
    data = {
        "Train No": ["12345", "67890"],
        "Train Name": ["Express Train", "Fast Train"],
        "Departure Time": ["08:00 AM", "09:30 AM"],
        "Arrival Time": ["10:00 AM", "11:30 AM"]
    }
    df = pd.DataFrame(data)
    
    # Display the dataframe as a clean table
    st.table(df)

elif choice == "Signup":
    st.title("Signup")
    # Streamlit Forms group inputs together
    with st.form("signup_form"):
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        submit_signup = st.form_submit_button("Signup")
        
        if submit_signup:
            if new_user and new_pass:
                st.success("Signup Successful! (Ready to connect to a database!)")
            else:
                st.error("Please fill out all fields.")

elif choice == "Login":
    st.title("Login")
    with st.form("login_form"):
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        
        if submit_login:
            if user and password: # Simple validation
                st.session_state["logged_in"] = True
                st.session_state["username"] = user
                st.success("Login Successful! Navigate to your Dashboard.")
            else:
                st.error("Please enter both username and password.")

elif choice == "Dashboard":
    st.title("Dashboard")
    st.subheader(f"Welcome, {st.session_state['username']}!")
    
    st.write("**Your Recent Bookings:**")
    st.markdown("- **Booking ID:** 12345 | **Train:** Deccan Express | **Date:** 2024-10-20")
    st.markdown("- **Booking ID:** 67890 | **Train:** Shatabdi Express | **Date:** 2024-10-22")
    
    st.write("---")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun() # Refresh the app to update the sidebar
