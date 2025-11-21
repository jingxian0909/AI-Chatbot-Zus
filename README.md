# AI Chatbot Engineer Assessment – ZUS Coffee Chatbot  
Backend: FastAPI (Python) • Vector DB: Pinecone • DB: Supabase
Frontend: React (Vercel) • Deployment: Heroku (Backend)  

---

##Overview

This project is simple AI Chatbot for Zus Coffee.  
It delivers a full end-to-end AI chatbot with:

- Multi-turn conversation memory  
- Agentic planner/controller  
- Tool calling (Calculator, RAG Product Search, Outlets Text2SQL Query)  
- Custom FastAPI backend  
- RAG using Pinecone  
- Safe Text2SQL execution  
- Robust error handling  
- React chat frontend with planner logs  
- Production deployment (Heroku + Vercel)  

---

#System Architecture

User → React Chat UI (Vercel) → FastAPI Backend (Heroku) → Planner / Controller (Calculator, RAG Search, Text2SQL)

---

#Features

### ✓ **1. Conversation Memory**
Tracks multi-turn slots such as:
- location (e.g., PJ, KL)

Stored inside planner state.

---

### ✓ **2. Agentic Planner**
A rule-based decision engine that chooses one of:

- Ask follow-up  
- Call calculator  
- Call `/products` RAG  
- Call `/outlets` Text2SQL  
- Finish response  

---

### ✓ **3. Tool Calling Integration**

#### **/calc**  
Evaluates arithmetic expressions safely.

#### **/products (RAG)**  
- Scrapes ZUS Coffee Drinkware  
- Embeds using OpenAi embeddings model
- Stores vectors in **Pinecone**  
- Retrieves top-k results  
- Generates final summary with LLM  

#### **/outlets (Text2SQL)**  
- NL → SQL via LLM  
- Safe SQL validator  
- No mutations allowed  
- Executes via Supabase

---

### ✓ **4. Safety & Security**
- No wildcard `SELECT *`  
- No destructive SQL  
- Strict column/table whitelist  
- Parameterized queries  
- No API keys in repo  

---

### ✓ **5. Unhappy Flow Handling**
Supports:

- Missing parameters  
- Invalid calc expressions  
- SQL injection attempts  

---

### ✓ **7. Frontend Chat UI**
React interface includes:

- Chat message bubbles  
- Streaming-like responses  
- Planner “decisions” section  
- Tool call results  
- LocalStorage conversation saving  
- Slash commands:  
  - `/calc`  
  - `/products`  
  - `/outlets`  
  - `/reset`

---

# Backend Setup (Local)

### 1. Create virtual environment
```
1. venv/bin/activate
2. Install dependencies
3. Create .env
(Not committed to GitHub)
PINECONE_API_KEY=xxxx
SUPABASE_API_KEY=xxxx
SUPABASE_URL=xxxx
OPENAI_API_KEY=xxxx
API_BASE_URL=xxxx

4.Data Preporcess (Products and Outlets)
uv run scrapeData.py  
uv run dataProcess.py   
uv run sql_convert.py
Go to Supabase and execute the outlets.sql
This will:
Scrape Drinkware
Embed using openai embeddings
Upsert into Pinecone vector DB
Insert into Supabase

5. Run FastAPI
uvicorn main:app --reload

🔌 API Endpoints
🛒 GET /products?query=...
☕ GET /outlets?query=...```


# Frontend Setup (Local)
npm start


