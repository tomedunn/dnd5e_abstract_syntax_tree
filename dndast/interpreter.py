from .nodes import *
from .dice_roller import Dice_Roller
from icepool import map, d, Die
import math

class Interpreter:
    def __init__(self, targets={}):
        self.targets = targets

    def evaluate(self, node, **kwargs):
        if type(node) in [str,int,float,list]:
            return node
        if node == None: return None
        method_name = f'evaluate_{type(node).__name__}'
        method = getattr(self, method_name)
        result = method(node, **kwargs)
        return result
    
    def evaluate_AndNode(self, node, **kwargs):
        result_a = self.evaluate(node.node_a, **kwargs)
        result_b = self.evaluate(node.node_b, **kwargs)
        return [a + b for a in result_a for b in result_b]
    
    def evaluate_AttackRollNode(self, node, **kwargs):
        def attack_outcomes(d20, chr, cmr, ab, ac):
            if d20 in chr:
                return 'critical hit'
            elif d20 in cmr:
                return 'critical miss'
            elif d20 + ab >= ac:
                return 'hit'
            else:
                return 'miss'
        
        outcomes = map(attack_outcomes, d(20), 
                       self.evaluate(node.critical_hit_range, **kwargs),
                       self.evaluate(node.critical_miss_range, **kwargs),
                       self.evaluate(node.attack_bonus, **kwargs),
                       self.evaluate(node.armor_class, **kwargs))
        return outcomes
    
    def evaluate_ReferenceNode(self, node, **kwargs):
        target, stat = node.value.split('.')
        target = kwargs.get(target, None)
        if target:
            return target.get(stat, None)
        else:
            return None
    
    def evaluate_RollNode(self, node):
        if type(node.value) is str:
            return Dice_Roller(node.value).value
        elif type(node.value) is dict:
            return Die(node.value)
    
    def evaluate_SaveRollNode(self, node, **kwargs):
        def save_outcomes(d20, dc, sb):
            if d20 + sb >= dc:
                return 'success'
            else:
                return 'failure'
        
        # evaluate outcomes
        outcomes = map(save_outcomes, d(20), 
                       self.evaluate(node.save_dc, **kwargs),
                       self.evaluate(node.save_bonus, **kwargs))
        return outcomes
    
    def evaluate_SelectionNode(self, node, **kwargs):
        def apply_results(outcome, results):
            return results[outcome]
        
        outcomes = self.evaluate(node.selector, **kwargs)
        results = {k: self.evaluate(v) for k, v in node.results.items()}
        return map(apply_results, outcomes, results)
    
    def evaluate_TargetingNode(self, node, **kwargs):
        def feet(s):
            return int(s.split(' ')[0])
        
        def calc_area(area):
            match area['shape']:
                case 'cone':
                    return 0.5*feet(area['length'])**2
                case 'cube':
                    return feet(area['length'])**2
                case 'cylinder':
                    return math.pi*feet(area['radius'])**2
                case 'emanation':
                    return math.pi*feet(area['radius'])**2
                case 'line':
                    return feet(area['length'])*feet(area['width'])
                case 'sphere':
                    return math.pi*feet(area['radius'])**2
                case _:
                    return None # should be an error ... probably
            
        r = feet(node.range)
        mr = 'melee' if r < 10 else 'ranged'

        # determine the number of melee and ranged targets
        if not node.area:
            n = min(node.max_targets, self.targets[f'{mr}_maxtargets'])
            targets = n*[self.targets[f'{mr}_target'].copy()]
            return targets
        else:
            area = calc_area(node.area)
            n = min(node.max_targets, self.targets[f'{mr}_maxtargets'], int(area/self.targets[f'{mr}_targetarea']))
            targets = n*[self.targets[f'{mr}_target'].copy()]
            return targets
    
    def evaluate_ValueNode(self, node, **kwargs):
        return node.value