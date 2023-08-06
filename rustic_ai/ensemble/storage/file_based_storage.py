import json
import os
from typing import List

from ..ensemble import Ensemble, EnsembleDecoder, EnsembleEncoder, EnsembleMember
from .exceptions import EnsembleIdAlreadyExists, EnsembleMemberNotFoundError, EnsembleNotFoundError
from .storage import EnsembleStorage


class FileEnsembleStorage(EnsembleStorage):
    """
    A file based storage implementation for Ensemble.

    This stores each ensemble in a separate JSON file, with the filename being the ensemble ID.

    Attributes:
        directory (str): The directory path to store ensemble files.
    """

    def __init__(self, directory: str) -> None:
        """
        Initialize the file based ensemble storage.

        Args:
            directory (str): The directory to store ensemble files.
        """
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def _get_ensemble_path(self, ensemble_id: str) -> str:
        """
        Get the file path for an ensemble based on its ID.

        Args:
            ensemble_id (str): The ensemble ID

        Returns:
            str: The file path
        """
        return os.path.join(self.directory, f"{ensemble_id}.json")

    def create_ensemble(self, ensemble: Ensemble) -> str:
        """
        Create a new ensemble by writing it to a file.

        Args:
            ensemble (Ensemble): The ensemble to create

        Returns:
            str: The ensemble ID

        Raises:
            EnsembleIdAlreadyExists: If ensemble with given ID already exists
        """
        path = self._get_ensemble_path(ensemble.id)
        if os.path.exists(path):
            raise EnsembleIdAlreadyExists

        with open(path, "w") as f:
            json.dump(ensemble, f, cls=EnsembleEncoder)

        return ensemble.id

    def get_ensemble(self, ensemble_id: str) -> Ensemble:
        """
        Load an ensemble from file storage.

        Args:
            ensemble_id (str): The ensemble ID

        Returns:
            Ensemble: The ensemble object

        Raises:
            EnsembleNotFoundError: If no file found for the given ID
        """
        path = self._get_ensemble_path(ensemble_id)
        if not os.path.exists(path):
            raise EnsembleNotFoundError

        with open(path) as f:
            data = json.load(f, cls=EnsembleDecoder)
            return data

    def update_ensemble(self, ensemble: Ensemble) -> None:
        """
        Update an existing ensemble in the storage.

        :param ensemble: The ensemble object to update
        :raises EnsembleNotFoundError: If no ensemble exists with the given ID
        """
        path = self._get_ensemble_path(ensemble.id)
        if not os.path.exists(path):
            raise EnsembleNotFoundError

        with open(path, "w") as f:
            json.dump(ensemble, f, cls=EnsembleEncoder)

    def delete_ensemble(self, ensemble_id: str) -> None:
        """
        Delete an ensemble from the storage.

        :param ensemble_id: The ID of the ensemble to delete
        :raises EnsembleNotFoundError: If no ensemble exists with the given ID
        """
        path = self._get_ensemble_path(ensemble_id)
        if not os.path.exists(path):
            raise EnsembleNotFoundError

        os.remove(path)

    def add_ensemble_member(self, ensemble_id: str, member: EnsembleMember) -> None:
        """
        Add a member to an ensemble.

        :param ensemble_id: The ID of the ensemble to add the member to
        :param member: The member to add
        :raises EnsembleNotFoundError: If no ensemble exists with the given ID
        """
        ensemble = self.get_ensemble(ensemble_id)
        ensemble.members[member.id] = member
        self.update_ensemble(ensemble)

    def remove_ensemble_member(self, ensemble_id: str, member_id: str) -> None:
        """
        Remove a member from an ensemble.

        :param ensemble_id: The ID of the ensemble to remove the member from
        :param member_id: The ID of the member to remove
        :raises EnsembleNotFoundError: If no ensemble exists with the given ID
        :raises EnsembleMemberNotFoundError: If no member exists with the given IDs
        """
        ensemble = self.get_ensemble(ensemble_id)
        if member_id not in ensemble.members:
            raise EnsembleMemberNotFoundError

        del ensemble.members[member_id]
        self.update_ensemble(ensemble)

    def list_ensemble_ids(self) -> List[str]:
        """
        List the IDs of all ensembles stored in the file storage.

        :return: A list of ensemble IDs
        """
        return [f.split('.')[0] for f in os.listdir(self.directory) if f.endswith('.json')]

    def clean_up(self) -> None:
        """Clean up the file storage"""
        for file in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, file))
