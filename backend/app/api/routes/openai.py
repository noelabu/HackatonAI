from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from decouple import config

router = APIRouter()

async def stream_api(prompt):
    client = OpenAI(
        api_key=config('OPENAI_API_KEY')
    )

    messages = [{"role": "user", "content": prompt}]

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
        else:
            break

@router.get(
    "/stream",
    status_code=201
)
async def test_api_stream(prompt:str):
    return StreamingResponse(stream_api(prompt))