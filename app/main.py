from fastapi import FastAPI
from api import routes_sessions, routes_chat, routes_debug, routes_feed, routes_groq
import uvicorn
app = FastAPI()

app.include_router(routes_sessions.router)
app.include_router(routes_chat.router)
app.include_router(routes_debug.router)
app.include_router(routes_feed.router)
app.include_router(routes_groq.groq_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)