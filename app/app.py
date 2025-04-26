from fastapi import FastAPI
from starlette.requests import Request

from app.config.database import SessionLocal
from app.routers.auth.router import router as auth_router
from app.routers.document.router import router as document_router
from app.routers.llm.router import router as llm_router

app = FastAPI()


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


@app.get('/')
def read_root():
    return {'message': 'Hello World!'}
