"""
Defines the Abstract Syntax Tree (AST) node classes for the Plymouth scripting language.
These nodes are the output of the parser.
"""

class Node:
    """Base class for all AST nodes."""
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class ExpressionStatement(Node):
    def __init__(self, expression):
        self.expression = expression

class Block(Node):
    def __init__(self, statements):
        self.statements = statements

class Assignment(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, right):
        self.op = op
        self.right = right

class PostOp(Node):
    def __init__(self, left, op):
        self.left = left
        self.op = op

class Number(Node):
    def __init__(self, value):
        self.value = float(value)

class String(Node):
    def __init__(self, value):
        self.value = value[1:-1] # Strip quotes

class Variable(Node):
    def __init__(self, name):
        self.name = name

class FunctionCall(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class FunctionDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class IfStatement(Node):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class ForStatement(Node):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

class PropertyAccess(Node):
    def __init__(self, obj, property_name):
        self.obj = obj
        self.property_name = property_name

class IndexAccess(Node):
    def __init__(self, obj, index_expr):
        self.obj = obj
        self.index = index_expr

class ReturnStatement(Node):
    def __init__(self, value):
        self.value = value

class Null(Node):
    pass

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class GlobalNode(Node):
    pass

class LocalNode(Node):
    pass
