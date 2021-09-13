from common.models.User import User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func, TypeDecorator, Text


db = SQLAlchemy(session_options=dict(autoflush=False))

class UserDao():
    @staticmethod
    def select_user_by_id(id):
        return User.query.filter(User.uid == id).first()



