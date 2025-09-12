# ⚡ SinghRopar Chatbot App  

A dynamic chatbot server built with **FastAPI** and powered by the **Groq API**.  
Designed for users with **limited hosting capabilities**, this lightweight server allows you to run and manage a chatbot seamlessly without requiring heavy infrastructure.  

---

## 🚀 Features  

- **Start/stop chatbot server easily**  
- **Configure Groq API key via UI**  
- **Change chatbot system prompt/content dynamically**  
- **View logs and request/response stats in real time**  
- **Lightweight and extensible FastAPI backend**  

---

## ⚙️ Hosting & Performance  

This project is optimized for **low-resource environments**.  
Currently tested on an **AWS t3a.medium (2 vCPU, 4 GB RAM)** instance.  

- Groq is used as the **fast AI inference layer**.  
- Instead of a heavy RAG pipeline, a **minimal hybrid approach** is implemented:  
  - The API maintains **full context in memory** rather than generating embeddings for large reference documents.  
  - To reduce excessive token usage, each **prompt-response pair** is stored in a **lightweight vector database (Annoy by Spotify)**.  
  - For embeddings, **all-MiniLM-L6-v2** is used — a compact and efficient model that allows quick similarity checks.  
  - If a question was already asked, the chatbot retrieves the **previous response** directly, saving **Groq API calls** and improving speed.  

This balance ensures that even on smaller servers, the chatbot runs smoothly while minimizing costs and resource usage.  
