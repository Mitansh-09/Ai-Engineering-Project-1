from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "alive"}

@app.get("/ping")
def ping():
    return {"message": "pong"}