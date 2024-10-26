from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import People, Base, engine, get_db
import requests
import os

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
Base.metadata.create_all(bind=engine)


TELEGRAM_BOT_TOKEN = '7887937612:AAHszVV-UqqWEgITxDhJItGcYXo_nocljP4'
CHAT_ID = '1529447580'

#TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
#CHAT_ID = os.getenv('ALLOWED_CHAT_IDS').split(',')


class PersonCreate(BaseModel):
    phone: str
    name: str
    answer: str


class PersonResponse(PersonCreate):
    id: int

    class Config:
        from_attributes = True


def send_to_telegram(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_ID:
        response = requests.post(url, json={"chat_id": chat_id, "text": message})
        if not response.ok:
            return False
    return True


# Получение данных из БД
@app.get("/people", response_model=List[PersonResponse])
def get_people(db: Session = Depends(get_db)):
    people = db.query(People).all()
    return people


# Добавление человека и его данных в БД
@app.post("/people", response_model=PersonResponse)
def post_people(person: PersonCreate, db: Session = Depends(get_db)):
    new_person = People(phone=person.phone, name=person.name, answer=person.answer)
    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    message = f"Добавлен новый человек:\nИмя: {new_person.name}\nТелефон: {new_person.phone}\nВопрос: {new_person.answer}"
    if send_to_telegram(message):
        return new_person
    else:
        raise HTTPException(status_code=500, detail="Не удалось отправить сообщение в Telegram")
