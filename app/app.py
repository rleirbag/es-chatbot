from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.config.database import SessionLocal
from app.routers.auth.router import router as auth_router
from app.routers.chat_history import router as chat_history_router
from app.routers.document.router import router as document_router
from app.routers.llm.router import router as llm_router
from app.routers.chat_router import router as chat_router
from app.routers.user.router import router as user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()

    try:
        response = await call_next(request)
    except:
        request.state.db.rollback()
        raise
    finally:
        request.state.db.close()

    return response


app.include_router(auth_router, prefix='/auth')
app.include_router(document_router, prefix='/document')
app.include_router(llm_router, prefix='/llm')
app.include_router(chat_history_router)
app.include_router(chat_router)
app.include_router(user_router)


@app.get('/')
def read_root():
    return {'message': 'Hello World!'}
