from flask import Flask, request, jsonify, abort, render_template
from flask_cors import CORS
from models import People, db
import requests
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

CORS(app)


TELEGRAM_BOT_TOKEN = '7887937612:AAHszVV-UqqWEgITxDhJItGcYXo_nocljP4'
CHAT_ID = '1529447580'

#TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
#CHAT_ID = os.getenv('ALLOWED_CHAT_IDS').split(',')


# Отоброжение главной страницы
@app.route('/')
def index():
    return render_template('index.html')


# Отображение xml файла
@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')


# Функция отправки заявки в тг канал
def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=data)
    return response.status_code == 200


# Получение данных из БД
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([i.to_dict() for i in people])


# Добавление человека и его данных в БД
@app.route('/people', methods=['POST'])
def post_people():
    data = request.get_json()

    if 'phone' not in data or 'name' not in data or 'answer' not in data:
        abort(400, description="Необходимо указать все поля!")

    person = People(phone=data['phone'], name=data['name'], answer=data['answer'])
    db.session.add(person)
    db.session.commit()

    message = f"Добавлен новый человек:\nИмя: {person.name}\nТелефон: {person.phone}\nВопрос: {person.answer}"
    if send_to_telegram(message):
        return jsonify(person.to_dict()), 201
    else:
        return jsonify({"error": "Не удалось отправить сообщение в Telegram"}), 500


# Создание БД и запуск сервера
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)

