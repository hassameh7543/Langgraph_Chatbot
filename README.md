# 💬 LangGraph Chatbot

An advanced **multi-threaded chatbot** built with [Streamlit](https://streamlit.io/), [LangGraph](https://www.langchain.com/langgraph), and [Groq LLM](https://groq.com/).  
It supports **conversation threads**, **chat history persistence with SQLite**, **downloadable chat transcripts**, and a **beautiful chat UI with typing animations**.  

---

## 🚀 Features

- **Multi-threaded Conversations**  
  Each new chat creates a unique thread (`thread_id`) stored in SQLite.  
- **Persistent Memory**  
  Conversations are checkpointed and can be reloaded at any time.  
- **Custom Chat UI**  
  Styled chat bubbles with light/dark mode and animated typing indicator.  
- **Groq-Powered AI**  
  Uses `ChatGroq` with `openai/gpt-oss-120b` model.  
- **Download Chat as TXT**  
  Export your full chat history with one click.  
- **Streamed Responses**  
  AI replies stream live with a typing effect.  

---



## 📂 Project Structure

