from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.llm.llm_service import LLMService

router = APIRouter(tags=['LLM'])


@router.post('/generate')
async def generate():
    try:

        async def generate():
            for text_chunk in LLMService().execute(
                'Qual é o seu nome? Me descreva sua origem.'
            ):
                yield text_chunk
            yield '\n'

        return StreamingResponse(
            generate(),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Content-Type': 'text/event-stream',
                'Connection': 'keep-alive',
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'An error occurred while generating text: {str(e)}',
        )
