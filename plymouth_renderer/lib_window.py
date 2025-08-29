"""
Implementation of the 'Window' global object.
"""
from .script_objects import Hash, Number, NativeFunction, Null

def window_get_width(interpreter, args):
    """Returns the width of the renderer's screen."""
    return Number(interpreter.renderer.screen.get_width())

def window_get_height(interpreter, args):
    """Returns the height of the renderer's screen."""
    return Number(interpreter.renderer.screen.get_height())

def window_get_x(interpreter, args):
    """Returns the x-coordinate of the window (always 0)."""
    return Number(0)

def window_get_y(interpreter, args):
    """Returns the y-coordinate of the window (always 0)."""
    return Number(0)

def window_set_background_top_color(interpreter, args):
    if len(args) != 3: raise TypeError("SetBackgroundTopColor expects 3 arguments (r, g, b).")
    color = tuple(int(arg.value * 255) for arg in args)
    interpreter.renderer.background_top_color = color
    return Null()

def window_set_background_bottom_color(interpreter, args):
    if len(args) != 3: raise TypeError("SetBackgroundBottomColor expects 3 arguments (r, g, b).")
    color = tuple(int(arg.value * 255) for arg in args)
    interpreter.renderer.background_bottom_color = color
    return Null()

def setup_window_library(interpreter, renderer):
    """Creates the 'Window' object and adds it to the interpreter's global scope."""
    if not hasattr(interpreter, 'renderer'):
        interpreter.renderer = renderer

    window_obj = Hash({
        "GetWidth": NativeFunction(window_get_width),
        "GetHeight": NativeFunction(window_get_height),
        "GetX": NativeFunction(window_get_x),
        "GetY": NativeFunction(window_get_y),
        "SetBackgroundTopColor": NativeFunction(window_set_background_top_color),
        "SetBackgroundBottomColor": NativeFunction(window_set_background_bottom_color),
    })
    interpreter.globals.define("Window", window_obj)

    return window_obj
