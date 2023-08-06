from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Hello World"}
