"""
Implementation of the 'Image' global object for the Plymouth scripting language.
"""
import pygame
from .script_objects import Hash, Number, String, NativeFunction, Null

class ImageObject(Hash):
    """A script object that represents an image, holding a pygame.Surface."""
    def __init__(self, surface):
        super().__init__()
        if not isinstance(surface, pygame.Surface):
            raise TypeError("ImageObject must be initialized with a pygame.Surface.")
        self.surface = surface

        # Populate the object with methods
        self.set("GetWidth", NativeFunction(self.get_width))
        self.set("GetHeight", NativeFunction(self.get_height))
        self.set("Scale", NativeFunction(self.scale))
        self.set("Crop", NativeFunction(self.crop))
        self.set("Rotate", NativeFunction(self.rotate))
        self.set("Tile", NativeFunction(self.tile))

    def __repr__(self):
        return f"<Image {self.surface.get_width()}x{self.surface.get_height()}>"

    # --- Native Methods for Image instances ---

    def get_width(self, interpreter, args):
        if args:
            raise TypeError("GetWidth() takes no arguments.")
        return Number(self.surface.get_width())

    def get_height(self, interpreter, args):
        if args:
            raise TypeError("GetHeight() takes no arguments.")
        return Number(self.surface.get_height())

    def scale(self, interpreter, args):
        if len(args) != 2 or not isinstance(args[0], Number) or not isinstance(args[1], Number):
            raise TypeError("Scale() expects two number arguments (width, height).")
        width = int(args[0].value)
        height = int(args[1].value)
        scaled_surface = pygame.transform.scale(self.surface, (width, height))
        return ImageObject(scaled_surface)

    def crop(self, interpreter, args):
        if len(args) != 4 or not all(isinstance(arg, Number) for arg in args):
            raise TypeError("Crop() expects four number arguments (x, y, width, height).")
        x, y, width, height = [int(arg.value) for arg in args]

        cropped_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        cropped_surface.blit(self.surface, (0, 0), (x, y, width, height))
        return ImageObject(cropped_surface)

    def rotate(self, interpreter, args):
        if len(args) != 1 or not isinstance(args[0], Number):
            raise TypeError("Rotate() expects one number argument (angle in degrees).")
        angle = args[0].value
        rotated_surface = pygame.transform.rotate(self.surface, angle)
        return ImageObject(rotated_surface)

    def tile(self, interpreter, args):
        if len(args) != 2 or not isinstance(args[0], Number) or not isinstance(args[1], Number):
            raise TypeError("Tile() expects two number arguments (width, height).")
        width, height = int(args[0].value), int(args[1].value)

        tiled_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        for x in range(0, width, self.surface.get_width()):
            for y in range(0, height, self.surface.get_height()):
                tiled_surface.blit(self.surface, (x, y))
        return ImageObject(tiled_surface)

# --- "Static" Methods on the global Image object ---

def image_new(interpreter, args):
    """The constructor for creating new images. Corresponds to Image.New()."""
    if len(args) != 1 or not isinstance(args[0], String):
        raise TypeError("Image.New() expects one string argument (the path).")

    path = args[0].value
    if path == "special://logo":
        # Use a default placeholder for the logo if not found
        try:
            surface = pygame.image.load("themes/spinfinity/animation-0001.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            surface = pygame.Surface((100, 100))
            surface.fill((0, 255, 0)) # Green placeholder
        return ImageObject(surface)

    try:
        # Assuming a basic font for Image.Text later
        pygame.font.init()
        surface = pygame.image.load(path).convert_alpha()
        return ImageObject(surface)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Runtime Warning: Could not load image '{path}': {e}")
        return Null()

def image_text(interpreter, args):
    """Renders text to a new image surface."""
    # text, r, g, b, [alpha=1], [font=None], [align="left"]
    if len(args) < 4:
        raise TypeError("Image.Text expects at least 4 arguments (text, r, g, b).")

    text = args[0].value if isinstance(args[0], String) else str(args[0].value)
    r = int(args[1].value * 255)
    g = int(args[2].value * 255)
    b = int(args[3].value * 255)

    alpha = 255
    if len(args) > 4 and isinstance(args[4], Number):
        alpha = int(args[4].value * 255)

    font_path = None
    if len(args) > 5 and isinstance(args[5], String):
        font_path = args[5].value # TODO: Handle font lookup/paths correctly

    # TODO: Handle alignment argument

    try:
        # A default font in case the user-provided one fails or is None
        font = pygame.font.Font(font_path, 24) # Default size 24
    except (IOError, pygame.error):
        print(f"Warning: Could not load font '{font_path}', using default.")
        font = pygame.font.Font(None, 24)

    color = (r, g, b)

    # Render with alpha. Pygame's font render doesn't directly support an alpha channel
    # in the color tuple. We create a surface with alpha and then set it.
    text_surface = font.render(text, True, color)
    text_surface.set_alpha(alpha)

    return ImageObject(text_surface)


# --- Library Setup ---

class ImageFactory:
    def __init__(self, image_dir):
        self.image_dir = image_dir

    def new(self, interpreter, args):
        if len(args) != 1 or not isinstance(args[0], String):
            raise TypeError("Image.New() expects one string argument (the path).")

        path = args[0].value
        if path == "special://logo":
            try:
                surface = pygame.image.load("themes/spinfinity/animation-0001.png").convert_alpha()
            except (pygame.error, FileNotFoundError):
                surface = pygame.Surface((100, 100)); surface.fill((0, 255, 0))
            return ImageObject(surface)

        full_path = f"{self.image_dir}/{path}"
        try:
            pygame.font.init()
            surface = pygame.image.load(full_path).convert_alpha()
            return ImageObject(surface)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Runtime Warning: Could not load image '{full_path}': {e}")
            return Null()

def setup_image_library(interpreter, image_dir):
    """Creates the 'Image' object and adds it to the interpreter's global scope."""
    factory = ImageFactory(image_dir)

    image_global_object = Hash({
        "New": NativeFunction(factory.new),
        "Text": NativeFunction(image_text) # image_text is still a static function
    })

    interpreter.globals.define("Image", image_global_object)

    return image_global_object
