import socket
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

import shortuuid
import yaml

from rustic_ai.ensemble.storage.exceptions import EnsembleMemberNotFoundError, EnsembleNotFoundError
from rustic_ai.messagebus import Client

from ..messagebus import Message
from ..messagebus.client.callback_client import CallbackClient
from ..messagebus.message_bus import MessageBus
from ..messagebus.storage.backend_factory import StorageBackendFactory
from .ensemble import Ensemble, EnsembleMember, MemberCommsType, MemberType
from .storage.ensemble_factory import EnsembleStorageFactory


@dataclass
class EnsembleMemberMap:
    """
    Represents an ensemble member and its associated message bus client.
    """

    member: EnsembleMember
    client: Client


@dataclass
class EnsembleMap:
    """
    Represents an ensemble and its associated message bus.
    """

    ensemble: Ensemble
    message_bus: MessageBus
    clients: Dict[str, Client] = field(default_factory=dict)

    def __post_init__(self):
        self.clients = {}


class EnsembleManager:
    """
    Manages ensembles and their members.
    """

    def __init__(self, config_yaml: str):
        """
        Initializes the ensemble manager.

        Args:
            config_yaml (str): The path to the YAML configuration file.
        """
        self.config_yaml = config_yaml

        # Load the configuration file
        with open(self.config_yaml) as f:
            self.config = yaml.safe_load(f)

        # Initialize the ensemble storage and message bus backend
        self.ensemble_storage = EnsembleStorageFactory.from_config(self.config)
        self.message_bus_backend = StorageBackendFactory.from_config(self.config)

        # Initialize the ensembles and ensemble members dictionaries
        self.ensembles: Dict[str, EnsembleMap] = {}

    def _get_machine_id(self) -> int:
        """
        Get the machine ID for this machine.

        Returns:
            int: The machine ID.
        """
        machine_id = 1
        try:
            # Get the IP address of the current machine
            ip_address = socket.gethostbyname(socket.gethostname())
            ip_parts = ip_address.split('.')
            # Get the last part as the machine ID
            machine_id = int(ip_parts[-1])
        finally:
            return machine_id

    def _create_message_bus(self, ensemble_id: str) -> MessageBus:
        """
        Creates a new message bus for the given ensemble ID.

        Args:
            ensemble_id (str): The ID of the ensemble.

        Returns:
            MessageBus: The new message bus.
        """
        return MessageBus(
            id=ensemble_id,
            machine_id=self._get_machine_id(),
            storage_backend=self.message_bus_backend,
        )

    def _add_to_ensembles(self, ensemble: Ensemble, message_bus: MessageBus) -> EnsembleMap:
        """
        Adds an ensemble and its associated message bus to the ensembles dictionary.

        Args:
            ensemble (Ensemble): The ensemble to add.
            message_bus (MessageBus): The message bus associated with the ensemble.
        """
        emap = EnsembleMap(ensemble=ensemble, message_bus=message_bus, clients={})
        self.ensembles[ensemble.id] = emap
        return emap

    def create_ensemble(self, ensemble_name: str) -> EnsembleMap:
        """
        Creates a new ensemble with the given name.

        Args:
            ensemble_name (str): The name of the ensemble.

        Returns:
            EnsembleMap: The new ensemble and its associated message bus.
        """
        # Create and store the ensemble
        ensemble = Ensemble(id=shortuuid.uuid(), name=ensemble_name, members={})
        self.ensemble_storage.create_ensemble(ensemble)

        # Create the message bus
        message_bus = self._create_message_bus(ensemble.id)
        return self._add_to_ensembles(ensemble, message_bus)

    def load_ensemble(self, ensemble_id: str) -> EnsembleMap:
        """
        Loads an ensemble from storage.

        Args:
            ensemble_id (str): The ID of the ensemble to load.

        Returns:
            EnsembleMap: The loaded ensemble and its associated message bus.
        """
        if ensemble_id in self.ensembles:
            return self.ensembles[ensemble_id]
        else:
            ensemble = self.ensemble_storage.get_ensemble(ensemble_id)
            message_bus = self._create_message_bus(ensemble_id)
            return self._add_to_ensembles(ensemble, message_bus)

    def get_ensemble(self, ensemble_id: str) -> EnsembleMap:
        """
        Gets an ensemble by ID.

        Args:
            ensemble_id (str): The ID of the ensemble to get.

        Returns:
            EnsembleMap: The ensemble and its associated message bus.
        """
        if ensemble_id in self.ensembles:
            return self.ensembles[ensemble_id]
        else:
            raise EnsembleNotFoundError

    def create_ensemble_member(
        self,
        ensemble_id: str,
        member_name: str,
        member_type: MemberType,
        member_comms: MemberCommsType,
        callback: Callable[[Message], None],
        endpoint: Optional[str] = None,
    ) -> EnsembleMemberMap:
        """
        Creates a new ensemble member and registers it with the message bus.

        Args:
            ensemble_id (str): The ID of the ensemble to add the member to.
            member_name (str): The name of the member.
            member_type (MemberType): The type of the member.
            member_comms (MemberCommsType): The communication type of the member.
            callback (Callable[[Message], None]): The callback function to handle incoming messages.
            endpoint (Optional[str], optional): The endpoint for the member. Defaults to None.

        Returns:
            EnsembleMemberMap: The new ensemble member and its associated message bus client.
        """
        ensemble_map = self.get_ensemble(ensemble_id)
        ensemble = ensemble_map.ensemble
        message_bus = ensemble_map.message_bus

        # Create the ensemble member
        ensemble_member = EnsembleMember(
            id=shortuuid.uuid(),
            name=member_name,
            member_type=member_type,
            comms_type=member_comms,
            endpoint=endpoint,
            is_active=True,
        )

        # Add the member to the ensemble
        ensemble.add_member(ensemble_member)

        # Create an message bus CallbackClient for the member and register it with the message bus
        client = CallbackClient(
            client_id=ensemble_member.id,
            message_bus=message_bus,
            message_callback=callback,
        )

        # Add the client to the message bus
        message_bus.register_client(client)

        ensemble_map.clients[ensemble_member.id] = client

        return EnsembleMemberMap(member=ensemble_member, client=client)

    def get_ensemble_member(self, ensemble_id: str, member_id: str) -> EnsembleMemberMap:
        """
        Gets an ensemble member by ID.

        Args:
            ensemble_id (str): The ID of the ensemble the member belongs to.
            member_id (str): The ID of the member to get.

        Returns:
            EnsembleMemberMap: The ensemble member and its associated message bus client.
        """
        ensemble_map = self.get_ensemble(ensemble_id)
        ensemble = ensemble_map.ensemble

        if member_id in ensemble.members:
            return EnsembleMemberMap(member=ensemble.members[member_id], client=ensemble_map.clients[member_id])
        else:
            raise EnsembleMemberNotFoundError

    def deactivate_ensemble_member(self, ensemble_id: str, member_id: str) -> None:
        """
        Deactivates an ensemble member and unregisters its message bus client.

        Args:
            ensemble_id (str): The ID of the ensemble the member belongs to.
            member_id (str): The ID of the member to deactivate.
        """
        ensemble_map = self.get_ensemble(ensemble_id)
        ensemble = ensemble_map.ensemble
        message_bus = ensemble_map.message_bus

        if member_id in ensemble.members:
            member = ensemble.members[member_id]
            if member.is_active:
                if member_id in ensemble_map.clients:
                    client = ensemble_map.clients[member_id]
                    message_bus.unregister_client(client)
                    del ensemble_map.clients[member_id]
                ensemble.deactivate_member(member_id)
                self.ensemble_storage.update_ensemble(ensemble)
        else:
            raise EnsembleMemberNotFoundError
