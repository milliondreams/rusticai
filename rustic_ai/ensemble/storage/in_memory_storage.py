from typing import Dict, List

from ..ensemble import Ensemble, EnsembleMember
from .exceptions import EnsembleIdAlreadyExists, EnsembleMemberNotFoundError, EnsembleNotFoundError
from .storage import EnsembleStorage


class InMemoryEnsembleStorage(EnsembleStorage):
    """
    A storage implementation that stores ensembles in memory.

    This implementation uses a dictionary to store ensembles in memory. Each ensemble is stored with its ID as the key
    and the ensemble object as the value.

    :param ensembles: A dictionary of ensembles to initialize the storage with, default is an empty dictionary
    """

    def __init__(self, ensembles: Dict[str, Ensemble] = {}) -> None:
        self.ensembles: Dict[str, Ensemble] = ensembles

    def create_ensemble(self, ensemble: Ensemble) -> str:
        """
        Create a new ensemble in the storage.

        :param ensemble: The ensemble object to create
        :return: The ID of the created ensemble
        """
        ensemble_id = ensemble.id
        if ensemble_id in self.ensembles:
            raise EnsembleIdAlreadyExists
        self.ensembles[ensemble_id] = ensemble
        return ensemble_id

    def get_ensemble(self, ensemble_id: str) -> Ensemble:
        """
        Get an ensemble from the storage.

        :param ensemble_id: The ID of the ensemble to get
        :return: The ensemble object
        :raises EnsembleNotFoundError: If the ensemble ID is not found in the storage
        """
        if ensemble_id in self.ensembles:
            return self.ensembles[ensemble_id]
        else:
            raise EnsembleNotFoundError

    def update_ensemble(self, ensemble: Ensemble) -> None:
        """
        Update an existing ensemble in the storage.

        :param ensemble: The ensemble object to update
        :raises EnsembleNotFoundError: If the ensemble ID is not found in the storage
        """
        if ensemble.id in self.ensembles:
            self.ensembles[ensemble.id] = ensemble
        else:
            raise EnsembleNotFoundError

    def delete_ensemble(self, ensemble_id: str) -> None:
        """
        Delete an ensemble from the storage.

        :param ensemble_id: The ID of the ensemble to delete
        :raises EnsembleNotFoundError: If the ensemble ID is not found in the storage
        """
        if ensemble_id in self.ensembles:
            del self.ensembles[ensemble_id]
        else:
            raise EnsembleNotFoundError

    def add_ensemble_member(self, ensemble_id: str, member: EnsembleMember) -> None:
        """
        Adds a member to an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble to add the member to.
            member (EnsembleMember): The member to add to the ensemble.

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID.
        """
        if ensemble_id not in self.ensembles:
            raise EnsembleNotFoundError

        self.ensembles[ensemble_id].members[member.id] = member

    def remove_ensemble_member(self, ensemble_id: str, member_id: str) -> None:
        """
        Removes a member from an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble to remove the member from.
            member_id (str): The ID of the member to remove from the ensemble.

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID.
            EnsembleMemberNotFoundError: If no member exists with the given ID in the specified ensemble.
        """
        if ensemble_id not in self.ensembles:
            raise EnsembleNotFoundError

        if member_id not in self.ensembles[ensemble_id].members:
            raise EnsembleMemberNotFoundError

        del self.ensembles[ensemble_id].members[member_id]

    def list_ensemble_ids(self) -> List[str]:
        """
        Lists all ensemble IDs.

        Returns:
            List[str]: A list of ensemble IDs.
        """
        return list(self.ensembles.keys())

    def clean_up(self) -> None:
        """Clean up the in-memory storage"""
        self.ensembles = {}
