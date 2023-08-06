import unittest

from rustic_ai.ensemble import EnsembleMember, MemberCommsType, MemberType


class TestEnsembleMember(unittest.TestCase):
    # Tests that an EnsembleMember object can be created with all required attributes
    def test_create_ensemble_member(self):
        member = EnsembleMember(
            id='123',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint='http://localhost:5000',
            is_active=True,
        )
        self.assertEqual(member.id, '123')
        self.assertEqual(member.name, 'Test Member')
        self.assertEqual(member.member_type, MemberType.BOT)
        self.assertEqual(member.comms_type, MemberCommsType.HTTP)
        self.assertEqual(member.endpoint, 'http://localhost:5000')
        self.assertTrue(member.is_active)

    # Tests that an EnsembleMember can be activated
    def test_activate_ensemble_member(self):
        member = EnsembleMember(
            id='123',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint='http://localhost:5000',
            is_active=False,
        )
        member.activate()
        self.assertTrue(member.is_active)

    # Tests that an EnsembleMember can be deactivated
    def test_deactivate_ensemble_member(self):
        member = EnsembleMember(
            id='123',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint='http://localhost:5000',
            is_active=True,
        )
        member.deactivate()
        self.assertFalse(member.is_active)

    # Tests that an error is raised when creating an EnsembleMember object with empty id
    def test_create_ensemble_member_empty_id(self):
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='',
                name='Test Member',
                member_type=MemberType.BOT,
                comms_type=MemberCommsType.HTTP,
                endpoint='http://localhost:5000',
                is_active=True,
            )

    # Tests that an error is raised when creating an EnsembleMember object with empty name
    def test_create_ensemble_member_empty_name(self):
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='123',
                name='',
                member_type=MemberType.BOT,
                comms_type=MemberCommsType.HTTP,
                endpoint='http://localhost:5000',
                is_active=True,
            )

    # Tests that an error is raised when creating an EnsembleMember object with invalid member_type
    def test_create_ensemble_member_invalid_member_type(self):
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='123',
                name='Test Member',
                member_type=None,
                comms_type=MemberCommsType.HTTP,
                endpoint='http://localhost:5000',
                is_active=True,
            )

    # Tests that an EnsembleMember object can be created with empty endpoint
    def test_create_ensemble_member_empty_endpoint(self):
        member = EnsembleMember(
            id='123',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint=None,
            is_active=True,
        )
        self.assertIsNone(member.endpoint)

    # Tests that an EnsembleMember object can be created with optional attributes
    def test_create_ensemble_member_optional_attributes(self):
        member = EnsembleMember(
            id='123',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint='http://localhost:5000',
            is_active=True,
        )
        self.assertEqual(member.id, '123')
        self.assertEqual(member.name, 'Test Member')
        self.assertEqual(member.member_type, MemberType.BOT)
        self.assertEqual(member.comms_type, MemberCommsType.HTTP)
        self.assertEqual(member.endpoint, 'http://localhost:5000')
        self.assertTrue(member.is_active)

    # Tests that a ValueError is raised when creating an EnsembleMember object with an invalid comms_type
    def test_invalid_comms_type(self):
        with self.assertRaises(ValueError) as context:
            EnsembleMember(
                id='1', name='test', member_type=MemberType.BOT, comms_type='invalid', endpoint=None, is_active=True
            )
        self.assertTrue('Ensemble member communication type must be a MemberCommsType' in str(context.exception))

    # Tests that deactivating an already inactive EnsembleMember does not change its active status
    def test_deactivate_inactive_member(self):
        member = EnsembleMember(
            id='1',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.HTTP,
            endpoint='http://test.com',
            is_active=False,
        )
        member.deactivate()
        self.assertFalse(member.is_active)
        member.deactivate()
        self.assertFalse(member.is_active)
