"""
A manual recursive descent parser for the Plymouth scripting language.
This version is designed to work with a simplified token stream, where
multi-character operators are parsed by looking ahead.
"""
from .tokenizer import Token
from . import ast

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def error(self, message):
        raise Exception(f"Parse Error: {message} at {self.peek()}")

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return Token('EOF', '', -1, -1)
        return self.tokens[self.pos + offset]

    def advance(self, amount=1):
        self.pos += amount

    def consume(self, token_type=None, token_value=None):
        token = self.peek()
        if token_type and token.type != token_type:
            self.error(f"Expected token {token_type}, but got {token.type}")
        if token_value and token.value != token_value:
            self.error(f"Expected token value '{token_value}', but got '{token.value}'")
        self.advance()
        return token

    def match(self, token_type, token_value=None):
        if self.peek().type == token_type and (token_value is None or self.peek().value == token_value):
            return self.consume()
        return None

    def _match_and_consume_op(self, operators):
        for op in operators:
            if all(self.peek(i).value == char for i, char in enumerate(op)):
                first_token = self.peek()
                self.advance(len(op))
                return Token('OPERATOR', op, first_token.line, first_token.column)
        return None

    def parse(self):
        statements = []
        while self.peek().type != 'EOF':
            statements.append(self.statement())
        return ast.Program(statements)

    def statement(self):
        if self.match('FUN'):
            return self.fun_declaration()
        if self.match('IF'):
            return self.if_statement()
        if self.match('FOR'):
            return self.for_statement()
        if self.peek().type == 'SYMBOL' and self.peek().value == '{':
            return self.block()

        expr = self.expression()
        self.consume('SYMBOL', ';')
        return ast.ExpressionStatement(expr)

    def if_statement(self):
        self.consume('SYMBOL', '(')
        condition = self.expression()
        self.consume('SYMBOL', ')')
        then_branch = self.statement()
        else_branch = None
        if self.match('ELSE'):
            else_branch = self.statement()
        return ast.IfStatement(condition, then_branch, else_branch)

    def for_statement(self):
        self.consume('SYMBOL', '(')
        initializer = self.expression(); self.consume('SYMBOL', ';')
        condition = self.expression(); self.consume('SYMBOL', ';')
        increment = self.expression()
        self.consume('SYMBOL', ')')
        body = self.statement()
        return ast.ForStatement(initializer, condition, increment, body)

    def block(self):
        self.consume('SYMBOL', '{')
        statements = []
        while not (self.peek().type == 'SYMBOL' and self.peek().value == '}'):
            statements.append(self.statement())
        self.consume('SYMBOL', '}')
        return ast.Block(statements)

    def fun_declaration(self):
        name = self.consume('ID').value
        self.consume('SYMBOL', '(')
        params = []
        if not self.match('SYMBOL', ')'):
            params.append(self.consume('ID').value)
            while self.match('SYMBOL', ','):
                params.append(self.consume('ID').value)
            self.consume('SYMBOL', ')')
        body = self.block()
        return ast.FunctionDef(name, params, body)

    def expression(self): return self.assignment()

    def assignment(self):
        node = self.logic_or()
        op_token = self._match_and_consume_op(['=', '+=', '-=', '*=', '/=', '%='])
        if op_token:
            right = self.assignment()
            return ast.Assignment(node, op_token, right)
        return node

    def logic_or(self):
        node = self.logic_and()
        while (op_token := self._match_and_consume_op(['||'])):
            right = self.logic_and()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def logic_and(self):
        node = self.equality()
        while (op_token := self._match_and_consume_op(['&&'])):
            right = self.equality()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def equality(self):
        node = self.comparison()
        while (op_token := self._match_and_consume_op(['==', '!='])):
            right = self.comparison()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def comparison(self):
        node = self.term()
        while (op_token := self._match_and_consume_op(['>=', '<=', '>', '<'])):
            right = self.term()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def term(self):
        node = self.factor()
        while (op_token := self._match_and_consume_op(['+', '-'])):
            right = self.factor()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def factor(self):
        node = self.unary()
        while (op_token := self._match_and_consume_op(['*', '/', '%'])):
            right = self.unary()
            node = ast.BinaryOp(left=node, op=op_token, right=right)
        return node

    def unary(self):
        op_token = self._match_and_consume_op(['!', '+', '-'])
        if op_token:
            operand = self.unary()
            return ast.UnaryOp(op_token, operand)
        return self.postfix()

    def postfix(self):
        node = self.call()
        op_token = self._match_and_consume_op(['++', '--'])
        if op_token:
            return ast.PostOp(node, op_token)
        return node

    def call(self):
        node = self.primary()
        while True:
            if self.match('SYMBOL', '('):
                args = []
                if not (self.peek().type == 'SYMBOL' and self.peek().value == ')'):
                    args.append(self.expression())
                    while self.match('SYMBOL', ','):
                        args.append(self.expression())
                self.consume('SYMBOL', ')')
                node = ast.FunctionCall(node, args)
            elif self.match('SYMBOL', '.'):
                prop_name = self.consume('ID').value
                node = ast.PropertyAccess(node, prop_name)
            elif self.match('SYMBOL', '['):
                index_expr = self.expression()
                self.consume('SYMBOL', ']')
                node = ast.IndexAccess(node, index_expr)
            else:
                break
        return node

    def primary(self):
        if self.peek().type == 'INTEGER' or self.peek().type == 'FLOAT':
            return ast.Number(self.consume().value)
        elif self.peek().type == 'STRING':
            return ast.String(self.consume().value)
        elif self.peek().type == 'ID':
            return ast.Variable(self.consume().value)
        elif self.match('SYMBOL', '('):
            node = self.expression()
            self.consume('SYMBOL', ')')
            return node
        elif self.match('LOCAL'):
            return ast.LocalNode()
        elif self.match('GLOBAL'):
            return ast.GlobalNode()
        elif self.match('NULL'):
            return ast.Null()
        elif self.match('TRUE'):
            return ast.Boolean(True)
        elif self.match('FALSE'):
            return ast.Boolean(False)
        else:
            self.error(f"Unexpected token in primary expression: {self.peek()}")
