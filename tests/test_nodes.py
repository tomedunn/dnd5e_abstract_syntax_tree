import pytest
from icepool import d, Die
from dndast.nodes import *

def test_node_from_dict():
    tree = dict_to_node(
        {
            'node': 'Attack',
            'targeting': {
                'node': 'Targeting',
                'range': '5 feet',
                'area': None,
                'max_targets': 1,
                'min_targets': 0,
            },
            'attack_roll': {
                'node': 'AttackRoll',
                'critical_hit_range': [20],
                'critical_miss_range': [1],
                'attack_bonus': 4,
                'armor_class': {
                    'node': 'Reference',
                    'value': 'target.armor_class',
                },
            },
            'results': {
                'critical miss': 0,
                'miss': 0,
                'hit': {'node': 'Damage', 'value': '1d6', 'type': 'slashing'},
                'critical hit': {'node': 'Damage', 'value': '2d6', 'type': 'slashing'},
            },
        }
    )

    assert tree == AttackNode(
            targeting=TargetingNode(
                range='5 feet',
                area=None,
                max_targets=1,
                min_targets=0,
            ),
            attack_roll=AttackRollNode(
                critical_hit_range=[20],
                critical_miss_range=[1],
                attack_bonus=4,
                armor_class=ReferenceNode('target.armor_class'),
            ),
            results={
                'critical miss': 0,
                'miss': 0,
                'hit': DamageNode('1d6', 'slashing'),
                'critical hit': DamageNode('2d6', 'slashing'),
            },
        )

def test_node_attackroll():
    tree = AttackRollNode(**{
        'critical_hit_range': [19,20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': 12,
    })
    assert tree.to_dict() == {
        'node': 'AttackRoll',
        'critical_hit_range': [19,20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': 12,
    }

    tree = AttackRollNode(**{
        'critical_hit_range': [19,20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': ReferenceNode('target.AC'),
    })
    assert tree.to_dict() == {
        'node': 'AttackRoll',
        'critical_hit_range': [19,20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': {
            'node': 'Reference',
            'value': 'target.AC',
        },
    }

def test_node_saveroll():
    tree = SaveRollNode(**{
        'save_dc': 12,
        'save_bonus': 4,
    })
    assert tree.to_dict() == {
        'node': 'SaveRoll',
        'save_dc': 12,
        'save_bonus': 4,
    }

    tree = SaveRollNode(**{
        'save_dc': 12,
        'save_bonus': ReferenceNode('target.dexterity_save_bonus'),
    })
    assert tree.to_dict() == {
        'node': 'SaveRoll',
        'save_dc': 12,
        'save_bonus': {
            'node': 'Reference',
            'value': 'target.dexterity_save_bonus',
        },
    }

def test_node_selection():
    tree = SelectionNode(
        selector=AttackRollNode(**{
            'critical_hit_range': [19,20],
            'critical_miss_range': [1],
            'attack_bonus': 4,
            'armor_class': ReferenceNode('target.AC'),
        }),
        results={
            'critical miss': 0,
            'miss': 0,
            'hit': 1,
            'critical hit': 2,
        },
    )

    assert tree.to_dict() == {
        'node': 'Selection',
        'selector': {
            'node': 'AttackRoll',
            'critical_hit_range': [19,20],
            'critical_miss_range': [1],
            'attack_bonus': 4,
            'armor_class': {
                'node': 'Reference',
                'value': 'target.AC',
            },
        },
        'results': {
            'critical miss': 0,
            'miss': 0,
            'hit': 1,
            'critical hit': 2,
        },
    }


    tree = SelectionNode(
        selector=AttackRollNode(**{
            'critical_hit_range': [19,20],
            'critical_miss_range': [1],
            'attack_bonus': 4,
            'armor_class': ReferenceNode('target.AC'),
        }),
        results={
            'critical miss': RollNode('4d6'),
            'miss': 0,
            'hit': 1,
            'critical hit': 2,
        },
    )

    assert tree.to_dict() == {
        'node': 'Selection',
        'selector': {
            'node': 'AttackRoll',
            'critical_hit_range': [19,20],
            'critical_miss_range': [1],
            'attack_bonus': 4,
            'armor_class': {
                'node': 'Reference',
                'value': 'target.AC',
            },
        },
        'results': {
            'critical miss': {
                'node': 'Roll',
                'value': '4d6',
            },
            'miss': 0,
            'hit': 1,
            'critical hit': 2,
        },
    }

def test_node_roll():
    tree = RollNode('4d6')

    assert tree.to_dict() == {
        'node': 'Roll',
        'value': '4d6',
    }