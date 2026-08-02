from fastapi import FastAPI

from routes import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "COI Case Study Automation API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}