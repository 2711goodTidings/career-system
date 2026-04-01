from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.get("/test")
def test():
    return {
        "code": 200,
        "message": "Backend test success",
        "data": {
            "project": "career-system"
        }
    }

from database import engine

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            return {"message": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}