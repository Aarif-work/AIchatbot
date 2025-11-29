from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import aiohttp, asyncio, time
from bs4 import BeautifulSoup
from typing import Dict, Any
from functools import lru_cache

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Stateful session storage
user_sessions = {}
PORTFOLIO_DATA = {}
PORTFOLIO_TEXT = ""
CACHE_LAST_FETCH = 0
CACHE_TTL_SECS = 15 * 60

@lru_cache(maxsize=100)
def get_cached_response(message: str) -> str:
    return None

PORTFOLIO_URL = "https://aarif-work.github.io/html/index.html"
SKILL_KEYS = ["flutter","dart","python","c++","javascript","mysql","iot","firebase"]

async def fetch_and_cache_portfolio():
    global PORTFOLIO_DATA, PORTFOLIO_TEXT, CACHE_LAST_FETCH
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=6)) as s:
            async with s.get(PORTFOLIO_URL) as r:
                html = await r.text()

        soup = BeautifulSoup(html, "html.parser")
        PORTFOLIO_TEXT = soup.get_text(separator=" ").lower()

        # --- dynamic skills ---
        skills_set = set()
        for span in soup.find_all("span"):
            t = (span.get_text() or "").strip()
            if t and len(t) < 30 and any(k in t.lower() for k in SKILL_KEYS):
                skills_set.add(t)
        skills = list(skills_set)[:8] or ["Flutter","Dart","Python","C++","IoT"]

        # --- dynamic projects (try known card class, else fallbacks) ---
        projects = []
        for card in soup.find_all("div", class_="portfolio-card"):
            h = card.find(["h3","h2"])
            if h: projects.append(h.get_text(strip=True))
        if not projects:
            for h in soup.find_all(["h3","h2"]):
                txt = h.get_text(strip=True)
                if any(w in txt.lower() for w in ["project","app","system","portfolio"]):
                    projects.append(txt)
        projects = (projects[:5] or ["Portfolio site"])

        PORTFOLIO_DATA = {
            "name": "Mohamed Aarif A",
            "role": "Flutter Developer & Programmer",
            "skills": skills,
            "projects": projects,
            "achievements": [],
            "full_text": PORTFOLIO_TEXT,
            "fetched_at": int(time.time())
        }
        CACHE_LAST_FETCH = PORTFOLIO_DATA["fetched_at"]
    except Exception:
        # graceful fallback
        PORTFOLIO_DATA = {
            "name": "Mohamed Aarif A",
            "role": "Flutter Developer & Programmer",
            "skills": ["Flutter","Dart","Python","C++","IoT"],
            "projects": ["Nadi Bio Band"],
            "achievements": [],
            "full_text": "mohamed aarif flutter developer programmer python dart c++ iot",
            "fetched_at": int(time.time())
        }
        CACHE_LAST_FETCH = PORTFOLIO_DATA["fetched_at"]

async def ensure_cache():
    if time.time() - CACHE_LAST_FETCH > CACHE_TTL_SECS or not PORTFOLIO_DATA:
        await fetch_and_cache_portfolio()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, str]:
    try:
        await ensure_cache()
        
        if request.session_id not in user_sessions:
            user_sessions[request.session_id] = {"history": []}
        
        session = user_sessions[request.session_id]
        context = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in session["history"][-3:]])
        
        system_prompt = f"""You are an AI assistant providing information about Mohamed Aarif A. Be natural, calm, and respectful in your responses.
        
INFO: {PORTFOLIO_DATA['name']}, {PORTFOLIO_DATA['role']}
SKILLS: {', '.join(PORTFOLIO_DATA['skills'])}
PROJECTS: {', '.join(PORTFOLIO_DATA['projects'])}

Previous conversation:
{context}
        
Respond in a human-like, smooth, and friendly manner. Keep answers clear and helpful."""
        
        full_prompt = f"{system_prompt}\n\nUser: {request.message}\nResponse:"
        response = await asyncio.to_thread(llm.invoke, full_prompt)
        
        session["history"].append({"user": request.message, "ai": response.content})
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]
        
        return {"reply": response.content}
    except Exception as e:
        return {"reply": "I'm having trouble right now. Please try again."}

@app.options("/chat")
async def chat_options():
    return {"message": "OK"}

@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Aarif Portfolio Chatbot API is running", "version": "2.0.0"}