"""
Defines the runtime objects for the Plymouth scripting language interpreter.
"""

class ScriptObject:
    """Base class for all script objects."""
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class Number(ScriptObject):
    def __init__(self, value):
        self.value = float(value)

    def __repr__(self):
        return str(self.value)

class String(ScriptObject):
    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return f'"{self.value}"'

class Null(ScriptObject):
    def __init__(self):
        self.value = None

    def __repr__(self):
        return "NULL"

class Boolean(ScriptObject):
    def __init__(self, value):
        self.value = bool(value)

    def __repr__(self):
        return "true" if self.value else "false"

class Hash(ScriptObject):
    """Represents a script object, which is a hash of key-value pairs."""
    def __init__(self, members=None):
        self.members = members or {}

    def get(self, key):
        return self.members.get(key)

    def set(self, key, value):
        self.members[key] = value

    def __repr__(self):
        return f"Hash({list(self.members.keys())})"

class Environment(Hash):
    """Manages variable scopes for the interpreter."""
    def __init__(self, enclosing=None):
        super().__init__()
        self.enclosing = enclosing

    def define(self, name, value):
        self.set(name, value)

    def get(self, name_token):
        name = name_token if isinstance(name_token, str) else name_token.value
        if name in self.members:
            return self.members[name]
        if self.enclosing is not None:
            return self.enclosing.get(name_token)
        raise NameError(f"Undefined variable '{name}'.")

    def assign(self, name_token, value):
        name = name_token if isinstance(name_token, str) else name_token.value
        if name in self.members:
            self.set(name, value)
            return value
        if self.enclosing is not None:
            return self.enclosing.assign(name_token, value)
        raise NameError(f"Undefined variable '{name}'.")

class ListObject(ScriptObject):
    """Represents a list/array object."""
    def __init__(self, elements=None):
        self.elements = elements or []

    def get(self, index):
        if 0 <= index < len(self.elements):
            return self.elements[index]
        return Null() # Return Null if out of bounds, like plymouth seems to

    def set(self, index, value):
        # Pad with Null if index is out of bounds
        while index >= len(self.elements):
            self.elements.append(Null())
        self.elements[index] = value

    def __repr__(self):
        return f"List(len={len(self.elements)})"

class Function(ScriptObject):
    """Base class for functions."""
    pass

class NativeFunction(Function):
    """A function implemented in Python."""
    def __init__(self, python_callable):
        self.callable = python_callable

    def __call__(self, interpreter, args):
        return self.callable(interpreter, args)

    def __repr__(self):
        return f"<NativeFunction {self.callable.__name__}>"

class CallableObject(Hash, Function):
    """An object that is both a hash and a function."""
    def __init__(self, python_callable, members=None):
        Hash.__init__(self, members)
        Function.__init__(self)
        self.callable = python_callable

    def __call__(self, interpreter, args):
        return self.callable(interpreter, args)

    def __repr__(self):
        return f"<CallableObject {self.callable.__name__}>"

class ScriptFunction(Function):
    """A function defined in a plymouth script."""
    def __init__(self, name, params_node, body_node, closure):
        self.name = name
        self.params = params_node
        self.body = body_node
        self.closure = closure # The environment where the function was created

    def __repr__(self):
        return f"<ScriptFunction {self.name}>"
