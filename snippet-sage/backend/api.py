from fastapi import FastAPI

app = FastAPI()

@app.get("/api/snippets")
async def list_snippets():
    return [{"id": "1", "title": "test", "code": "print('hello')", "language": "python"}]