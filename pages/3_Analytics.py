import streamlit as st

st.set_page_config(page_title="Developer Analytics", page_icon="🛠️", layout="wide")

st.title("🛠️ Developer Analytics Dashboard")
st.markdown("Internal view for debugging and monitoring AI + user interactions.")

# Section: General session info
st.subheader("📂 Session Overview")
st.write("Inspect what's inside st.session_state")
# TODO: Optionally pretty-print session state keys/values for debugging

st.markdown("---")

# Section: Chat + Metrics
st.subheader("💬 Chat Interactions with Metrics")

# TODO: Loop over st.session_state.chat_history
#   - For each prompt/response, show:
#       - User prompt text
#       - Bot response (raw + formatted)
#       - Sentiment score + label
#       - Risk score + crisis level
#       - FEM metric (if available)
#       - Display the picture taken alongside metrics

# Example UI structure:
# for interaction in st.session_state.chat_history:
#     col1, col2 = st.columns([2, 3])
#     with col1:
#         st.image(interaction.get("photo"), caption="Captured Photo")  # if stored
#         st.metric("FEM", interaction.get("fem_score", 0.0))
#     with col2:
#         st.markdown(f"**User:** {interaction['user']}")
#         st.markdown(f"**Bot:** {interaction['bot']}")
#         st.write(f"Sentiment: {interaction.get('sentiment_label')} ({interaction.get('sentiment_score')})")
#         st.write(f"Risk Score: {interaction.get('risk_score')} / 10")
#         st.write(f"Crisis Level: {interaction.get('crisis_level')}")

st.markdown("---")

# Section: AI Calls Debugging
st.subheader("🤖 AI Call Internals")
# TODO: Display intermediate outputs of ai_calls (e.g., summaries, final input strings)
#       Useful for debugging prompt formatting and context handling

st.markdown("---")

# Section: Graphs / Visualizations
st.subheader("📊 Visual Analytics")
# TODO: Add plots here (e.g., risk scores over time, sentiment gradient chart)
# Example placeholder:
# st.line_chart([entry['risk_score'] for entry in st.session_state.chat_history])
