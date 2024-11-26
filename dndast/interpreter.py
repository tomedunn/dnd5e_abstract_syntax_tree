from .nodes import *
from .dice_roller import Dice_Roller
from icepool import map, d, Die

class Interpreter:
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
    
    def evaluate_ValueNode(self, node, **kwargs):
        return node.value