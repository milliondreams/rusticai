import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, Optional


class MemberType(str, Enum):
    """Enum representing the type of an ensemble member."""

    BOT = "bot"
    HUMAN = "human"


class MemberCommsType(str, Enum):
    """Enum representing the communication type used by an ensemble member."""

    HTTP = "http"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"


@dataclass
class EnsembleMember:
    """
    Represents a member in a conversational ensemble.

    Attributes:
        id: Unique ID of the member
        name: Display name of the member
        ensemble_id: ID of the ensemble this member belongs to
        member_type: Type of the member (bot or human)
        comms_type: Communication type used by this member
        endpoint: Endpoint URL if applicable
        is_active: Flag indicating if member is active
    """

    id: str
    name: str
    member_type: MemberType
    comms_type: MemberCommsType
    endpoint: Optional[str] = None
    is_active: bool = True

    def __post_init__(self):
        if not self.id:
            raise ValueError("Ensemble member ID cannot be empty")
        if not self.name:
            raise ValueError("Ensemble member name cannot be empty")
        if not self.member_type:
            raise ValueError("Ensemble member type cannot be empty")
        if not self.comms_type:
            raise ValueError("Ensemble member communication type cannot be empty")

        if not isinstance(self.member_type, MemberType):
            try:
                self.member_type = MemberType(self.member_type)
            except ValueError:
                raise ValueError("Ensemble member type must be a MemberType")

        if not isinstance(self.comms_type, MemberCommsType):
            try:
                self.comms_type = MemberCommsType(self.comms_type)
            except ValueError:
                raise ValueError("Ensemble member communication type must be a MemberCommsType")

        if (self.comms_type == MemberCommsType.WEBHOOK) and (
            not self.endpoint or not self.endpoint.startswith("https://")
        ):
            raise ValueError("Ensemble member endpoint must start with http for HTTP Communication type")

    def activate(self):
        """Activate the member."""
        self.is_active = True

    def deactivate(self):
        """Deactivate the member."""
        self.is_active = False

    def serialize(self) -> str:
        """Serialize the member to JSON."""
        return json.dumps(self, cls=EnsembleMemberEncoder)

    @staticmethod
    def deserialize(serialized_member: str) -> "EnsembleMember":
        """Deserialize a member from JSON."""
        return json.loads(serialized_member, cls=EnsembleMemberDecoder)


@dataclass
class Ensemble:
    """
    Represents a conversational ensemble.

    Attributes:
        id: Unique ID of the ensemble
        name: Name of the ensemble
        members: Dictionary of EnsembleMember objects belonging to this ensemble
    """

    id: str  # Short UUID
    name: str  # Ensemble name
    members: Dict[str, EnsembleMember] = field(default_factory=dict)  # Ensemble members

    def __post_init__(self):
        if not self.id:
            raise ValueError("Ensemble ID cannot be empty")
        if not self.name:
            raise ValueError("Ensemble name cannot be empty")
        if not self.members or self.members is None:
            self.members = {}

    def add_member(self, member: EnsembleMember):
        """Add a member to the ensemble."""
        self.members[member.id] = member

    def remove_member(self, member_id: str):
        """Remove a member from the ensemble."""
        del self.members[member_id]

    def get_member(self, member_id: str) -> EnsembleMember:
        """Get a member from the ensemble."""
        return self.members[member_id]

    def activate_member(self, member_id: str):
        """Activate a member in the ensemble."""
        self.members[member_id].activate()

    def deactivate_member(self, member_id: str):
        """Deactivate a member in the ensemble."""
        self.members[member_id].deactivate()

    def serialize(self):
        """Serialize the ensemble to a JSON string."""
        return json.dumps(self, cls=EnsembleEncoder)

    @staticmethod
    def deserialize(json_str: str):
        """Deserialize a JSON string to an Ensemble object."""
        return json.loads(json_str, cls=EnsembleDecoder)


class EnsembleEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Ensemble):
            return {"id": o.id, "name": o.name, "members": {m_id: asdict(m) for m_id, m in o.members.items()}}
        return super().default(o)  # pragma: no cover


class EnsembleDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'id' in obj and 'name' in obj and 'members' in obj:
            return Ensemble(
                id=obj['id'],
                name=obj['name'],
                members={m_id: EnsembleMember(**m_data) for m_id, m_data in obj['members'].items()},
            )
        return obj


class EnsembleMemberEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, EnsembleMember):
            return asdict(o)
        return super().default(o)  # pragma: no cover


class EnsembleMemberDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'id' in obj and 'name' in obj and 'member_type' in obj and 'comms_type' in obj:
            return EnsembleMember(**obj)
        return obj  # pragma: no cover
