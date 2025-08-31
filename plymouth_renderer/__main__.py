"""
The main entry point for the Plymouth Renderer application.
"""
import sys
import logging
from .tokenizer import Tokenizer
from .parser import Parser
from .interpreter import Interpreter
from .renderer import Renderer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Plymouth renderer."""
    logger.info("Starting Plymouth Renderer")

    test_mode = "--test" in sys.argv
    if test_mode:
        sys.argv.remove("--test")

    if len(sys.argv) < 2:
        print("Usage: python -m plymouth_renderer <path_to_script> [--test]")
        sys.exit(1)

    script_path = sys.argv[1]

    # 1. Create core components
    renderer = Renderer()
    interpreter = Interpreter(renderer)
    renderer.interpreter = interpreter # Complete the circular reference

    # 2. Read and parse the script
    logger.info(f"Loading script: {script_path}")
    try:
        with open(script_path, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        logger.error(f"Script file not found: {script_path}")
        sys.exit(1)

    tokens = list(Tokenizer(source).tokenize())
    parser = Parser(tokens)
    program_ast = parser.parse()

    # 3. Run the renderer and the interpreter
    if test_mode:
        import time
        logger.info("Running in test mode.")
        renderer.run_in_thread()
        interpreter.interpret(program_ast)
        logger.info("Script interpreted. Simulating boot events...")

        # Simulate some events
        if interpreter.boot_progress_callback:
            logger.info("Simulating boot progress...")
            for i in range(11):
                progress = i / 10.0
                interpreter.execute_function(interpreter.boot_progress_callback, [interpreter.script_objects.Number(0.1), interpreter.script_objects.Number(progress)])
                time.sleep(0.2)

        if interpreter.display_message_callback:
            logger.info("Simulating display message...")
            interpreter.execute_function(interpreter.display_message_callback, [interpreter.script_objects.String("Updating system...")])
            time.sleep(1)

        if interpreter.display_password_callback:
            logger.info("Simulating password prompt...")
            interpreter.execute_function(interpreter.display_password_callback, [interpreter.script_objects.String("Password: "), interpreter.script_objects.Number(3)])
            time.sleep(1)

        if interpreter.quit_callback:
            logger.info("Simulating quit...")
            interpreter.execute_function(interpreter.quit_callback, [])
            time.sleep(1)

        renderer.stop()
        logger.info("Test finished.")
    else:
        # In normal mode, the renderer runs in a thread, and the script
        # executes on the main thread. The program exits when the window is closed.
        renderer.run_in_thread()
        interpreter.interpret(program_ast)
        # The renderer thread will keep the application alive until the window is closed.

if __name__ == "__main__":
    main()
