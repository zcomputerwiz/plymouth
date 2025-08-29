"""
Implementation of the 'Sprite' global object and Sprite instances.
"""
from .script_objects import Hash, Number, NativeFunction, Null
from .lib_image import ImageObject

class SpriteObject(Hash):
    """A script object representing a sprite on the screen."""
    def __init__(self, image_obj, renderer):
        super().__init__()
        if image_obj and not isinstance(image_obj, ImageObject):
            raise TypeError("SpriteObject must be initialized with an ImageObject or None.")

        self.image_obj = image_obj

        self.x = 0
        self.y = 0
        self.z = 0
        self.opacity = 1.0

        self.set("x", Number(self.x))
        self.set("y", Number(self.y))
        self.set("z", Number(self.z))
        self.set("opacity", Number(self.opacity))

        self.set("SetX", NativeFunction(self.set_x))
        self.set("SetY", NativeFunction(self.set_y))
        self.set("SetZ", NativeFunction(self.set_z))
        self.set("SetOpacity", NativeFunction(self.set_opacity))
        self.set("SetPosition", NativeFunction(self.set_position))
        self.set("SetImage", NativeFunction(self.set_image))

        renderer.add_sprite(self)

    def __repr__(self):
        return f"<Sprite z={self.z} @ ({self.x},{self.y}) opacity={self.opacity}>"

    # --- Native Methods for Sprite instances ---

    def set_x(self, interpreter, args):
        if len(args) == 1 and isinstance(args[0], Number):
            self.x = args[0].value
            self.set("x", args[0])
        else:
            raise TypeError("SetX expects one number argument.")
        return Null()

    def set_y(self, interpreter, args):
        if len(args) == 1 and isinstance(args[0], Number):
            self.y = args[0].value
            self.set("y", args[0])
        else:
            raise TypeError("SetY expects one number argument.")
        return Null()

    def set_z(self, interpreter, args):
        if len(args) == 1 and isinstance(args[0], Number):
            self.z = args[0].value
            self.set("z", args[0])
        else:
            raise TypeError("SetZ expects one number argument.")
        return Null()

    def set_opacity(self, interpreter, args):
        if len(args) == 1 and isinstance(args[0], Number):
            self.opacity = args[0].value
            self.set("opacity", args[0])
        else:
            raise TypeError("SetOpacity expects one number argument.")
        return Null()

    def set_position(self, interpreter, args):
        if len(args) == 3 and all(isinstance(arg, Number) for arg in args):
            self.x = args[0].value
            self.y = args[1].value
            self.z = args[2].value
            self.set("x", args[0])
            self.set("y", args[1])
            self.set("z", args[2])
        else:
            raise TypeError("SetPosition expects three number arguments (x, y, z).")
        return Null()

    def set_image(self, interpreter, args):
        if len(args) == 1 and isinstance(args[0], ImageObject):
            self.image_obj = args[0]
        else:
            raise TypeError("SetImage expects one Image argument.")
        return Null()

# --- "Static" Methods on the global Sprite object ---

def sprite_new(interpreter, args):
    """The constructor for creating new sprites. Corresponds to Sprite.New()."""
    if not hasattr(interpreter, 'renderer'):
        raise Exception("Interpreter is not connected to a renderer.")

    image_obj = None
    if len(args) == 1:
        if not isinstance(args[0], ImageObject):
            raise TypeError("Sprite.New expects an Image argument.")
        image_obj = args[0]
    elif len(args) > 1:
        raise TypeError("Sprite.New expects at most one argument.")

    return SpriteObject(image_obj, interpreter.renderer)

# --- Library Setup ---

def setup_sprite_library(interpreter, renderer):
    """Creates the 'Sprite' object and adds it to the interpreter's global scope."""

    # Attach renderer to interpreter so native functions can access it
    interpreter.renderer = renderer

    sprite_global_object = Hash({
        "New": NativeFunction(sprite_new)
    })

    interpreter.globals.define("Sprite", sprite_global_object)

    return sprite_global_object
