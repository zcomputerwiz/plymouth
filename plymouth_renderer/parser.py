"""
A manual recursive descent parser for the Plymouth scripting language.
"""
from .tokenizer import Tokenizer, Token
from . import ast

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.current_token = None
        self.advance()

    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None

    def error(self, message):
        raise Exception(f"Parse Error: {message} at {self.current_token}")

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f"Expected token {token_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def parse(self):
        statements = []
        while self.current_token:
            statements.append(self.statement())
        return ast.Program(statements)

    def statement(self):
        if self.current_token.type == 'FUN':
            return self.fun_declaration()
        elif self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'FOR':
            return self.for_statement()
        elif self.current_token.type == 'LBRACE':
            return self.block()
        else:
            expr = self.expression()
            self.eat('SEMI')
            return ast.ExpressionStatement(expr)

    def if_statement(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        then_branch = self.statement()
        else_branch = None
        if self.current_token and self.current_token.type == 'ELSE':
            self.advance()
            else_branch = self.statement()
        return ast.IfStatement(condition, then_branch, else_branch)

    def for_statement(self):
        self.eat('FOR')
        self.eat('LPAREN')
        initializer = self.expression(); self.eat('SEMI')
        condition = self.expression(); self.eat('SEMI')
        increment = self.expression()
        self.eat('RPAREN')
        body = self.statement()
        return ast.ForStatement(initializer, condition, increment, body)

    def block(self):
        self.eat('LBRACE')
        statements = []
        while self.current_token and self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        self.eat('RBRACE')
        return ast.Block(statements)

    def fun_declaration(self):
        self.eat('FUN')
        name = self.current_token.value; self.eat('ID')
        self.eat('LPAREN')
        params = []
        if self.current_token.type != 'RPAREN':
            params.append(self.current_token.value); self.eat('ID')
            while self.current_token.type == 'COMMA':
                self.advance()
                params.append(self.current_token.value); self.eat('ID')
        self.eat('RPAREN')
        body = self.block()
        return ast.FunctionDef(name, params, body)

    def expression(self): return self.assignment()
    def assignment(self):
        node = self.logic_or()
        if self.current_token and self.current_token.type.startswith('OP_ASSIGN'):
            op = self.current_token; self.advance()
            right = self.assignment()
            return ast.Assignment(node, op, right)
        return node
    def logic_or(self):
        node = self.logic_and()
        while self.current_token and self.current_token.type == 'OP_OR':
            op = self.current_token; self.advance()
            right = self.logic_and()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def logic_and(self):
        node = self.equality()
        while self.current_token and self.current_token.type == 'OP_AND':
            op = self.current_token; self.advance()
            right = self.equality()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def equality(self):
        node = self.comparison()
        while self.current_token and self.current_token.type in ('OP_EQ', 'OP_NE'):
            op = self.current_token; self.advance()
            right = self.comparison()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def comparison(self):
        node = self.term()
        while self.current_token and self.current_token.type in ('OP_GT', 'OP_GE', 'OP_LT', 'OP_LE'):
            op = self.current_token; self.advance()
            right = self.term()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.type in ('OP_PLUS', 'OP_MINUS'):
            op = self.current_token; self.advance()
            right = self.factor()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def factor(self):
        node = self.unary()
        while self.current_token and self.current_token.type in ('OP_MUL', 'OP_DIV'):
            op = self.current_token; self.advance()
            right = self.unary()
            node = ast.BinaryOp(left=node, op=op, right=right)
        return node
    def unary(self):
        if self.current_token and self.current_token.type in ('OP_NOT', 'OP_PLUS', 'OP_MINUS'):
            op = self.current_token; self.advance()
            operand = self.unary()
            return ast.UnaryOp(op, operand)
        return self.postfix()
    def postfix(self):
        node = self.call()
        if self.current_token and self.current_token.type in ('OP_INC', 'OP_DEC'):
            op = self.current_token; self.advance()
            return ast.PostOp(node, op)
        return node
    def call(self):
        node = self.primary()
        while self.current_token:
            if self.current_token.type == 'LPAREN':
                self.advance()
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.expression())
                    while self.current_token.type == 'COMMA':
                        self.advance()
                        args.append(self.expression())
                self.eat('RPAREN')
                node = ast.FunctionCall(node, args)
            elif self.current_token.type == 'DOT':
                self.advance()
                prop_name = self.current_token.value; self.eat('ID')
                node = ast.PropertyAccess(node, prop_name)
            elif self.current_token.type == 'LBRACK':
                self.advance()
                index_expr = self.expression()
                self.eat('RBRACK')
                node = ast.IndexAccess(node, index_expr)
            else:
                break
        return node
    def primary(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.advance(); return ast.Number(token.value)
        elif token.type == 'STRING':
            self.advance(); return ast.String(token.value)
        elif token.type == 'ID':
            self.advance(); return ast.Variable(token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        elif token.type == 'LOCAL':
            self.advance(); return ast.LocalNode()
        elif token.type == 'GLOBAL':
            self.advance(); return ast.GlobalNode()
        else:
            self.error(f"Unexpected token in primary expression: {token}")
