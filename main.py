
#qrSOwi5X8zvwpiPJd
from fastapi import FastAPI, Request
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import openai
import certifi
from pymongo import MongoClient
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS za React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Promeni na domen u produkciji
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# OpenAI klijent
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
# MongoDB konekcija
mongodb_uri = os.getenv("MONGODB_URI")

#client = MongoClient(os.getenv("MONGODB_URI"))
client = MongoClient(mongodb_uri, tlsCAFile = certifi.where())

db = client.get_database("chatbot")
messages_collection = db.messages

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Message, request: Request):
    # Simuliran odgovor bota (ovde možeš dodati OpenAI, RAG, NLP itd.)
    
    #Dohvatanje IP adrese
    client_ip = request.headers.get('x-forwarded-for', request.client.host)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=
            [
                {
                    "role": "system",
                    "content": "Ti si AI asistent koji odgovara na pitanja o Nemanji Pešiću. On je softverski inženjer, voli veštačku inteligenciju, i radio je na raznim projektima koristeći C#, .NET i FastAPI. Odgovaraj ljubazno i precizno."
                    "Nemanja je rodjen 19.08.1993. godine u Nisu u Srbiji. Osnovna skola - Cele kula,Srednja skola - gimnazija Bora Stankovic Nis. Fakultet - Elektronski fakultet Nis na smeru Upravljanje sistemima 09.2012 - 09-2021."
                    "Prosek mu je 8.1. Najbolje su mu isli programerski predmeti kao sto je Algoritmi i programiranje. Bio je na razmeni studenata u Paderbornu u Nemackoj od 09.2014-09/2015."
                    "Pokusaj da odgovori imaju jednu do dve recenice ako je moguce."
                },
                {
                    "role": "user",
                    "content":msg.message
                }
            ]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Greška u komunikaciji sa AI modelom: {str(e)}"
    # Loguj poruku u bazu kao jedan dokument
    messages_collection.insert_one({
        "ip": client_ip,
        "timestamp": datetime.utcnow(),
        "user_message": msg.message,
        "bot_reply": reply
    })
    
    messages_collection.insert_one({"bot": reply})
    
    
    return {"reply": reply}


# frontend pogadja endpoint post metodom na http://127.0.0.1:8000/chat i u telu {message: "neko pitanje"}
# tu gde je pogodjen endpoint treba postaviti logiku da model obradjuje to pitanje i vraca odgovor