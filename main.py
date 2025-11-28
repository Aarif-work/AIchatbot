from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

def fetch_portfolio_data():
    try:
        response = requests.get('https://aarif-work.github.io/html/index.html', timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            'name': 'Mohamed Aarif A',
            'role': 'Flutter Developer & Programmer',
            'skills': [],
            'projects': [],
            'achievements': []
        }
        
        # Extract skills
        tech_spans = soup.find_all('span')
        skills = set()
        for span in tech_spans:
            text = span.get_text().strip()
            if text and len(text) < 20 and any(tech in text.lower() for tech in ['flutter', 'python', 'dart', 'c++', 'javascript', 'mysql', 'iot', 'firebase']):
                skills.add(text)
        data['skills'] = list(skills)[:6]
        
        # Extract projects
        project_cards = soup.find_all('div', class_='portfolio-card')
        for card in project_cards[:3]:
            title_elem = card.find('h3')
            if title_elem:
                data['projects'].append(title_elem.get_text().strip())
        
        return data
    except:
        return {
            'name': 'Mohamed Aarif A',
            'role': 'Flutter Developer & Programmer',
            'skills': ['Flutter', 'Dart', 'Python', 'C++', 'IoT'],
            'projects': ['Nadi Bio Band', 'Flutter Development', 'Algorithmic Solutions'],
            'achievements': ['IIT Madras Data Science Program', 'Grade A in Computational Thinking']
        }

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        portfolio_data = fetch_portfolio_data()
        
        system_prompt = f"""You are an AI assistant answering questions about Mohamed Aarif A.
        
INFO: {portfolio_data['name']}, {portfolio_data['role']}
SKILLS: {', '.join(portfolio_data['skills'])}
PROJECTS: {', '.join(portfolio_data['projects'])}
        
Answer in a friendly, positive tone about Aarif's expertise."""
        
        full_prompt = f"{system_prompt}\n\nUser: {request.message}\nResponse:"
        response = llm.invoke(full_prompt)
        return {"reply": response.content}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

@app.get("/")
def root():
    return {"message": "Chatbot is running"}