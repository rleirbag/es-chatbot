from fastapi import APIRouter, HTTPException, Security
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm.llm_service import LLMService
from app.utils.security import get_current_user

router = APIRouter(tags=['LLM'])


class Prompt(BaseModel):
    message: str


@router.post('/generate')
async def generate(
    prompt: Prompt,
    user_info: dict = Security(get_current_user),
):
    try:

        async def generate():
            for text_chunk in LLMService().execute(prompt.message):
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
