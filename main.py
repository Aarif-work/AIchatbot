from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import aiohttp, asyncio, time
from bs4 import BeautifulSoup
from typing import Dict, Any
import hashlib
import json

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
CACHE_LAST_FETCH = 0
CACHE_TTL_SECS = 15 * 60
response_cache = {}
RESPONSE_CACHE_TTL = 300
PORTFOLIO_ETAG = ""

PORTFOLIO_URL = "https://aarif-work.github.io/html/index.html"
SKILL_KEYS = ["flutter","dart","python","c++","javascript","mysql","iot","firebase"]

async def fetch_and_cache_portfolio():
    global PORTFOLIO_DATA, CACHE_LAST_FETCH, PORTFOLIO_ETAG
    try:
        headers = {}
        if PORTFOLIO_ETAG:
            headers["If-None-Match"] = PORTFOLIO_ETAG
            
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=6)) as s:
            async with s.get(PORTFOLIO_URL, headers=headers) as r:
                if r.status == 304:
                    return
                    
                PORTFOLIO_ETAG = r.headers.get("ETag", "")
                html = await r.text()

        soup = BeautifulSoup(html, "html.parser")
        
        skills = []
        projects = []
        
        for elem in soup.find_all(["span", "h3", "h2", "p"]):
            text = elem.get_text(strip=True)
            if any(k in text.lower() for k in SKILL_KEYS) and len(text) < 50:
                skills.append(text)
            elif any(w in text.lower() for w in ["project", "app"]) and len(text) < 100:
                projects.append(text)
                
        PORTFOLIO_DATA = {
            "name": "Mohamed Aarif A",
            "role": "Flutter Developer & Programmer", 
            "skills": skills[:8] or ["Flutter","Dart","Python","C++"],
            "projects": projects[:5] or ["Portfolio site"],
            "fetched_at": int(time.time())
        }
        CACHE_LAST_FETCH = PORTFOLIO_DATA["fetched_at"]
    except Exception:
        if not PORTFOLIO_DATA:
            PORTFOLIO_DATA = {
                "name": "Mohamed Aarif A",
                "role": "Flutter Developer & Programmer",
                "skills": ["Flutter","Dart","Python","C++"],
                "projects": ["Portfolio site"],
                "fetched_at": int(time.time())
            }
            CACHE_LAST_FETCH = PORTFOLIO_DATA["fetched_at"]

async def ensure_cache():
    if time.time() - CACHE_LAST_FETCH > CACHE_TTL_SECS or not PORTFOLIO_DATA:
        await fetch_and_cache_portfolio()

def get_cache_key(message: str, mode: str) -> str:
    return hashlib.md5(f"{message.lower().strip()}:{mode}".encode()).hexdigest()

def get_cached_response(cache_key: str) -> str:
    if cache_key in response_cache:
        cached_time, response = response_cache[cache_key]
        if time.time() - cached_time < RESPONSE_CACHE_TTL:
            return response
        del response_cache[cache_key]
    return None

def cache_response(cache_key: str, response: str):
    response_cache[cache_key] = (time.time(), response)
    if len(response_cache) > 200:
        oldest = min(response_cache.keys(), key=lambda k: response_cache[k][0])
        del response_cache[oldest]

def get_relevant_context(message: str, portfolio_data: dict) -> str:
    msg_lower = message.lower()
    context_parts = [f"Name: {portfolio_data['name']}", f"Role: {portfolio_data['role']}"]
    
    if any(skill.lower() in msg_lower for skill in portfolio_data['skills']):
        relevant_skills = [s for s in portfolio_data['skills'] if s.lower() in msg_lower][:3]
        if relevant_skills:
            context_parts.append(f"Skills: {', '.join(relevant_skills)}")
    
    if any(word in msg_lower for word in ["project", "work", "built", "created"]):
        context_parts.append(f"Projects: {', '.join(portfolio_data['projects'][:3])}")
        
    return "\n".join(context_parts)

def summarize_old_messages(history: list) -> str:
    if len(history) <= 4:
        return ""
    old_msgs = history[:-4]
    topics = set()
    for msg in old_msgs:
        if any(word in msg['user'].lower() for word in ["skill", "project", "experience"]):
            topics.add("discussed skills/projects")
        if any(word in msg['user'].lower() for word in ["contact", "hire", "work"]):
            topics.add("discussed contact/hiring")
    return f"Earlier: {', '.join(topics)}" if topics else ""

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    stream: bool = False
    mode: str = "portfolio"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        cache_key = get_cache_key(request.message, request.mode)
        cached = get_cached_response(cache_key)
        if cached:
            if request.stream:
                async def cached_stream():
                    for char in cached:
                        yield f"data: {json.dumps({'token': char})}\n\n"
                        await asyncio.sleep(0.01)
                    yield f"data: {json.dumps({'done': True})}\n\n"
                return StreamingResponse(cached_stream(), media_type="text/plain")
            return {"reply": cached}
        
        await ensure_cache()
        
        if request.session_id not in user_sessions:
            user_sessions[request.session_id] = {"history": []}
        session = user_sessions[request.session_id]
        
        if request.mode == "portfolio":
            context = get_relevant_context(request.message, PORTFOLIO_DATA)
            system_msg = f"You are Mohamed Aarif A's portfolio assistant. Answer about him using:\n{context}\n\nBe concise and helpful."
        else:
            system_msg = "You are a helpful AI assistant. Answer any question clearly and concisely."
        
        summary = summarize_old_messages(session["history"])
        recent_context = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in session["history"][-4:]])
        
        full_prompt = f"{system_msg}\n\n{summary}\n{recent_context}\n\nUser: {request.message}\nAI:"
        
        if request.stream:
            async def generate():
                full_response = ""
                async for chunk in llm.astream(full_prompt):
                    if hasattr(chunk, 'content') and chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'token': chunk.content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                
                cache_response(cache_key, full_response)
                session["history"].append({"user": request.message, "ai": full_response})
                if len(session["history"]) > 20:
                    session["history"] = session["history"][-10:]
                    
            return StreamingResponse(generate(), media_type="text/plain")
        else:
            response = await llm.ainvoke(full_prompt)
            reply = response.content
            
            cache_response(cache_key, reply)
            session["history"].append({"user": request.message, "ai": reply})
            if len(session["history"]) > 20:
                session["history"] = session["history"][-10:]
                
            return {"reply": reply}
            
    except Exception as e:
        return {"reply": "I'm having trouble right now. Please try again."}

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Aarif Portfolio Chatbot API is running", "version": "2.0.0"}