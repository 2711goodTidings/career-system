from sqlalchemy import create_engine

USERNAME = "root"
PASSWORD = "123456Aa!"
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "career_planner"

DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_engine(DATABASE_URL)

def test_connection():
    try:
        with engine.connect() as conn:
            print("MySQL connected successfully!")
    except Exception as e:
        print("MySQL connection failed:", e)