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
    

    tree = dict_to_node({
        'node': 'And', 
        'values': [
            {'node': 'Damage', 'value': '1d6', 'type': 'slashing'},
            {
                'node': 'Condition', 
                'value': 'stunned', 
                'duration': {
                    'node': 'Duration',
                    'value': ['1 minute'],
                }
            },
        ]
    })
    assert type(tree) is AndNode
    assert type(tree.values[0]) is DamageNode
    assert type(tree.values[1]) is ConditionNode

    tree = dict_to_node({
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
            'armor_class': 12,
        },
        'results': {
            'critical miss': 0,
            'miss': 0,
            'hit': {'node': 'Damage', 'value': '1d6', 'type': 'slashing'},
            'critical hit': {'node': 'Damage', 'value': '2d6', 'type': 'slashing'},
        },
    })
    assert type(tree) is AttackNode
    assert type(tree.targeting) is TargetingNode
    assert type(tree.attack_roll) is AttackRollNode
    assert type(tree.results) is dict
    
    tree = dict_to_node({
        'node': 'AttackRoll',
        'critical_hit_range': [20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': {
            'node': 'Reference',
            'value': 'target.armor_class',
        },
    })
    assert type(tree) is AttackRollNode
    assert type(tree.armor_class) is ReferenceNode
    
    tree = dict_to_node({
        'node': 'Condition',
        'value': 'Stunned',
        'duration': {'node': 'Duration', 'value': ['1 minute']},
    })
    assert type(tree) is ConditionNode
    assert type(tree.duration) is DurationNode

    tree = dict_to_node({'node': 'Damage', 'value': '1d6', 'type': 'slashing'})
    assert type(tree) is DamageNode

    tree = dict_to_node({'node': 'Duration', 'value': ['1 minute']})
    assert type(tree) is DurationNode

    tree = dict_to_node({'node': 'Move', 'value': '15 feet'})
    assert type(tree) is MoveNode

    tree = dict_to_node({'node': 'Reference', 'value': 'target.AC'})
    assert type(tree) is ReferenceNode

    tree = dict_to_node({'node': 'Roll', 'value': '1d4 + 1'})
    assert type(tree) is RollNode

    tree = dict_to_node({
        'node': 'Save',
        'targeting': {
            'node': 'Targeting',
            'range': '5 feet',
            'area': None,
            'max_targets': 2,
            'min_targets': 0,
        },
        'save_roll': {
            'node': 'SaveRoll',
            'save_dc': 12,
            'save_bonus': 4,
        },
        'results': {
            'failure': {'node': 'Damage', 'value': '1d6', 'type': 'fire'},
            'success': 0.5,
        },
    })
    assert type(tree) is SaveNode
    assert type(tree.targeting) is TargetingNode
    assert type(tree.save_roll) is SaveRollNode
    assert type(tree.results) is dict
    
    tree = dict_to_node({'node': 'SaveRoll', 'save_dc': 13, 'save_bonus': 4})
    assert type(tree) is SaveRollNode

    tree = dict_to_node({
        'node': 'Targeting',
        'range': '60 feet',
        'area': {
            'shape': 'cylinder',
            'radius': '20 feet',
            'height': '40 feet',
        },
        'max_targets': 2,
        'min_targets': 0,
    })
    assert type(tree) is TargetingNode



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