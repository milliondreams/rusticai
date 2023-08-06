import json
import unittest

from rustic_ai.ensemble import Ensemble, EnsembleMember, MemberCommsType, MemberType


class TestEnsemble(unittest.TestCase):
    # Tests that a member can be added to an empty ensemble
    def test_add_member_to_empty_ensemble(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        member = EnsembleMember(
            id='1',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member)
        assert len(ensemble.members) == 1
        assert ensemble.get_member('1') == member

    # Tests that a member can be added to a non-empty ensemble
    def test_add_member_to_non_empty_ensemble(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        member1 = EnsembleMember(
            id='1',
            name='Test Member 1',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        member2 = EnsembleMember(
            id='2',
            name='Test Member 2',
            member_type=MemberType.HUMAN,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member1)
        ensemble.add_member(member2)
        assert len(ensemble.members) == 2
        assert ensemble.get_member('1') == member1
        assert ensemble.get_member('2') == member2

    # Tests that a member can be removed from an ensemble
    def test_remove_member_from_ensemble(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        member = EnsembleMember(
            id='1',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member)
        ensemble.remove_member('1')
        assert len(ensemble.members) == 0

    # Tests that a member can be retrieved from an ensemble
    def test_get_member_from_ensemble(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        member = EnsembleMember(
            id='1',
            name='Test Member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member)
        assert ensemble.get_member('1') == member

    # Tests that an error is raised when adding a member with the same ID as an existing member
    def test_add_member_with_same_id(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        member1 = EnsembleMember(
            id='1',
            name='Test Member 1',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        member2 = EnsembleMember(
            id='1',
            name='Test Member 2',
            member_type=MemberType.HUMAN,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member1)
        ensemble.add_member(member2)
        assert ensemble.get_member('1').name == 'Test Member 2'
        assert ensemble.get_member('1').member_type == MemberType.HUMAN
        assert ensemble.get_member('1').comms_type == MemberCommsType.WEBSOCKET

    # Tests that an error is raised when attempting to remove a non-existent member
    def test_remove_non_existent_member(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        with self.assertRaises(KeyError):
            ensemble.remove_member('1')

    # Tests that attempting to get a non-existent member raises a KeyError
    def test_nonexistent_member(self):
        ensemble = Ensemble(id='1', name='Test Ensemble')
        with self.assertRaises(KeyError):
            ensemble.get_member('nonexistent_member')

    # Tests that removing all members from an ensemble results in an empty member dictionary
    def test_remove_all_members(self):
        ensemble = Ensemble(id='1', name='test_ensemble')
        member1 = EnsembleMember(
            id='1',
            name='test_member1',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        member2 = EnsembleMember(
            id='2',
            name='test_member2',
            member_type=MemberType.HUMAN,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member1)
        ensemble.add_member(member2)
        assert len(ensemble.members) == 2
        ensemble.remove_member(member1.id)
        assert len(ensemble.members) == 1
        ensemble.remove_member(member2.id)
        assert len(ensemble.members) == 0

    # Tests that an ensemble can be serialized to JSON
    def test_serialize_ensemble(self):
        ensemble = Ensemble(id='1', name='test_ensemble')
        member1 = EnsembleMember(
            id='1',
            name='test_member1',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        member2 = EnsembleMember(
            id='2',
            name='test_member2',
            member_type=MemberType.HUMAN,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        ensemble.add_member(member1)
        ensemble.add_member(member2)
        serialized_ensemble = ensemble.serialize()
        json_ensemble = json.loads(serialized_ensemble)

        assert json_ensemble['id'] == '1'
        assert json_ensemble['name'] == 'test_ensemble'
        assert json_ensemble['members']['1']['id'] == '1'
        assert json_ensemble['members']['1']['name'] == 'test_member1'
        assert MemberType(json_ensemble['members']['1']['member_type']) == MemberType.BOT
        assert MemberCommsType(json_ensemble['members']['1']['comms_type']) == MemberCommsType.WEBSOCKET
        assert json_ensemble['members']['1']['endpoint'] is None
        assert json_ensemble['members']['1']['is_active'] is True
        assert json_ensemble['members']['2']['id'] == '2'
        assert json_ensemble['members']['2']['name'] == 'test_member2'
        assert MemberType(json_ensemble['members']['2']['member_type']) == MemberType.HUMAN
        assert MemberCommsType(json_ensemble['members']['2']['comms_type']) == MemberCommsType.WEBSOCKET
        assert json_ensemble['members']['2']['endpoint'] is None
        assert json_ensemble['members']['2']['is_active'] is True

    # Tests that an ensemble can be deserialized from JSON
    def test_deserialize_ensemble(self):
        serialized_ensemble = {
            'id': '1',
            'name': 'test_ensemble',
            'members': {
                '1': {
                    'id': '1',
                    'name': 'test_member1',
                    'member_type': 'bot',
                    'comms_type': 'websocket',
                    'endpoint': None,
                    'is_active': True,
                },
                '2': {
                    'id': '2',
                    'name': 'test_member2',
                    'member_type': 'human',
                    'comms_type': 'websocket',
                    'endpoint': None,
                    'is_active': True,
                },
            },
        }
        ensemble = Ensemble.deserialize(json.dumps(serialized_ensemble))
        assert ensemble.id == '1'
        assert ensemble.name == 'test_ensemble'
        assert len(ensemble.members) == 2
        assert ensemble.get_member('1').name == 'test_member1'
        assert ensemble.get_member('1').member_type == MemberType.BOT
        assert ensemble.get_member('1').comms_type == MemberCommsType.WEBSOCKET
        assert ensemble.get_member('1').endpoint is None
        assert ensemble.get_member('1').is_active is True
        assert ensemble.get_member('2').name == 'test_member2'
        assert ensemble.get_member('2').member_type == MemberType.HUMAN
        assert ensemble.get_member('2').comms_type == MemberCommsType.WEBSOCKET
        assert ensemble.get_member('2').endpoint is None
        assert ensemble.get_member('2').is_active is True

    # Test validations in Ensemble dataclass work as expected
    def test_ensemble_validations(self):
        e1 = Ensemble(id='1', name='Test', members=None)
        assert e1.id == '1'
        with self.assertRaises(ValueError):
            Ensemble(id=None, name="Test")
        with self.assertRaises(ValueError):
            Ensemble(id='1', name=None)
        with self.assertRaises(ValueError):
            Ensemble(id='1', name='')
        with self.assertRaises(TypeError):
            EnsembleMember()
        with self.assertRaises(TypeError):
            EnsembleMember(id='1', name=None)
        with self.assertRaises(TypeError):
            EnsembleMember(id='1', name='')
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=None,
                comms_type=MemberCommsType.HTTP,
                endpoint='http://localhost:8080',
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type='invalid_member_type',
                comms_type=MemberCommsType.HTTP,
                endpoint='http://localhost:8080',
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=MemberType.BOT,
                comms_type=None,
                endpoint='http://localhost:8080',
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=MemberType.BOT,
                comms_type='invalid_comms_type',
                endpoint='http://localhost:8080',
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=MemberType.BOT,
                comms_type=MemberCommsType.WEBHOOK,
                endpoint=None,
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=MemberType.BOT,
                comms_type=MemberCommsType.WEBHOOK,
                endpoint='',
                is_active=False,
            )
        with self.assertRaises(ValueError):
            EnsembleMember(
                id='1',
                name='test_member',
                member_type=MemberType.BOT,
                comms_type=MemberCommsType.WEBHOOK,
                endpoint='invalid_endpoint',
                is_active=False,
            )

    # Test that and ensemble member can be serialized and deserialized
    def test_serialize_deserialize_ensemble_member(self):
        member = EnsembleMember(
            id='1',
            name='test_member',
            member_type=MemberType.BOT,
            comms_type=MemberCommsType.WEBSOCKET,
            endpoint=None,
            is_active=True,
        )
        serialized_member = member.serialize()
        json_member = json.loads(serialized_member)

        assert json_member['id'] == '1'
        assert json_member['name'] == 'test_member'
        assert MemberType(json_member['member_type']) == MemberType.BOT
        assert MemberCommsType(json_member['comms_type']) == MemberCommsType.WEBSOCKET
        assert json_member['endpoint'] is None
        assert json_member['is_active'] is True

        member = EnsembleMember.deserialize(serialized_member)
        assert member.id == '1'
        assert member.name == 'test_member'
        assert member.member_type == MemberType.BOT
        assert member.comms_type == MemberCommsType.WEBSOCKET
        assert member.endpoint is None
        assert member.is_active is True


if __name__ == '__main__':
    unittest.main()
