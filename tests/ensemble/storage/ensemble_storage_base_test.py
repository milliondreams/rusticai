from abc import ABC, abstractmethod

from rustic_ai.ensemble import Ensemble, EnsembleMember, MemberCommsType, MemberType
from rustic_ai.ensemble.storage import (
    EnsembleIdAlreadyExists,
    EnsembleMemberNotFoundError,
    EnsembleNotFoundError,
    EnsembleStorage,
)
from rustic_ai.ensemble.storage.ensemble_factory import EnsembleStorageFactory


class AbstractTests(object):
    class TestEnsembleStorageABC(ABC):
        """
        A base test class for testing ensemble storage implementations.

        This class defines a set of tests that can be used to test any ensemble storage implementation
        that implements the `EnsembleStorage` interface.

        To use this class, you need to subclass it and implement the `get_storage_config()` method to return an
        instance of the ensemble storage implementation you want to test.

        """

        @abstractmethod
        def get_storage_config(self) -> dict:
            """
            Get the configuration for the ensemble storage implementation to test.

            :return: The configuration for the ensemble storage implementation
            """
            pass

        def get_storage(self) -> EnsembleStorage:
            """
            Get an instance of the ensemble storage implementation to test.

            :return: An instance of the ensemble storage implementation
            """
            if '_storage' not in self.__dict__:
                self._storage = EnsembleStorageFactory.from_config(self.get_storage_config())
            return self._storage

        def setUp(self):
            """
            Set up the test case.

            This method is called before each test method is run. It sets up the ensemble storage instance
            to use for the tests.
            """
            self.storage = self.get_storage()

        def tearDown(self):
            """
            Tear down the test case.

            This method is called after each test method is run. It cleans up the ensemble storage instance.
            """
            self.storage.clean_up()

        def test_create_and_get_ensemble(self):
            """
            Test creating and getting an ensemble from the storage.

            This test creates a new ensemble in the storage, retrieves it by ID, and checks that it matches
            the original ensemble object.
            """
            ensemble_member = EnsembleMember(
                "member1", "Test Member 1", MemberType.BOT, MemberCommsType.HTTP, "http://loclahost/", True
            )
            ensemble = Ensemble("test1", "Test Ensemble", {"member1": ensemble_member})
            ensemble_id = self.storage.create_ensemble(ensemble)

            retrieved = self.storage.get_ensemble(ensemble_id)
            self.assertEqual(retrieved, ensemble)

        def test_update_ensemble(self):
            """
            Test updating an ensemble in the storage.

            This test creates a new ensemble in the storage, updates its name, and checks that the
            updated name is reflected in the storage.
            """
            ensemble = Ensemble(
                "test2",
                "Test Ensemble",
                {
                    "1": EnsembleMember(
                        "1", "Test Member 1", MemberType.BOT, MemberCommsType.HTTP, "http://loclahost/", True
                    )
                },
            )
            ensemble_id = self.storage.create_ensemble(ensemble)

            ensemble.name = "Updated Name"
            self.storage.update_ensemble(ensemble)

            updated = self.storage.get_ensemble(ensemble_id)
            self.assertEqual(updated.name, "Updated Name")

            ensemble.name = "Updated Name 2"
            ensemble.add_member(
                EnsembleMember("2", "Test Member 2", MemberType.BOT, MemberCommsType.HTTP, "http://loclahost/", True)
            )

            self.storage.update_ensemble(ensemble)

            updated1 = self.storage.get_ensemble(ensemble_id)
            self.assertCountEqual(updated1.members.keys(), ["1", "2"])

        def test_list_ensemble_ids(self):
            """
            Test listing ensemble IDs from the storage.

            This test creates a number of ensembles in the storage, and checks that the list of ensemble
            IDs returned by the storage matches the list of IDs of the created ensembles.
            """

            self.storage.clean_up()
            ensemble_ids = []
            for i in range(5):
                ensemble = Ensemble(f"teste{i}", f"Test Ensemble {i}")
                ensemble_ids.append(self.storage.create_ensemble(ensemble))

            retrieved_ids = self.storage.list_ensemble_ids()
            self.assertCountEqual(retrieved_ids, ensemble_ids)

        def test_get_missing_ensemble(self):
            """
            Test getting a missing ensemble from the storage.

            This test tries to retrieve an ensemble that does not exist in the storage and checks that an
            `EnsembleNotFoundError` is raised.
            """
            missing_id = "missing"
            with self.assertRaises(EnsembleNotFoundError):
                self.storage.get_ensemble(missing_id)

        def test_update_missing_ensemble(self):
            """
            Test updating a missing ensemble in the storage.

            This test tries to update an ensemble that does not exist in the storage and checks that an
            `EnsembleNotFoundError` is raised.
            """
            missing_ensemble = Ensemble("missing", "Test")
            with self.assertRaises(EnsembleNotFoundError):
                self.storage.update_ensemble(missing_ensemble)

        def test_delete_ensemble(self):
            """
            Test deleting an ensemble from the storage.

            This test creates an ensemble in the storage, deletes it, and checks that it is no longer
            present in the storage.
            """
            ensemble = Ensemble("test3", "Test")
            ensemble_id = self.storage.create_ensemble(ensemble)
            retrieved = self.storage.get_ensemble(ensemble_id)

            self.assertEqual(retrieved, ensemble)

            self.storage.delete_ensemble(ensemble_id)

            with self.assertRaises(EnsembleNotFoundError):
                self.storage.get_ensemble(ensemble_id)

        def test_delete_missing_ensemble(self):
            """
            Test deleting a missing ensemble from the storage.

            This test tries to delete an ensemble that does not exist in the storage and checks that an
            `EnsembleNotFoundError` is raised.
            """
            missing_id = "missing"
            with self.assertRaises(EnsembleNotFoundError):
                self.storage.delete_ensemble(missing_id)

        def test_duplicate_ensemble_id(self):
            """
            Test creating an ensemble with a duplicate ID in the storage.

            This test creates an ensemble in the storage with a given ID, and then tries to create another
            ensemble with the same ID. It checks that an `EnsembleIdAlreadyExists` exception is raised.
            """
            ensemble = Ensemble("test3", "Test")
            self.storage.create_ensemble(ensemble)

            duplicate = Ensemble("test3", "Duplicate")
            with self.assertRaises(EnsembleIdAlreadyExists):
                self.storage.create_ensemble(duplicate)

        def test_add_member_to_ensemble(self):
            """
            Test adding a member to an ensemble in the storage.

            This test creates an ensemble in the storage, adds a member to it, and checks that the member
            is present in the ensemble.
            """
            ensemble = Ensemble('testm0', 'Test Ensemble')
            ensemble_id = self.storage.create_ensemble(ensemble)

            member = EnsembleMember(
                'member1', 'Test Member', MemberType.BOT, MemberCommsType.HTTP, 'http://localhost', True
            )
            self.storage.add_ensemble_member(ensemble_id, member)

            retrieved = self.storage.get_ensemble(ensemble_id)
            self.assertIn(member.id, retrieved.members)

        def test_remove_member_from_ensemble(self):
            """
            Test removing a member from an ensemble in the storage.

            This test creates an ensemble in the storage, adds a member to it, removes the member, and
            checks that the member is no longer present in the ensemble.
            """
            ensemble = Ensemble('testm1', 'Test Ensemble')
            ensemble_id = self.storage.create_ensemble(ensemble)

            member = EnsembleMember(
                'member1', 'Test Member', MemberType.BOT, MemberCommsType.HTTP, 'http://localhost', True
            )
            self.storage.add_ensemble_member(ensemble_id, member)
            retrieved0 = self.storage.get_ensemble(ensemble_id)
            self.assertIn(member.id, retrieved0.members)

            self.storage.remove_ensemble_member(ensemble_id, member.id)
            retrieved = self.storage.get_ensemble(ensemble_id)
            self.assertNotIn(member.id, retrieved.members)

        def test_add_member_to_missing_ensemble(self):
            """
            Test adding a member to a missing ensemble in the storage.

            This test tries to add a member to an ensemble that does not exist in the storage and checks
            that an `EnsembleNotFoundError` is raised.
            """
            ensemble_storage = self.get_storage()
            ensemble = Ensemble('testm2', 'Test Ensemble')
            ensemble_storage.create_ensemble(ensemble)

            member = EnsembleMember(
                'member1', 'Test Member', MemberType.BOT, MemberCommsType.HTTP, 'http://localhost', True
            )

            with self.assertRaises(EnsembleNotFoundError):
                ensemble_storage.add_ensemble_member('missing', member)

        def test_remove_member_from_missing_ensemble(self):
            """
            Test removing a member from a missing ensemble in the storage.

            This test tries to remove a member from an ensemble that does not exist in the storage and
            checks that an `EnsembleNotFoundError` is raised.
            """
            ensemble_storage = self.get_storage()
            ensemble = Ensemble('testm3', 'Test Ensemble')
            ensemble_id = ensemble_storage.create_ensemble(ensemble)

            member = EnsembleMember(
                'member1', 'Test Member', MemberType.BOT, MemberCommsType.HTTP, 'http://localhost', True
            )
            ensemble_storage.add_ensemble_member(ensemble_id, member)

            with self.assertRaises(EnsembleNotFoundError):
                ensemble_storage.remove_ensemble_member("missing_ensemble", 'missing_member')

        def test_remove_missing_member(self):
            """
            Test removing a missing member from an ensemble in the storage.

            This test tries to remove a member from an ensemble that does not exist in the storage and
            checks that an `EnsembleMemberNotFoundError` is raised.
            """
            ensemble = Ensemble('testm4', 'Test Ensemble')
            ensemble_id = self.storage.create_ensemble(ensemble)

            member = EnsembleMember(
                'member1', 'Test Member', MemberType.BOT, MemberCommsType.HTTP, 'http://localhost', True
            )
            self.storage.add_ensemble_member(ensemble_id, member)

            missing_member_id = 'missing_member'
            with self.assertRaises(EnsembleMemberNotFoundError):
                self.storage.remove_ensemble_member(ensemble_id, missing_member_id)

            retrieved = self.storage.get_ensemble(ensemble_id)
            self.assertIn(member.id, retrieved.members)
