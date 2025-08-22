import streamlit as st
from chatbot_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# -----------------
# UTILITY FUNCTIONS
# -----------------

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        st.session_state['thread_labels'][thread_id] = f"Chat {len(st.session_state['chat_threads'])}"

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def export_chat_as_txt(chat_history):
    txt_content = ""
    for msg in chat_history:
        role = msg["role"].capitalize()
        content = msg["content"]
        txt_content += f"{role}: {content}\n\n"
    return txt_content

# -----------------
# SESSION SETUP
# -----------------

st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖", layout="wide")

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'thread_labels' not in st.session_state:
    st.session_state['thread_labels'] = {}

add_thread(st.session_state['thread_id'])

for idx, tid in enumerate(st.session_state['chat_threads'], start=1):
    if tid not in st.session_state['thread_labels']:
        st.session_state['thread_labels'][tid] = f"Chat {idx}"

# -----------------
# SIDEBAR
# -----------------

st.sidebar.title("🤖 LangGraph Chatbot")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    reset_chat()

st.sidebar.subheader("💬 My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    label = st.session_state['thread_labels'].get(thread_id, str(thread_id))
    if st.sidebar.button(label, use_container_width=True):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": msg.content})

        st.session_state['message_history'] = temp_messages

# -----------------
# MAIN CHAT UI
# -----------------

st.markdown(
    """
    <style>
    /* User bubble */
    .user-bubble {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 0 18px;
        margin: 8px 0;
        display: inline-block;
        max-width: 75%;
        font-size: 15px;
        float: right;
        clear: both;
        word-wrap: break-word;
    }
    /* Assistant bubble */
    .assistant-bubble {
        background: #f1f0f0;
        color: #111;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 0;
        margin: 8px 0;
        display: inline-block;
        max-width: 75%;
        font-size: 15px;
        float: left;
        clear: both;
        word-wrap: break-word;
    }
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .assistant-bubble { background: #3a3b3c; color: #e4e6eb; }
        .user-bubble { background: linear-gradient(135deg, #34b7f1, #0a84ff); }
    }
    /* Typing indicator (3 dots animation) */
    .typing {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 18px;
        background: #3a3b3c;
        color: white;
        font-size: 14px;
        margin: 8px 0;
        float: left;
        clear: both;
    }
    .typing span {
        height: 8px;
        width: 8px;
        background-color: white;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: blink 1.4s infinite both;
    }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
        0% { opacity: .2; }
        20% { opacity: 1; }
        100% { opacity: .2; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💬 LangGraph Chatbot")

# Display history
for message in st.session_state['message_history']:
    if message['role'] == 'user':
        st.markdown(f"<div class='user-bubble'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-bubble'>{message['content']}</div>", unsafe_allow_html=True)

# Download button
if st.session_state['message_history']:
    txt_file = export_chat_as_txt(st.session_state['message_history'])
    st.download_button(
        label="📄 Download Chat (.txt)",
        data=txt_file,
        file_name="chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

# -----------------
# CHAT INPUT + RESPONSE
# -----------------

user_input = st.chat_input("Type your message here...")

if user_input and isinstance(user_input, str):
    # User bubble
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

    CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

    # Assistant typing animation
    response_placeholder = st.empty()
    response_placeholder.markdown(
        "<div class='typing'><span></span><span></span><span></span></div>",
        unsafe_allow_html=True
    )

    assistant_text = ""
    for message_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=str(user_input))]},  # force string
        config=CONFIG,
        stream_mode="messages"
    ):
        assistant_text += message_chunk.content or ""
        response_placeholder.markdown(
            f"<div class='assistant-bubble'>{assistant_text}▌</div>",
            unsafe_allow_html=True
        )

    # Final clean response
    response_placeholder.markdown(
        f"<div class='assistant-bubble'>{assistant_text}</div>",
        unsafe_allow_html=True
    )

    st.session_state['message_history'].append({"role": "assistant", "content": assistant_text})
