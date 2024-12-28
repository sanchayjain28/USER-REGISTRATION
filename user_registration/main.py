from fastapi import FastAPI
import uvicorn
from api import router
from settings import settings

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings['PORT']), reload=True)
