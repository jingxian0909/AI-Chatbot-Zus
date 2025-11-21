from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from products import router as products_router
from outlets import router as outlets_router
from chat import router as chat_router

app = FastAPI(title="Mindhive Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix="/api")
app.include_router(outlets_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "FastAPI backend running!"}