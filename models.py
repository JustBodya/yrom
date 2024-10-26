from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class People(db.Model):
    __tablename__='people'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20))
    name = db.Column(db.String(80))
    answer = db.Column(db.String(200))


    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'answer': self.answer,
        }

