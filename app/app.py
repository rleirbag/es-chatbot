from fastapi import FastAPI

from app.routers.auth.router import router as auth_router
from app.routers.document.router import router as document_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(document_router, prefix="/document")


@app.get('/')
def read_root():
    return {'message': 'Hello World!'}
