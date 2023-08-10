from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, String, create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from ..ensemble import Ensemble, EnsembleMember
from .exceptions import EnsembleIdAlreadyExists, EnsembleMemberNotFoundError, EnsembleNotFoundError
from .storage import EnsembleStorage

Base = declarative_base()


class EnsembleMemberModel(Base):
    """
    Defines the database schema for the ensemble_members table.
    """

    __tablename__ = 'ensemble_members'

    id = Column(String, primary_key=True)
    ensemble_id = Column(String, ForeignKey('ensembles.id'), primary_key=True)
    name = Column(String)
    member_type = Column(String)
    comms_type = Column(String)
    endpoint = Column(String)
    is_active = Column(Boolean)


class EnsembleModel(Base):
    """
    Defines the database schema for the ensembles table.
    """

    __tablename__ = 'ensembles'

    id = Column(String, primary_key=True)
    name = Column(String)
    members = relationship("EnsembleMemberModel", backref="ensemble")


class SqlEnsembleStorage(EnsembleStorage):
    """
    SQLAlchemy implementation of EnsembleStorage.
    """

    def __init__(self, connection_string):
        """
        Initialize the SQLAlchemy engine and session.
        """
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_ensemble(self, ensemble):
        """
        Create a new ensemble in the database.
        """
        try:
            with self.Session.begin() as session:
                # Create a new EnsembleModel object and add it to the session
                ensemble_model = EnsembleModel(id=ensemble.id, name=ensemble.name)
                session.add(ensemble_model)

                # Create EnsembleMemberModel objects for each member and add them to the session
                for member in ensemble.members.values():
                    member_model = EnsembleMemberModel(
                        id=member.id,
                        name=member.name,
                        member_type=member.member_type,
                        comms_type=member.comms_type,
                        endpoint=member.endpoint,
                        is_active=member.is_active,
                        ensemble_id=ensemble.id,
                    )
                    session.add(member_model)
        except exc.IntegrityError:
            raise EnsembleIdAlreadyExists

        return ensemble.id

    def get_ensemble(self, ensemble_id):
        """
        Retrieve an existing ensemble from the database.
        """
        with self.Session() as session:
            # Query the database for the EnsembleModel object with the given ID
            ensemble = session.query(EnsembleModel).get(ensemble_id)

            # If no ensemble is found, raise an EnsembleNotFoundError
            if not ensemble:
                raise EnsembleNotFoundError

            # Create an Ensemble object from the retrieved data and return it
            members = {
                m.id: EnsembleMember(
                    id=m.id,
                    name=m.name,
                    member_type=m.member_type,
                    comms_type=m.comms_type,
                    endpoint=m.endpoint,
                    is_active=m.is_active,
                )
                for m in ensemble.members
            }
            return Ensemble(id=ensemble.id, name=ensemble.name, members=members)

    def update_ensemble(self, ensemble: Ensemble) -> None:
        """
        Update an existing ensemble in the database.

        Args:
            ensemble (Ensemble): The ensemble object to update

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID
        """
        with self.Session.begin() as session:
            # Query the database for the EnsembleModel object with the given ID
            existing = session.query(EnsembleModel).get(ensemble.id)

            # If no ensemble is found, raise an EnsembleNotFoundError
            if not existing:
                raise EnsembleNotFoundError

            # Update the name of the ensemble
            existing.name = ensemble.name

            # Update or create EnsembleMemberModel objects for each member
            for member in ensemble.members.values():
                member_model = session.query(EnsembleMemberModel).get((member.id, ensemble.id))
                if member_model:
                    member_model.name = member.name
                    member_model.member_type = member.member_type
                    member_model.comms_type = member.comms_type
                    member_model.endpoint = member.endpoint
                    member_model.is_active = member.is_active
                else:
                    member_model = EnsembleMemberModel(
                        id=member.id,
                        name=member.name,
                        member_type=member.member_type,
                        comms_type=member.comms_type,
                        endpoint=member.endpoint,
                        is_active=member.is_active,
                        ensemble_id=ensemble.id,
                    )
                    session.add(member_model)

    def delete_ensemble(self, ensemble_id: str) -> None:
        """
        Delete an ensemble from the database.

        Args:
            ensemble_id (str): The ID of the ensemble to delete

        Raises:
            EnsembleNotFoundError: If no ensemble exists with the given ID
        """
        with self.Session.begin() as session:
            # Query the database for the EnsembleModel object with the given ID
            ensemble = session.query(EnsembleModel).get(ensemble_id)

            # If no ensemble is found, raise an EnsembleNotFoundError
            if not ensemble:
                raise EnsembleNotFoundError

            # Delete the ensemble and its associated members from the database
            session.delete(ensemble)

    def get_ensembles(self) -> List[Ensemble]:
        """
        Lists all ensembles stored in the SQL database.

        Returns:
            List[Ensemble]: A list of Ensemble objects.
        """
        with self.Session() as session:
            # Query the database for all EnsembleModel objects
            ensembles = session.query(EnsembleModel).all()

            # Create an Ensemble object from the retrieved data for each ensemble
            return [
                Ensemble(
                    id=ensemble.id,
                    name=ensemble.name,
                    members={
                        m.id: EnsembleMember(
                            id=m.id,
                            name=m.name,
                            member_type=m.member_type,
                            comms_type=m.comms_type,
                            endpoint=m.endpoint,
                            is_active=m.is_active,
                        )
                        for m in ensemble.members
                    },
                )
                for ensemble in ensembles
            ]

    def get_ensemble_ids(self):
        """
        Lists the IDs of all ensembles stored in the SQL database.

        Returns:
            List[str]: A list of ensemble IDs.
        """
        with self.Session() as session:
            return [r[0] for r in session.query(EnsembleModel.id)]

    def add_ensemble_member(self, ensemble_id, member):
        """
        Adds a member to an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble to add the member to.
            member (EnsembleMember): The member to add to the ensemble.
        """
        with self.Session.begin() as session:
            ensemble = session.query(EnsembleModel).get(ensemble_id)
            if ensemble:
                ensemble_member = EnsembleMemberModel(
                    id=member.id,
                    name=member.name,
                    member_type=member.member_type,
                    comms_type=member.comms_type,
                    endpoint=member.endpoint,
                    ensemble=ensemble,
                )
                session.add(ensemble_member)
            else:
                raise EnsembleNotFoundError

    def remove_ensemble_member(self, ensemble_id, member_id):
        """
        Removes a member from an ensemble.

        Args:
            ensemble_id (str): The ID of the ensemble to remove the member from.
            member_id (str): The ID of the member to remove from the ensemble.
        """
        with self.Session.begin() as session:
            ensemble = session.query(EnsembleModel).get(ensemble_id)
            if ensemble:
                member = session.query(EnsembleMemberModel).get((member_id, ensemble_id))
                if member:
                    session.delete(member)
                else:
                    raise EnsembleMemberNotFoundError
            else:
                raise EnsembleNotFoundError

    def clean_up(self) -> None:
        """Clean up the SQL storage"""
        with self.Session.begin() as session:
            # Delete all ensembles and their associated members from the database
            session.query(EnsembleModel).delete()
            session.query(EnsembleMemberModel).delete()

    def close_connection(self) -> None:
        """Close the SQL connection"""
        self.engine.dispose()
