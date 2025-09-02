import re
import collections

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

class Tokenizer:
    """
    A lexical scanner that is more faithful to the C implementation.
    It tokenizes single-character symbols and leaves multi-character
    operator logic to the parser.
    """
    def __init__(self, code):
        self.code = code
        self.token_specification = [
            # Note: order is important for regex matching
            ('BLOCK_COMMENT', r'/\*.*?\*/'),
            ('COMMENT',       r'//.*|#.*'),
            ('NEWLINE',       r'\n'),
            ('WHITESPACE',    r'[ \t]+'),
            ('FLOAT',         r'\d+\.\d*'),
            ('INTEGER',       r'\d+'),
            ('STRING',        r'"(?:\\.|[^"\\])*"'),
            ('ID',            r'[A-Za-z_][A-Za-z0-9_]*'),
            ('SYMBOL',        r'[(){}\[\];,=.<>+\-*/%&|!~^]'), # All single-char symbols
            ('MISMATCH',      r'.'),
        ]
        self.keywords = {'if', 'else', 'while', 'for', 'do', 'fun', 'return', 'break', 'continue', 'NULL', 'true', 'false', 'this', 'global', 'local'}

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        line_num = 1
        line_start = 0
        # Use re.DOTALL to make '.' in block comments match newlines
        for mo in re.finditer(tok_regex, self.code, re.DOTALL):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind in ('COMMENT', 'BLOCK_COMMENT', 'WHITESPACE'):
                continue
            elif kind == 'STRING':
                # Unescape the string value, removing the surrounding quotes
                value = value[1:-1]
                value = re.sub(r'\\(.)', r'\1', value)
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character {value!r} on line {line_num}')

            if kind == 'ID' and value in self.keywords:
                kind = value.upper()

            yield Token(kind, value, line_num, column)
