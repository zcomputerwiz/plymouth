"""
The Renderer manages the PyGame window and the main drawing loop.
It is independent of the script execution.
"""
import pygame

class Renderer:
    def __init__(self, width=1024, height=768):
        self.interpreter = None # Will be set after initialization
        pygame.init()
        pygame.display.set_caption("Plymouth Renderer")
        self.screen = pygame.display.set_mode((width, height))
        self.sprites = []
        self.running = False
        self.clock = pygame.time.Clock()
        self.background_color = (0, 0, 0) # Default to black

    def add_sprite(self, sprite_obj):
        """Adds a sprite to the list of sprites to be rendered."""
        if sprite_obj not in self.sprites:
            self.sprites.append(sprite_obj)
            # Sort by z-index whenever a new sprite is added
            self.sprites.sort(key=lambda s: s.z)

    def remove_sprite(self, sprite_obj):
        """Removes a sprite from the render list."""
        if sprite_obj in self.sprites:
            self.sprites.remove(sprite_obj)

    def set_background_color(self, color_tuple):
        """Sets the background color of the screen."""
        self.background_color = color_tuple

    def run_in_thread(self):
        """Runs the rendering loop in a separate thread."""
        import threading
        render_thread = threading.Thread(target=self.run)
        render_thread.start()

    def run(self):
        """The main rendering loop."""
        self.running = True
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Run script refresh callback
            if self.interpreter:
                self.interpreter.tick()

            # Drawing
            self.screen.fill(self.background_color)

            # Draw all sprites in order of their z-index
            self.sprites.sort(key=lambda s: s.z) # Re-sort every frame in case z changes
            for sprite in self.sprites:
                if sprite.image_obj and sprite.image_obj.surface:
                    # Create a copy to avoid modifying the original surface's alpha
                    temp_surface = sprite.image_obj.surface.copy()
                    alpha = int(max(0, min(1, sprite.opacity)) * 255)
                    temp_surface.set_alpha(alpha)
                    self.screen.blit(temp_surface, (sprite.x, sprite.y))

            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(60) # 60 FPS

        pygame.quit()

    def stop(self):
        """Stops the rendering loop."""
        self.running = False
