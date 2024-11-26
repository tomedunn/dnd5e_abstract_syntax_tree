from .lexer import Lexer
from .parser_ import Parser
from .interpreter import Interpreter

class Dice_Roller:
    def __init__(self, eq_str):
        self.eq_str = eq_str
        self.tokens = Lexer(self.eq_str).generate_tokens()
        self.tree = Parser(self.tokens).parse()
        self.value = Interpreter().evaluate(self.tree)