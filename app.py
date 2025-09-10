from re import S
from click import clear
import streamlit as st
from modules import auth
import time
from groq import Groq
import os


st.set_page_config(
        page_title="Authenticated Mental Health Chatbot",
        page_icon="🧠",
        layout="wide"
    )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app.py location
USER_DB_FILE = os.path.join(BASE_DIR, "data", "users.txt")
PROFILE_DIR = os.path.join(BASE_DIR, "data", "profiles")



# Initialize session state variables if not already set
if True:
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'system_variables' not in st.session_state:
        st.session_state.system_variables={
            'user_db_file': USER_DB_FILE,
            'profile_dir': PROFILE_DIR,
            'resource_1': None,
            'resource_2': None,
            'groq_client': Groq(api_key="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"),
            'model': "llama-3.3-70b-versatile",
            'detector': None,
            'crisis_keywords': [],
            'counselor_credentials':{},
            'counselor_email':"aerickegreene12@gmail.com",
            'smtp_email': "",
            'smtp_password':""
        }
    if 'chat_info' not in st.session_state:
        st.session_state.chat_info={
            'first_prompt':True,
            'fem_feature':False,
            'fem_acknowledged':True,
            'pp':"",
            'chat_summary':""
        }
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'role' not in st.session_state:
        st.session_state.role=None
        counselor_credentials=st.session_state.system_variables.get("counselor_credentials", {})

# If not authenticated, show login/sign-up page
if not st.session_state.authenticated:

    st.title("🧠 Authenticated Mental Health Chatbot")
    st.markdown("🔐 **Secure, Personalized AI Mental Health Support**")
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Login", "Sign Up", "Counselor Resources", "Developer Analytics","About"])
    # Login Tab
    with tab1:
        st.subheader("🔑 Login")
        with st.form(key='login_form'):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            if login_button:
                user_info = auth.authenticate_user(username, password, st.session_state.system_variables['user_db_file'])
                if user_info:
                    st.success(f"✅ Login successful! \nWelcome back, {user_info['name']}!")
                    st.info("Loading your dashboard...")
                    st.snow()
                    st.session_state.user_info = user_info
                    st.session_state.username = username
                    st.session_state.chat_info['pp'] = auth.load_user_profile(username,     PROFILE_DIR=st.session_state.system_variables['profile_dir']) or ""
                    profile_status = "loaded" if st.session_state.chat_info['pp'] else "not found"
                    st.info(f"Personal profile {profile_status}.")
                    st.session_state.authenticated = True
                    st.session_state.role="User"
                    time.sleep(1)
                    # Redirect to dashboard page
                    st.switch_page(r"pages/1_User_Dashboard.py")
                else:
                    st.error("❌ Invalid username or password. Please try again.")
    # Sign Up Tab
    with tab2:
        st.subheader("🆕 Sign Up")
        with st.form(key='signup_form'):
            new_username = st.text_input("Choose a Username")
            new_email = st.text_input("Email Address")
            new_name = st.text_input("Full Name")
            new_phone = st.text_input("Phone Number (optional)")
            new_password = st.text_input("Create a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up", on_click=clear)
            if signup_button:
                if not new_username or not new_email or not new_name or not new_password:
                    st.error("❌ All fields except phone number are required.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match. Please try again.")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                else:
                    users = auth.load_users(st.session_state.system_variables['user_db_file'])
                    if new_username in users:
                        st.error("❌ Username already exists. Please choose a different one.")
                    else:
                        import re
                        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                        if not re.match(pattern, new_email):
                            st.warning("Invalid email format.")
                            st.warning("Please enter a valid email address.")
                        else:
                            auth.save_user(new_username, new_email, new_name, new_phone, new_password, st.session_state.system_variables['user_db_file'])
                            auth.save_user_profile(new_username, "", st.session_state.system_variables['profile_dir'])
                            st.success("✅ Sign up successful! You can now log in.")
                            st.info("Please log in using the Login tab.")
                            time.sleep(1) 
                            st.rerun()
    # Counselor Resources Tab
    with tab3:
        st.subheader("🛠️Counselor Login")
        st.markdown("If you are a counselor and would like to access the counselor resources, please contact the system administrator to obtain login credentials.")
        tries=0
        tries_limit=3
        with st.form(key='counselor_login_form'):
            counselor_username = st.text_input("Counselor Username")
            counselor_password = st.text_input("Counselor Password", type="password")
            counselor_login_button = st.form_submit_button("Login as Counselor")
            if st.session_state.authenticated is False and st.session_state.role is None:
                if counselor_login_button:
                    tries+=1
                    if tries<=tries_limit:
                        if (counselor_username in counselor_credentials and 
                            counselor_credentials[counselor_username] == counselor_password):
                            st.success("✅ Counselor login successful!")
                            st.info("Accessing counselor resources...")
                            with st.spinner():
                                time.sleep(2)       
                            st.session_state.user_info={}
                            st.session_state.username="Counselor"
                            st.session_state.pp=""
                            st.session_state.authenticated=True
                            st.session_state.role="Admin"
                            st.success("You are now logged in as a Counselor.")
                            st.switch_page(r"pages/2_Counselor_View.py")
                        else:
                            st.warning("Invalid Credentials")
                            if tries_limit-tries!=0:
                                st.warning(f"{tries_limit-tries} more failed attempt will disable Admin privileges") 
                    else:
                        st.warning("Admin Privileges Disabled")
                        st.session_state.role="User"

    # Developer Analytics Tab
    with tab4:
        st.subheader("📊 Developer Analytics")
        st.markdown("Analytics features will be available in future updates.") 
        st.info("This section is under development. Please check back later.")
    
    # About Tab
    with tab5:
        st.subheader("ℹ️ About This App")
        st.markdown("---")
        st.markdown("""
        **AIM Health Chatbot** is designed to provide secure and personalized mental health support using AI technology. 
        It offers a confidential space for users to share their thoughts and feelings, while also providing resources for crisis situations.
        
        ### Features:
        - **User Authentication**: Secure login and sign-up process to protect user data.
        - **Personalized Support**: AI-driven responses tailored to individual user needs.
        - **Crisis Intervention**: Immediate alerts to counselors in high-risk situations.
        - **Counselor Access**: Dedicated resources and tools for mental health professionals.
        
        ### Technologies Used:
        - Streamlit for the web interface
        - Groq for AI model integration
        - VADER and FER for sentiment and facial expression analysis
        - SMTP for email notifications
        
        ### Contact:
        For support or inquiries, please contact the AIMHCB Team at
                    - Email: aerickegreene@gmsil.com
                    - Phone: +233-59-879-5722
                    """)
                         
    st.markdown("---")
    st.markdown("ℹ️ Developed by the AIMHCB Team.")
else:
    st.switch_page(r"pages/1_User_Dashboard.py")


    
    