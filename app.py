from flask import Flask, jsonify
from config import Config
from extensions import db, login_manager
import webbrowser
import threading
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.meal import meal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(meal_bp)

    with app.app_context():
        try:
            db.create_all()
            print(f"[DB] Tables created OK. URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"[DB] CRITICAL: db.create_all() failed: {e}")

    # Diagnostic route — visit /debug-db on the hosted URL to see DB status
    @app.route("/debug-db")
    def debug_db():
        try:
            from sqlalchemy import inspect, text
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            user_count = db.session.execute(
                text("SELECT COUNT(*) FROM user")
            ).scalar() if "user" in tables else "N/A"
            return jsonify({
                "status": "ok",
                "db_uri": app.config["SQLALCHEMY_DATABASE_URI"],
                "tables": tables,
                "user_count": user_count,
            })
        except Exception as e:
            return jsonify({"status": "error", "error": str(e), "type": type(e).__name__}), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Only open browser in the main process, not in Flask's reloader child process
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(debug=True)