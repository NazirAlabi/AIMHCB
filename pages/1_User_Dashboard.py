from matplotlib.pylab import f
import streamlit as st
from sympy import im
from modules import auth, analysis, ai_calls, crisis
import time
import logging
import os
from groq import Groq
import os

st.set_page_config(
        page_title="Authenticated Mental Health Chatbot",
        page_icon="🧠",
        layout="wide"
    )


# Guard: ensure system_variables exist (app.py should set this)
if True:   
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = True
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {'name': 'Demo User', 'email': '', 'phone': 'Not provided'}
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'system_variables' not in st.session_state:
        st.session_state.system_variables={
            'user_db_file': r"C:\Users\Nazir Alabi\AIMHCB-Complete-\data\users.txt",
            'profile_dir': r"C:\Users\Nazir Alabi\AIMHCB-Complete-\data\profiles\ ",
            'resource_1': None,
            'resource_2': None,
            'groq_client': Groq(api_key="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"),
            'model': "llama-3.3-70b-versatile",
            'detector': None,
            'crisis_keywords': [],
            'counselor_credentials':{}
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

# Load essential system variables
crisis_keywords= st.session_state.system_variables.get("crisis_keywords", [])
groq_client=st.session_state.system_variables.get("groq_client", None)
model=st.session_state.system_variables.get("model", "llama-3.3-70b-versatile")
resource_1=st.session_state.system_variables.get("resource_1", "")
resource_2=st.session_state.system_variables.get("resource_2", "")
crisis_level="NONE"
risk_score=0
sentiment_label="Neutral"
sentiment_score=0.0
chat_context=""

if "system_variables" not in st.session_state:
    st.error("System variables not initialized. Please start from app.py.")
    st.stop()

@st.cache_resource
def detector_cache():
    detector=analysis.load_fem_model()
    return detector


if st.session_state.authenticated:
    user_info = st.session_state.user_info
    username = st.session_state.username
    
    with st.sidebar:
        st.markdown("### User Dashboard")
        st.write(f"**Username:** {username}")
        st.write(f"Name: {user_info.get('name', 'N/A')}")
        st.write(f"Email: {user_info.get('email', 'N/A')}")
        st.write(f"Phone: {user_info.get('phone', 'N/A')}")
        if st.button("Logout"):
            for key in ["authenticated", "user_info", "username", "chat_history", 
            "first_prompt", "fem_acknowledged", "pp", "groq_client", "model"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("app.py")
        st.markdown("---")
        st.header("ℹ️ Enhanced Features")
        st.write("✅ **Personalized responses**")
        st.write("✅ **Real-time sentiment analysis**")
        st.write("✅ **Crisis risk assessment**")
        st.write("✅ **Professional mental health support**")
        st.markdown("---")
        st.header("🚨 Crisis Resources")
        st.write(f"**{resource_1}**")
        st.info("Developed by the AIMHCB Team.")

    st.subheader(f"💬 Chat with WellBot - Hello {user_info['name']}!")
    st.session_state.chat_info["fem_feature"]=st.checkbox(label="Enable Facial Expression Analysis", value=False)
    facialExp=st.session_state.chat_info["fem_feature"]
    if facialExp:
        st.session_state.system_variables['detector']=detector_cache()
        input_col, response_col = st.columns([1, 1])
    else:
        input_col, response_col = st.columns([2, 3])
    with input_col:
        st.subheader("💭 Your Message")
        if facialExp:
            input_area, photo_area = st.columns([4, 1])
            with input_area:
                with st.form(key='user_input_form', clear_on_submit=True, enter_to_submit=True):
                    user_input = st.text_area("Share what's on your mind...",
                                    height=90)
                    send_clicked= st.form_submit_button("Send")
            with photo_area:
                photo= st.camera_input("Take a selfie", key="camera", on_change=None)
        else:
            with st.form(key='user_input_form', clear_on_submit=True, enter_to_submit=True):
                user_input = st.text_area("Share what's on your mind...",
                                height=90).strip()
                send_clicked= st.form_submit_button("Send")

        if st.button("Clear Chat 🗑️"):
            if 'chat_history' in st.session_state:
                st.session_state.chat_history = []
            try:
                st.session_state.chat_info["first_prompt"]=True
            except Exception as e:
                logging.error("First prompt item in chat_info reassignment to true failed!")
                logging.error(f"{e}")

            st.rerun()

        if send_clicked and user_input:
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            if facialExp:
                fem=analysis.get_fem(facialExp, st.session_state.system_variables['detector'], photo)
            else:
                fem=0.0
            sentiment_score, risk_score, crisis_level, sentiment_label = analysis. analyze_sentiment_and_risk(user_input, CRISIS_KEYWORDS=crisis_keywords)
            if st.session_state.chat_history:
                st.session_state.chat_info["first_prompt"]=False
            try:
                if st.session_state.chat_info["first_prompt"]:
                    chat_context=auth.load_user_profile(username, st.session_state.system_variables.get('profile_dir', '')) or ""
                else:
                    chat_context=ai_calls.summarize_chat_history(st.session_state.chat_history, chat_context if chat_context else "", groq_client=groq_client, model= model)
            except Exception:
                chat_context=""
            final_input=f"Context: {chat_context}\nUser: {user_input}"
            bot_response=ai_calls.generate_with_sentiment(
                groq_client,
                model,
                final_input,
                0.0 if fem is None else fem,
                user_info['name'],
                risk_score if risk_score else 1,
                st.session_state.chat_info['fem_acknowledged'],
                st.session_state.chat_info["first_prompt"],
                chat_context,
            )
            if crisis_level=='SEVERE':
                crisis.crisis(st.session_state.system_variables['counselor_email'], st.session_state.system_variables['smtp_email'], st.session_state.system_variables['smtp_password'], user_info=user_info, user_name=username, user_message=user_input, risk_score=st.session_state.risk_score, alerts_path=st.session_state.alerts_path)
            st.session_state.chat_history.append({
                'user': user_input,
                'bot': bot_response,
                'timestamp': time.time(),
                'risk_score': risk_score,
                'crisis_level': crisis_level
            })
        elif send_clicked and not user_input:
            st.warning("Please enter a message before first.")
    with response_col:
        if crisis_level in locals() and crisis_level=='SEVERE':
            crisis.display_crisis_intervention(risk_score=risk_score, resources_1=resource_1, resources_2=resource_2)
        st.subheader("🤖 WellBot's Response")
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            last_interaction = st.session_state.chat_history[-1]
            st.markdown(f"**You:** {last_interaction['user']}...")
            with st.container(border=True, horizontal_alignment="center"):
                with st.chat_message(name='ai'):
                    st.write(f"##### ***{last_interaction['bot']}***")
            st.write(f"###### Response generated at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_interaction['timestamp']))} \n Risk Score: {last_interaction['risk_score']}/10")
        else:
            st.info("💡Your conversation will appear here.")
            st.write(f"**Tell me what's on your mind, {user_info['name']}**")
    st.markdown("---")
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### 🕒 Conversation History")
        for interaction in reversed(st.session_state.chat_history[-10:]):
            with st.expander(f"**You:** {interaction['user'][:30]}..."):
                with st.container():
                    st.markdown("**Wellbot:**")
                    st.markdown(f"{interaction['bot']}")
                    st.info(f"*Response generated at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(interaction['timestamp']))}*")
    else:
        st.info("💡 Your conversation history will appear here.")

    st.markdown("---")
    st.subheader("📝Quick Prompts")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("I'm feeling anxious"):
            st.session_state["q_prompt"]="I'm feeling anxious. Can you help me out?"
    with col2:
        if st.button("I'm feeling really good today"):
            st.session_state["q_prompt"]="I'm feeling really good today!"
    with col3:
        if st.button("I'm feeling a bit down"):
            st.session_state["q_prompt"]="I'm feeling a bit down."
    if "q_prompt" in st.session_state:
        q_prompt = st.session_state.q_prompt
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'first_prompt' not in st.session_state:
            st.session_state.chat_info["first_prompt"] = True
        if facialExp:
            if photo: fem=analysis.get_fem(facialExp, st.session_state.system_variables['detector'], photo)
            else: fem=0.0
        sentiment_score, risk_score, crisis_level, sentiment_label=analysis.analyze_sentiment_and_risk(q_prompt, crisis_keywords)
        response=ai_calls.generate_with_sentiment(
            groq_client,
            model,
            q_prompt,
            fem if facialExp else 0.0,
            user_info['name'],
            risk_score,
            st.session_state.chat_info['fem_acknowledged'],
            st.session_state.chat_info["first_prompt"],
            "",
        )

        st.session_state.chat_history.append({
                'user': st.session_state.q_prompt,
                'bot': response,
                'timestamp': time.time(),
                'risk_score': risk_score,
                'crisis_level': crisis_level
            })