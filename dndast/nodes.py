from dataclasses import dataclass
import sys


def dict_to_node(node_dict):
    """Converts an abstract syntax tree in dictionary form into a node base representation.
    """
    if not node_dict:
        return EmptyNode()
    
    else:
        class_name = node_dict.pop('node')
        new_node = getattr(sys.modules[__name__], f'{class_name}Node')

        for k, v in node_dict.items():
            if type(v) == dict:
                node_dict[k] = dict_to_node(v)
        
        return new_node(**node_dict)


@dataclass
class AttackRollNode:
    """
    type = roll
    Specifies an attack roll. The roll provides four possible outcomes based on
        critical_hit_range: (list) The d20 roll values that count as a critical hit.
        critical_miss_range: (list) The d20 roll values that count as a critical miss.
        attack_bonus: (int, roll) The attacker's attack bonus.
        armor_class: (int, ref) The target's armor class.
    
    Possible outputs are:
        'critical miss': d20 in critical_miss_range
        'miss': d20 + attack_bonus >= armor_class
        'hit':  d20 + attack_bonus <  armor_class
        'critical hit': d20 in critical_hit_range
    
    Example:
        {
            'node': 'AttackRoll',
            'critical_hit_range': [19,20],
            'critical_miss_range': [1],
            'attack_bonus': 4,
            'armor_class': 10,
        }
    """
    critical_hit_range: list
    critical_miss_range: list
    attack_bonus: any
    armor_class: any

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'AttackRoll',
            'critical_hit_range': self.critical_hit_range,
            'critical_miss_range': self.critical_miss_range,
            'attack_bonus': self.attack_bonus,
            'armor_class': self.armor_class,
        }


@dataclass
class DamageNode:
    equation: str
    type: str

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Damage',
            'equation': self.equation,
            'type': self.type
        }


@dataclass
class EmptyNode:

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Empty',
        }


@dataclass
class ReferenceNode:
    """
    type = value
    Used to reference specific stats from a target.
    {
        'node': 'Reference',
        'value': 'target.AC',
    }
    """
    value: str

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Reference',
            'value': self.value,
        }


@dataclass
class RollNode:
    """
    type = roll
    Used to define a roll
        value: (str) dice equation or (dict) of values and counts

    Examples:
    As a string dice equation,
        {
            'node': 'Roll',
            'value': '1d4 + 1',
        }
    or as a dictionary of values and counts,
        {
            'node': 'Roll',
            'value': {2: 1, 3: 1, 4: 1, 5: 1}, # 1d4 + 1 in dictionary form
        }
    """
    value: any

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Roll',
            'value': self.value,
        }


@dataclass
class SaveRollNode:
    """
    type = roll
    Specifies a saving throw. The roll provides two possible outcomes based on
        save_dc: (int) The difficulty class of the saving throw.
        save_bonus: (int, roll, ref) The saving throw bonus of the target.
    
    Possible outputs are:
        'success': d20 + save_bonus >= save_dc
        'failure': d20 + save_bonus <  save_dc
    
    Example:
        {
            'node': 'SaveRoll',
            'save_dc': 13,
            'save_bonus': 4,
        }
    """
    save_dc: any
    save_bonus: any

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'SaveRoll',
            'save_dc': self.save_dc,
            'save_bonus': self.save_bonus,
        }


@dataclass
class SelectionNode:
    """
    type = control
    Applies a roll to a dictionary of results.
        selector: (roll) The roll used to determine the probability of each result.
        results: (dict) A dictionary of values associated with each outcome of the selector.
    
    Example:
        {
            'node': 'Selection',
            'selector': {
                'node': 'AttackRoll',
                'critical_hit_range': [19,20],
                'critical_miss_range': [1],
                'attack_bonus': 4,
                'armor_class': 10,
            },
            'result': {
                'critical miss': 0,
                'miss': 0,
                'hit': 1,
                'critical hit': 2,
            },
        }
    """
    selector: any
    results: dict

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Selection',
            'selector': self.selector.to_dict(),
            'results': self.results,
        }


@dataclass
class ValueNode:
    """
    type = value
    Defines a value to be returned.
        value: (anything not a node) The value to be returned.
    
    Example:
        {
            'node': 'Value',
            'value': 1,
        }
    """
    value: any

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Value',
            'value': self.value,
        }