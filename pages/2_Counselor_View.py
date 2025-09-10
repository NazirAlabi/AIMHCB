import streamlit as st
from modules import auth  # optional; used only to show users if available

# Guard: ensure system_variables exist (app.py should set this)
if "system_variables" not in st.session_state:
    st.error("System variables not initialized. Please start from app.py.")
    st.stop()

# Keep original minimal behavior, but make it safer / slightly more useful for Admins
if st.session_state.get("role") == "Admin":
    tab1, tab2, tab3 = st.tabs(["Users' Information", "Risk Distribution", "Failed Crisis ALerts"])

    with tab1:
        # Try to display a users table if auth.load_users is available and the file exists
        try:
            users = auth.load_users(st.session_state.system_variables['user_db_file'])
            if users:
                rows = []
                for username, info in users.items():
                    rows.append({
                        "username": username,
                        "name": info.get("name", "N/A"),
                        "email": info.get("email", "N/A"),
                        "phone": info.get("phone", "Not provided")
                    })
                st.table(rows)
            else:
                # preserve the original empty behavior while giving a helpful message
                st.info("No users found (user DB is empty).")
        except Exception:
            # If auth isn't available or reading failed, fall back to original simple table call
            st.table()

    # keep placeholders for the other tabs (you can populate these later)
    with tab2:
        st.info("Risk distribution visualization goes here.")
    with tab3:
        st.info("Failed crisis alerts list goes here.")

else:
    # preserve your original 'do nothing' behavior but give a helpful hint
    st.warning("Access denied. Counselor (Admin) role required to view this page.")
