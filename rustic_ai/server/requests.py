from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rustic_ai.ensemble.ensemble import MemberType
from rustic_ai.messagebus.utils import Priority


class CreateEnsembleRequest(BaseModel):
    """Request body for creating an ensemble."""

    name: str


class EnsembleResponse(BaseModel):
    """Response body for an ensemble."""

    id: str
    name: str
    members: dict


class CreateEnsembleMemberRequest(BaseModel):
    """Request body for creating an ensemble member."""

    name: str
    member_type: MemberType
    callback_url: str

    def __post_init__(self):
        """Post init validation."""
        if not isinstance(self.member_type, MemberType):  # pragma: no cover
            try:
                self.member_type = MemberType(self.member_type)
            except ValueError:
                raise ValueError("Ensemble member type must be a MemberType")


class EnsembleMemberResponse(BaseModel):
    """Request body for adding a member to an ensemble."""

    id: str
    ensemble_id: str
    name: str
    member_type: MemberType
    callback_url: Optional[str]


class MessageRequests(BaseModel):
    """Request body for sending a message."""

    sender: str
    content: Dict[Any, Any]
    recipients: Optional[List[str]] = None
    priority: Priority = Priority.NORMAL
    thread_id: Optional[int] = None
    in_reply_to: Optional[int] = None
    topic: Optional[str] = None

    def __post_init__(self):
        """Post init validation."""
        if not isinstance(self.priority, Priority):  # pragma: no cover
            try:
                self.priority = Priority(self.priority)
            except ValueError:
                raise ValueError("Priority must be a Priority")
