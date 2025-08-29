import re
import collections

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.token_specification = [
            ('COMMENT',    r'#.*'),
            ('NEWLINE',    r'\n'),
            ('WHITESPACE', r'[ \t]+'),
            ('NUMBER',     r'\d+(\.\d*)?'),
            ('STRING',     r'"[^"]*"'),
            ('ID',         r'[A-Za-z_][A-Za-z0-9_]*'),
            ('LPAREN',     r'\('),
            ('RPAREN',     r'\)'),
            ('LBRACE',     r'\{'),
            ('RBRACE',     r'\}'),
            ('LBRACK',     r'\['),
            ('RBRACK',     r'\]'),
            ('COMMA',      r','),
            ('SEMI',       r';'),
            ('DOT',        r'\.'),
            # Operators - order is important
            ('OP_OR',      r'\|\|'),
            ('OP_AND',     r'&&'),
            ('OP_EQ',      r'=='),
            ('OP_NE',      r'!='),
            ('OP_GE',      r'>='),
            ('OP_LE',      r'<='),
            ('OP_GT',      r'>'),
            ('OP_LT',      r'<'),
            ('OP_ASSIGN_EXTEND', r'\|='),
            ('OP_ASSIGN_PLUS',   r'\+='),
            ('OP_ASSIGN_MINUS',  r'-='),
            ('OP_ASSIGN_MUL',    r'\*='),
            ('OP_ASSIGN_DIV',    r'/='),
            ('OP_ASSIGN_MOD',    r'%='),
            ('OP_ASSIGN',  r'='),
            ('OP_EXTEND',  r'\|'),
            ('OP_INC',     r'\+\+'),
            ('OP_DEC',     r'--'),
            ('OP_PLUS',    r'\+'),
            ('OP_MINUS',   r'-'),
            ('OP_MUL',     r'\*'),
            ('OP_DIV',     r'/'),
            ('OP_MOD',     r'%'),
            ('OP_NOT',     r'!'),
            ('MISMATCH',   r'.'), # Any other character
        ]
        self.keywords = {'if', 'else', 'while', 'for', 'do', 'fun', 'return', 'break', 'continue', 'NULL', 'true', 'false', 'this', 'global', 'local'}

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind in ('COMMENT', 'WHITESPACE'):
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')

            if kind == 'ID' and value in self.keywords:
                kind = value.upper()

            yield Token(kind, value, line_num, column)
