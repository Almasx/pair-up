import psycopg2
import psycopg2.extras
from flask import g, current_app


def get_db():
    if "db" not in g:
        url = (current_app.config.get("DATABASE_URL") or "").strip()
        if not url:
            raise RuntimeError(
                "DATABASE_URL is not set. Add it to server/.env (see .env.example)."
            )
        g.db = psycopg2.connect(
            url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    app.teardown_appcontext(close_db)
