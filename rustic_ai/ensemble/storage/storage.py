from abc import ABC, abstractmethod
from typing import List

from ..ensemble import Ensemble, EnsembleMember


class EnsembleStorage(ABC):
    """Abstract base class for ensemble storage."""

    @abstractmethod
    def create_ensemble(self, ensemble: Ensemble) -> str:
        """Create a new ensemble and return its ID"""
        pass  # pragma: no cover

    @abstractmethod
    def get_ensemble(self, ensemble_id: str) -> Ensemble:
        """Get an ensemble by ID"""
        pass  # pragma: no cover

    @abstractmethod
    def update_ensemble(self, ensemble: Ensemble) -> None:
        """Update an existing ensemble"""
        pass  # pragma: no cover

    @abstractmethod
    def delete_ensemble(self, ensemble_id: str) -> None:
        """Delete an ensemble by ID"""
        pass  # pragma: no cover

    @abstractmethod
    def list_ensemble_ids(self) -> List[str]:
        """List all ensemble ids"""
        pass  # pragma: no cover

    @abstractmethod
    def add_ensemble_member(self, ensemble_id: str, member: EnsembleMember) -> None:
        """Add a member to an ensemble"""
        pass  # pragma: no cover

    @abstractmethod
    def remove_ensemble_member(self, ensemble_id: str, member_id: str) -> None:
        """Remove a member from an ensemble"""
        pass  # pragma: no cover

    @abstractmethod
    def clean_up(self) -> None:
        """Clean up the storage"""
        pass  # pragma: no cover
