from fastapi import FastAPI

from rustic_ai import __version__

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    """Health endpoint for the API."""
    return {"message": "OK"}


@app.get("/version")
async def version():
    """Version endpoint for the API."""
    # Get version of the current package
    version = __version__
    return {"version": version}
