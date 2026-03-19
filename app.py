import streamlit as st
from agent import ask_agent

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI Research Assistant", page_icon="🤖", layout="wide")

# ---------------- Custom Styling ----------------
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("⚙️ Settings")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

    st.markdown("---")
    st.write("### About")
    st.write("🌐 Real-time AI Assistant")
    st.write("Uses LLM + Web Search + Memory")
    st.success("🟢 System Active")

# ---------------- Main UI ----------------
st.title("🤖 AI Research Assistant")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history (ChatGPT style)
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

# Chat input (bottom)
user_input = st.chat_input("Ask anything...")

if user_input:
    # Show user message instantly
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.chat_history.append(("user", user_input))

    # Show AI response with loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_agent(user_input)
            st.markdown(response)

    st.session_state.chat_history.append(("assistant", response))