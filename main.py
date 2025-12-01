from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import asyncio, time
from typing import Dict
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
    temperature=0.3,
    max_tokens=150
)

# Static portfolio data
PORTFOLIO_DATA = {
    "name": "Mohamed Aarif A (Aarif)",
    "role": (
        "Full-stack Flutter Developer, IoT Innovator, and Problem-Solving Programmer who builds "
        "polished, high-performance mobile applications and sensor-driven systems using modern, "
        "scalable engineering practices."
    ),
    "tagline": (
        "Crafting refined cross-platform mobile experiences, intelligent IoT solutions, "
        "and computationally efficient systems."
    ),

    "location": "Karaikudi, Tamil Nadu 630001, India",
    "email": "mohamedaarif1811@gmail.com",

    "domains": (
        "• **Mobile Development:** Flutter, Dart, Firebase, cross-platform UI/UX engineering.\n"
        "• **IoT Engineering:** ESP32, real-time sensor acquisition, pulse analysis, Bluetooth communication, edge computing.\n"
        "• **Data & Algorithms:** Computational efficiency, optimization, scalable data architecture, error-resilient processing.\n"
        "• **Systems Thinking:** Combining mobile + hardware + backend to build fully integrated digital ecosystems."
    ),

    "education": (
        "• Student of the **IIT Madras BS in Data Science & Programming** program (old batch), "
        "with exposure to computational foundations, mathematical reasoning, data-driven systems, "
        "and real-world programming practices.\n"
        "• Developed strong fundamentals in algorithms, data structures, data handling, "
        "problem solving, and structured system design."
    ),

    "achievements": (
        "• Awarded **Grade A** in the *Computational Thinking* course at IIT Madras.\n"
        "• Received **personal recognition from Prof. V. Kamakoti**, Director of IIT Madras, "
        "known for his contributions to Computer Architecture, VLSI, and Cybersecurity.\n"
        "• Built multiple showcased projects in IoT, Flutter, and algorithms that demonstrate "
        "end-to-end design, engineering rigor, and problem-solving depth."
    ),

    "personal_strengths": (
        "• Strong UI/UX intuition — builds clean, modern, user-first interfaces.\n"
        "• Excellent debugging and analytical skills.\n"
        "• Passion for learning new technologies quickly.\n"
        "• Ability to bridge hardware + software — rare combination.\n"
        "• Loves improving performance, reducing complexity, and writing efficient code."
    ),

    "tech_stack": {
        "mobile": "Flutter, Dart, Firebase, Local Storage, Provider/Bloc, REST APIs, Responsive UI/UX",
        "iot": "ESP32, C/C++, Optical Pulse Sensors, Bluetooth LE, Serial Communication, Embedded Programming",
        "backend": "Python, Node.js Basics, Flask/FastAPI (learning), MySQL, Firebase Realtime/Firestore",
        "general": "Git/GitHub, Debugging Tools, VS Code, Circuit Design, Prototyping",
    },

    "projects": {
        "flutter_development": {
            "summary": (
                "Designs and develops elegant, high-performance mobile applications with clean structure, "
                "animation-rich UI, and seamless cross-platform behaviour using Flutter and Dart."
            ),
            "details": (
                "• Firebase integration (Auth, Firestore, Realtime DB, Storage)\n"
                "• Responsive layouts for Android/iOS\n"
                "• Smooth state management (Provider/Bloc)\n"
                "• Modern app patterns: MVVM, clean architecture\n"
                "• Focus on accessibility, UX clarity, and minimalistic design"
            )
        },

        "nadi_bio_band": {
            "summary": (
                "A flagship IoT wearable project designed to capture and analyze wrist-pulse patterns in real time "
                "using optical sensors and an ESP32 microcontroller."
            ),
            "details": (
                "• Integrated **optical pulse sensors** to acquire heartbeat/pulse waveform\n"
                "• **ESP32 firmware** built for accurate sampling and noise-filtered readings\n"
                "• Real-time data transmission to mobile via **Bluetooth LE**\n"
                "• Displays analytics, pulse behavior, and insights on-screen\n"
                "• Designed for **educational, wellness, and research** applications\n"
                "• Represents Aarif's passion for merging hardware with intuitive software"
            )
        },

        "algorithmic_solutions": {
            "summary": (
                "A collection of algorithm-focused projects emphasizing computational efficiency, "
                "fast execution, and structured logic-building."
            ),
            "details": (
                "• Implemented in C/C++, Python, and Rust\n"
                "• Focuses on performance optimization, complexity reduction, and clean problem-solving patterns\n"
                "• Includes data handling, modular design, efficient storage, and scalable architecture thinking"
            )
        }
    },

    "mentors": {
        "palani_vairavan": (
            "Engineering Leadership @ Amazon | Formerly AWS & Microsoft Azure | "
            "Teacher at Hope3 Varsity"
        ),
        "siva_kumar": "Leader at Hope3 Foundation, Treasty (Education & Innovation Focus)",
        "gokul_kittusamy": "CEO of ELARCHITEK, MIT Background, Hardware & Innovation Mentor",
        "meenakshi_sundaram": "Applied Data Scientist (Semiconductor + Modeling Expertise)",
        "mani_rr": "Senior Software Engineer and Engineering Mentor"
    },

    "contact": {
        "email": "mohamedaarif1811@gmail.com",
        "location": "Karaikudi, Tamil Nadu, India",
        "linkedin": "Available on portfolio website",
        "github": "https://github.com/aarif-work"
    },

    "about_long": (
        "I'm **Mohamed Aarif A**, a developer who blends mobile engineering with IoT innovation. "
        "I specialize in creating seamless, elegant, and high-performance mobile apps in Flutter, "
        "while also building real-time sensor systems such as the Nadi Bio Band using ESP32 and "
        "embedded programming. I love solving complex problems through clean architecture, "
        "mathematical reasoning, and computational efficiency. My education at IIT Madras strengthened "
        "my analytical foundation and deepened my understanding of algorithms, data structures, "
        "and structured thinking. My goal is to build meaningful products that merge design, "
        "technology, and intelligence."
    )
}

