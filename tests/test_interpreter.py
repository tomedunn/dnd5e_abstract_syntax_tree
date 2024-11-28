import pytest
from icepool import d, Die
from dndast.nodes import *
from dndast.interpreter import *

TARGETS = {
    'maxtargets': 5,
    'melee_maxtargets': 2,
    'melee_target': {
        'armor_class': 18,
        'strength_save_bonus': 1,
        'dexterity_save_bonus': 0,
        'constitution_save_bonus': 2,
        'intelligence_save_bonus': 1,
        'wisdom_save_bonus': 2,
        'charisma_save_bonus': 2,
    },
    'ranged_targetarea': 10**2,
    'ranged_maxtargets': 4,
    'ranged_target': {
        'armor_class': 12,
        'strength_save_bonus': 1,
        'dexterity_save_bonus': 0,
        'constitution_save_bonus': 2,
        'intelligence_save_bonus': 1,
        'wisdom_save_bonus': 2,
        'charisma_save_bonus': 2,
    },
}

def test_interpreter_attackroll():
    tree = AttackRollNode(**{
        'critical_hit_range': [19,20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': ReferenceNode('target.AC'),
    })
    target = {
        'AC': 10,
    }
    interpreter = Interpreter(targets=TARGETS)
    result = interpreter.evaluate(tree, target=target)
    die = Die({'critical hit': 2, 'critical miss': 1, 'hit': 13, 'miss': 4})
    assert result == die


def test_interpreter_reference():
    tree = ReferenceNode('target.AC')
    target = {
        'AC': 10,
    }
    interpreter = Interpreter(targets=TARGETS)
    assert 10 == interpreter.evaluate(tree, target=target)


def test_interpreter_roll():
    interpreter = Interpreter(targets=TARGETS)
    tree = RollNode('d20')
    result = interpreter.evaluate(tree)
    assert result.mean() == 10.5

    tree = RollNode({1: 1, 2: 1, 3: 1, 4: 1})
    result = interpreter.evaluate(tree)
    assert result.mean() == 2.5


def test_interpreter_saveroll():
    tree = SaveRollNode(**{
        'save_dc': 12,
        'save_bonus': ReferenceNode('target.dexterity_save_bonus'),
    })
    target = {
        'dexterity_save_bonus': 4,
    }
    interpreter = Interpreter(targets=TARGETS)
    result = interpreter.evaluate(tree, target=target)
    die = Die({'failure': 7, 'success': 13})
    assert result == die


def test_interpreter_selection():
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
    target = {
        'AC': 10,
    }
    interpreter = Interpreter(targets=TARGETS)
    result = interpreter.evaluate(tree, target=target)
    die = Die({0: 5, 1: 13, 2: 2})
    assert result == die


def test_interpreter_targeting():
    tree = TargetingNode(**{
        'range': '60 feet',
        'area': {
            'shape': 'cylinder',
            'radius': '20 feet',
            'height': '40 feet',
        },
        'max_targets': 2,
        'min_targets': 0,
    })
    interpreter = Interpreter(targets=TARGETS)
    assert 2 == len(interpreter.evaluate(tree))
    assert interpreter.evaluate(tree) == [
        {
            'armor_class': 12,
            'strength_save_bonus': 1,
            'dexterity_save_bonus': 0,
            'constitution_save_bonus': 2,
            'intelligence_save_bonus': 1,
            'wisdom_save_bonus': 2,
            'charisma_save_bonus': 2,
        },
        {
            'armor_class': 12,
            'strength_save_bonus': 1,
            'dexterity_save_bonus': 0,
            'constitution_save_bonus': 2,
            'intelligence_save_bonus': 1,
            'wisdom_save_bonus': 2,
            'charisma_save_bonus': 2,
        },
    ]

    tree = TargetingNode(**{
        'range': '5 feet',
        'area': None,
        'max_targets': 1,
        'min_targets': 0,
    })
    interpreter = Interpreter(targets=TARGETS)
    assert 1 == len(interpreter.evaluate(tree))
    assert interpreter.evaluate(tree) == [
        {
            'armor_class': 18,
            'strength_save_bonus': 1,
            'dexterity_save_bonus': 0,
            'constitution_save_bonus': 2,
            'intelligence_save_bonus': 1,
            'wisdom_save_bonus': 2,
            'charisma_save_bonus': 2,
        },
    ]


def test_interpreter_value():
    interpreter = Interpreter(targets=TARGETS)

    assert 'string' == interpreter.evaluate(ValueNode('string'))
    assert 10 == interpreter.evaluate(ValueNode(10))
    assert [1,2,3] == interpreter.evaluate(ValueNode([1,2,3]))