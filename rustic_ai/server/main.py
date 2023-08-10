import os

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from rustic_ai import __version__
from rustic_ai.ensemble.ensemble import MemberCommsType, MemberType
from rustic_ai.ensemble.ensemble_manager import EnsembleManager
from rustic_ai.ensemble.storage.exceptions import EnsembleNotFoundError
from rustic_ai.server.requests import (
    CreateEnsembleMemberRequest,
    CreateEnsembleRequest,
    EnsembleMemberResponse,
    EnsembleResponse,
    MessageRequests,
)

from .handlers import build_url_callback_method

app = FastAPI()

# Get the config location from commandline arguments
# If no config location is provided, check the enviroment variable
# If no enviroment variable is provided, use the default config location
config_location = os.environ.get("CONFIG_LOCATION", "config/config.yaml")

# Create a EnsembleManager object
ensemble_manager: EnsembleManager = EnsembleManager(config_location)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint for the API."""
    return """
    <html>
        <head>
            <title>Rustic AI</title>
        </head>
        <body>
            <h1>Rustic AI</h1>
            <p>API for Rustic AI</p>
            <p>Go to <a href="/docs">/docs</a> for OpenAPI UI</p>
        </body>
    </html>"""


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


@app.get("/config")
async def config():
    """Config endpoint for the API."""
    # Get config of the current package
    with open(config_location, "r") as f:
        config = yaml.safe_load(f)

    return {"path": config_location, "config": config}


@app.post("/app/ensembles")
async def create_ensemble(ensemble_request: CreateEnsembleRequest):
    """Create an ensemble."""

    # Create an ensemble
    ensemble_map = ensemble_manager.create_ensemble(ensemble_request.name)
    ensemble = ensemble_map.ensemble

    return EnsembleResponse(id=ensemble.id, name=ensemble.name, members=ensemble.members)


@app.get("/app/ensembles")
async def get_ensembles():
    """Get all ensembles."""

    # Get all ensembles
    ensembles = ensemble_manager.get_ensembles()

    return [EnsembleResponse(id=e.id, name=e.name, members=e.members) for e in ensembles]


@app.get("/app/ensembles/{ensemble_id}")
async def get_ensemble(ensemble_id: str):
    """Get an ensemble."""

    # Get an ensemble
    ensemble_map = ensemble_manager.get_ensemble(ensemble_id)
    ensemble = ensemble_map.ensemble

    return EnsembleResponse(id=ensemble.id, name=ensemble.name, members=ensemble.members)


@app.post("/app/ensembles/{ensemble_id}/members")
async def add_member(ensemble_id: str, member_request: CreateEnsembleMemberRequest):
    """Add a member to an ensemble."""

    # Get an ensemble
    try:
        ensemble_manager.load_ensemble(ensemble_id)
    except EnsembleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ensemble '{ensemble_id}'  not found")

    # Add a member to an ensemble
    callback_handler = build_url_callback_method(member_request.callback_url)
    ensemble_member_map = ensemble_manager.create_ensemble_member(
        ensemble_id,
        member_request.name,
        MemberType(member_request.member_type),
        MemberCommsType.HTTP,
        callback_handler,
        member_request.callback_url,
    )

    return EnsembleMemberResponse(
        id=ensemble_member_map.member.id,
        ensemble_id=ensemble_id,
        name=ensemble_member_map.member.name,
        member_type=ensemble_member_map.member.member_type,
        callback_url=ensemble_member_map.member.endpoint,
    )


@app.post("/app/ensembles/{ensemble_id}/messages")
async def send_message(ensemble_id: str, message: MessageRequests):
    """Send a message to an ensemble."""

    # Send a message to an ensemble
    return ensemble_manager.send_message(
        ensemble_id,
        message.sender,
        message.content,
        message.recipients,
        message.priority,
        message.thread_id,
        message.in_reply_to,
        message.topic,
    )
