from typing import Dict

import redis

from ..ensemble import Ensemble, EnsembleMember
from .exceptions import EnsembleIdAlreadyExists, EnsembleMemberNotFoundError, EnsembleNotFoundError
from .storage import EnsembleStorage


class RedisEnsembleStorage(EnsembleStorage):
    """
    Redis based storage for Ensembles.

    Uses Redis hashes to store ensemble data.
    """

    def __init__(self, redis_connection: str, redis_class=redis.StrictRedis):
        """
        Initializes the Redis client.
        """
        self.redis = redis_class.from_url(redis_connection, decode_responses=True)

    def _get_ensemble_key(self, ensemble_id: str) -> str:
        """
        Gets the Redis key for an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble.

        Returns:
            str: The Redis key for the ensemble.
        """
        return f"ensemble:{ensemble_id}"

    def create_ensemble(self, ensemble: Ensemble) -> str:
        """
        Creates a new ensemble in Redis.

        Args:
            ensemble (Ensemble): The ensemble to create.

        Returns:
            str: The ID of the newly created ensemble.
        """
        ensemble_id = ensemble.id
        ensemble_key = self._get_ensemble_key(ensemble_id)

        dataE = self.redis.hget(ensemble_key, 'd')
        if dataE:
            raise EnsembleIdAlreadyExists

        data = ensemble.serialize()

        self.redis.hset(ensemble_key, 'd', data)

        return ensemble_id

    def get_ensemble(self, ensemble_id: str) -> Ensemble:
        """
        Retrieves an existing ensemble from Redis.

        Args:
            ensemble_id (str): The ID of the ensemble to retrieve.

        Returns:
            Ensemble: The retrieved ensemble.

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID.
        """
        ensemble_key = self._get_ensemble_key(ensemble_id)
        data = self.redis.hget(ensemble_key, 'd')

        if not data:
            raise EnsembleNotFoundError
        ensemble = Ensemble.deserialize(data)

        return ensemble

    def update_ensemble(self, ensemble: Ensemble) -> None:
        """
        Updates an existing ensemble in Redis.

        Args:
            ensemble (Ensemble): The ensemble to update.
        """
        ensemble_key = self._get_ensemble_key(ensemble.id)
        current_ensemble = self.get_ensemble(ensemble.id)

        if current_ensemble.members:
            new_members = current_ensemble.members
            new_members.update(ensemble.members)
        else:
            new_members = ensemble.members

        ensemble.members = new_members

        data = ensemble.serialize()
        self.redis.hset(ensemble_key, 'd', data)

    def list_ensemble_ids(self) -> list:
        """
        Lists all ensembles in Redis.

        Returns:
            list: A list of ensemble IDs.
        """
        all_keys = self.redis.keys("ensemble:*")
        return [key[9:] for key in all_keys]

    def delete_ensemble(self, ensemble_id: str) -> None:
        """
        Deletes an existing ensemble from Redis.

        Args:
            ensemble_id (str): The ID of the ensemble to delete.

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID.
        """
        ensemble_key = self._get_ensemble_key(ensemble_id)
        self.get_ensemble(ensemble_id)
        self.redis.delete(ensemble_key)

    def add_ensemble_member(self, ensemble_id: str, member: EnsembleMember) -> None:
        """
        Add a member to an ensemble in Redis.
        """
        # Get ensemble
        ensemble = self.get_ensemble(ensemble_id)
        ensemble.members[member.id] = member

        # Update ensemble JSON
        self.update_ensemble(ensemble)

    def get_ensemble_members(self, ensemble_id: str) -> Dict[str, EnsembleMember]:
        """
        Get all members of an ensemble from Redis.
        """
        # Get ensemble
        ensemble = self.get_ensemble(ensemble_id)

        return ensemble.members

    def remove_ensemble_member(self, ensemble_id: str, member_id: str) -> None:
        """
        Removes a member from an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble to remove the member from.
            member_id (str): The ID of the member to remove from the ensemble.
        """
        # Get ensemble
        ensemble = self.get_ensemble(ensemble_id)

        # Check if member exists
        if member_id not in ensemble.members:
            raise EnsembleMemberNotFoundError

        # Remove member
        del ensemble.members[member_id]

        ensemble_key = self._get_ensemble_key(ensemble_id)
        # Update ensemble JSON
        self.redis.hset(ensemble_key, 'd', ensemble.serialize())

    def clean_up(self) -> None:
        """
        Deletes all ensembles from Redis.
        """
        self.redis.flushall()
