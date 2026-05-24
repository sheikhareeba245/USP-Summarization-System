from flask import Flask
from config import Config
from extensions import db
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

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
    
    # Blueprint register karo
    from routes.auth import auth
    app.register_blueprint(auth)
    
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
    app.run(debug=True)