user_sessions = {}
response_cache = {}
RESPONSE_CACHE_TTL = 1800

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

def get_portfolio_context() -> str:
    return f"""You are Aarif's Portfolio Concierge, a precise, cordial assistant that answers questions about Mohamed Aarif A based solely on the portfolio's content. Speak in concise, confident sentences with professional warmth.

Identity Snapshot:
Name: {PORTFOLIO_DATA['name']}
Role: {PORTFOLIO_DATA['role']}
Tagline: {PORTFOLIO_DATA['tagline']}
Location: {PORTFOLIO_DATA['location']}
Contact: {PORTFOLIO_DATA['email']}

Domains:
{PORTFOLIO_DATA['domains']}

Education:
{PORTFOLIO_DATA['education']}

Achievements:
{PORTFOLIO_DATA['achievements']}

Personal Strengths:
{PORTFOLIO_DATA['personal_strengths']}

Tech Stack:
- Mobile: {PORTFOLIO_DATA['tech_stack']['mobile']}
- IoT: {PORTFOLIO_DATA['tech_stack']['iot']}
- Backend: {PORTFOLIO_DATA['tech_stack']['backend']}
- General: {PORTFOLIO_DATA['tech_stack']['general']}

Projects:
- Flutter Development: {PORTFOLIO_DATA['projects']['flutter_development']['summary']}
  Details: {PORTFOLIO_DATA['projects']['flutter_development']['details']}

- Nadi Bio Band: {PORTFOLIO_DATA['projects']['nadi_bio_band']['summary']}
  Details: {PORTFOLIO_DATA['projects']['nadi_bio_band']['details']}

- Algorithmic Solutions: {PORTFOLIO_DATA['projects']['algorithmic_solutions']['summary']}
  Details: {PORTFOLIO_DATA['projects']['algorithmic_solutions']['details']}

Mentors:
- Palani Vairavan: {PORTFOLIO_DATA['mentors']['palani_vairavan']}
- Siva Kumar: {PORTFOLIO_DATA['mentors']['siva_kumar']}
- Gokul Kittusamy: {PORTFOLIO_DATA['mentors']['gokul_kittusamy']}
- Meenakshi Sundaram: {PORTFOLIO_DATA['mentors']['meenakshi_sundaram']}
- Mani RR: {PORTFOLIO_DATA['mentors']['mani_rr']}

About:
{PORTFOLIO_DATA['about_long']}

Answering Policy:
- If asked anything outside of the site's content, say: "That isn't on the public portfolio, so I can't confirm."
- Keep responses ≤120 words unless the user asks for more depth
- Always offer the best next step (e.g., "Email Aarif at mohamedaarif1811@gmail.com")
- Prefer concrete details from the site; avoid speculation"""

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
        
        if request.session_id not in user_sessions:
            user_sessions[request.session_id] = {"history": []}
        session = user_sessions[request.session_id]
        
        if request.mode == "portfolio":
            system_msg = get_portfolio_context()
        else:
            system_msg = "You are a helpful AI assistant. Answer any question clearly and concisely."
        
        recent_context = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in session["history"][-2:]])
        
        full_prompt = f"{system_msg}\n\n{recent_context}\n\nUser: {request.message}\nAI:"
        
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