"""
Implementation of the 'Image' global object for the Plymouth scripting language.
"""
import logging
import pygame
from .script_objects import Hash, Number, String, NativeFunction, Null, CallableObject

logger = logging.getLogger(__name__)

class ImageObject(Hash):
    """A script object that represents an image, holding a pygame.Surface."""
    def __init__(self, surface):
        super().__init__()
        if not isinstance(surface, pygame.Surface):
            raise TypeError("ImageObject must be initialized with a pygame.Surface.")
        self.surface = surface

        self.set("GetWidth", NativeFunction(self.get_width))
        self.set("GetHeight", NativeFunction(self.get_height))
        self.set("Scale", NativeFunction(self.scale))
        self.set("Crop", NativeFunction(self.crop))
        self.set("Rotate", NativeFunction(self.rotate))
        self.set("Tile", NativeFunction(self.tile))

    def __repr__(self):
        return f"<Image {self.surface.get_width()}x{self.surface.get_height()}>"

    def get_width(self, interpreter, args):
        if args: raise TypeError("GetWidth() takes no arguments.")
        return Number(self.surface.get_width())

    def get_height(self, interpreter, args):
        if args: raise TypeError("GetHeight() takes no arguments.")
        return Number(self.surface.get_height())

    def scale(self, interpreter, args):
        if len(args) != 2 or not all(isinstance(arg, Number) for arg in args):
            raise TypeError("Scale() expects two number arguments (width, height).")
        width, height = int(args[0].value), int(args[1].value)
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

class ImageFactory:
    def __init__(self, image_dir):
        self.image_dir = image_dir

    def new(self, interpreter, args):
        if len(args) != 1 or not isinstance(args[0], String):
            raise TypeError("Image() expects one string argument (the path).")

        path = args[0].value
        if path.startswith("special://"):
            logger.warning(f"Special image path '{path}' not implemented, creating dummy surface.")
            surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            return ImageObject(surface)

        full_path = f"{self.image_dir}/{path}"
        try:
            pygame.font.init()
            surface = pygame.image.load(full_path).convert_alpha()
            logger.info(f"Successfully loaded image: '{full_path}'")
            return ImageObject(surface)
        except (pygame.error, FileNotFoundError) as e:
            logger.warning(f"Could not load image '{full_path}', creating dummy surface. Error: {e}")
            surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            return ImageObject(surface)

def image_text(interpreter, args):
    if len(args) < 4: raise TypeError("Image.Text expects at least 4 arguments (text, r, g, b).")
    text = args[0].value if isinstance(args[0], String) else str(args[0].value)
    r, g, b = [int(arg.value * 255) for arg in args[1:4]]
    alpha = int(args[4].value * 255) if len(args) > 4 and isinstance(args[4], Number) else 255
    font_path = args[5].value if len(args) > 5 and isinstance(args[5], String) else None

    try:
        font = pygame.font.Font(font_path, 24)
    except (IOError, pygame.error):
        font = pygame.font.Font(None, 24)

    text_surface = font.render(text, True, (r, g, b))
    text_surface.set_alpha(alpha)
    return ImageObject(text_surface)

def setup_image_library(interpreter, image_dir):
    factory = ImageFactory(image_dir)

    image_global_object = CallableObject(
        python_callable=factory.new,
        members={
            "New": NativeFunction(factory.new),
            "Text": NativeFunction(image_text)
        }
    )

    interpreter.globals.define("Image", image_global_object)
    return image_global_object
