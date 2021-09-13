from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options=dict(autoflush=False))