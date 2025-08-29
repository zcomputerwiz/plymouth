"""
Implementation of the 'Math' global object for the Plymouth scripting language.
"""
import math
from .script_objects import Hash, Number, NativeFunction, Boolean

def native_function(func):
    """A decorator to simplify creating NativeFunction objects."""
    def wrapper(interpreter, args):
        # This is where we could add argument type/count checking
        return func(*[arg.value for arg in args])
    return NativeFunction(wrapper)

# --- Math Library Functions ---

@native_function
def math_cos(value):
    return Number(math.cos(value))

@native_function
def math_sin(value):
    return Number(math.sin(value))

@native_function
def math_tan(value):
    return Number(math.tan(value))

@native_function
def math_atan2(y, x):
    return Number(math.atan2(y, x))

@native_function
def math_sqrt(value):
    return Number(math.sqrt(value))

@native_function
def math_abs(value):
    return Number(abs(value))

@native_function
def math_min(a, b):
    return Number(min(a, b))

@native_function
def math_max(a, b):
    return Number(max(a, b))

@native_function
def math_int(value):
    return Number(int(value))

@native_function
def math_random():
    return Number(math.random())

# --- Library Setup ---

def setup_math_library(interpreter):
    """Creates the 'Math' object and adds it to the interpreter's global scope."""
    math_obj = Hash({
        "Cos": math_cos,
        "Sin": math_sin,
        "Tan": math_tan,
        "ATan2": math_atan2,
        "Sqrt": math_sqrt,
        "Abs": math_abs,
        "Min": math_min,
        "Max": math_max,
        "Int": math_int,
        "Random": math_random,
        "Pi": Number(math.pi)
    })

    interpreter.globals.define("Math", math_obj)

    # Also define the legacy global functions for compatibility
    interpreter.globals.define("MathCos", math_cos)
    interpreter.globals.define("MathSin", math_sin)
    # ... and so on for others if needed.

    return math_obj
