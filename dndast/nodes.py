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
    value: any

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            'node': 'Value',
            'value': self.value,
        }