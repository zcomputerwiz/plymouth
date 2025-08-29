"""
Implementation of the 'Plymouth' global object.
This object is used to control core renderer and system functions.
"""
from .script_objects import Hash, Number, NativeFunction, Null, Function

def plymouth_set_background_color(interpreter, args):
    """Sets the background color of the renderer's screen."""
    if len(args) != 3:
        raise TypeError("SetBackgroundColor requires 3 arguments (r, g, b).")

    # Values are expected to be 0-1 floats in the script
    r = int(args[0].value * 255)
    g = int(args[1].value * 255)
    b = int(args[2].value * 255)

    interpreter.renderer.set_background_color((r, g, b))
    return Null()

def plymouth_set_refresh_function(interpreter, args):
    """Sets a callback function to be called on every frame."""
    if len(args) != 1 or not isinstance(args[0], Function):
        raise TypeError("SetRefreshFunction expects one function argument.")
    interpreter.refresh_callback = args[0]
    return Null()

def plymouth_get_mode(interpreter, args):
    """Returns the current boot mode."""
    # We can hardcode this for the simulation
    return String("boot")

def plymouth_get_capslock_state(interpreter, args):
    """Returns the capslock state."""
    # We can hardcode this for the simulation
    return Number(0) # 0 for off

def plymouth_set_refresh_rate(interpreter, args):
    """Sets the refresh rate of the renderer."""
    if len(args) != 1 or not isinstance(args[0], Number):
        raise TypeError("SetRefreshRate expects one number argument.")
    interpreter.renderer.refresh_rate = args[0].value
    return Null()

def setup_plymouth_library(interpreter, renderer):
    """Creates the 'Plymouth' object and adds it to the interpreter's global scope."""

    # Attach the renderer to the interpreter instance so native functions can access it
    if not hasattr(interpreter, 'renderer'):
        interpreter.renderer = renderer

    def generic_callback_setter(callback_name):
        def setter(interpreter, args):
            if len(args) == 1 and isinstance(args[0], Function):
                setattr(interpreter, callback_name, args[0])
            else:
                raise TypeError(f"{callback_name} expects one function argument.")
            return Null()
        return NativeFunction(setter)

    plymouth_global_object = Hash({
        "SetBackgroundColor": NativeFunction(plymouth_set_background_color),
        "SetRefreshFunction": NativeFunction(plymouth_set_refresh_function),
        "SetRefreshRate": NativeFunction(plymouth_set_refresh_rate),
        "GetMode": NativeFunction(plymouth_get_mode),
        "GetCapslockState": NativeFunction(plymouth_get_capslock_state),
        "SetDisplayNormalFunction": generic_callback_setter("display_normal_callback"),
        "SetDisplayPasswordFunction": generic_callback_setter("display_password_callback"),
        "SetBootProgressFunction": generic_callback_setter("boot_progress_callback"),
        "SetQuitFunction": generic_callback_setter("quit_callback"),
        "SetDisplayMessageFunction": generic_callback_setter("display_message_callback"),
        "SetHideMessageFunction": generic_callback_setter("hide_message_callback"),
    })

    interpreter.globals.define("Plymouth", plymouth_global_object)

    return plymouth_global_object
