from flask import Flask
from config import Config
from extensions import db
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
import os

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    #Preload
    print("Preloading AI models......")
    from utils.keywords import get_kw_model
    get_kw_model()
    print("Models ready!")

    from routes.auth import auth
    app.register_blueprint(auth)

    # 1. Upload Blueprint
    from routes.upload import upload
    app.register_blueprint(upload)
    print("Upload blueprint registered!")

    # 2. Summarize Blueprint
    from routes.summarize import summarize
    app.register_blueprint(summarize)
    print("Summarize blueprint registered!")

    # 3. Library Blueprint
    from routes.library import library
    app.register_blueprint(library)
    print("Library blueprint registered!")

    try:
     from routes.chat import chat_bp
     app.register_blueprint(chat_bp)
     print("Chat blueprint registered!")
    except Exception as e:
     print(f"Chat blueprint ERROR: {e}")

    with app.app_context():
        from models.user import User
        from models.document import Document
        from models.summary import Summary
        from models.chat import Chat
        db.create_all()
        print("Database ready!")

    return app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
