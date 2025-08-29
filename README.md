# Plymouth Renderer

This project is a cross-platform Python interpreter and renderer for Plymouth boot splash scripts. It allows for debugging and visualization of Plymouth themes without needing a local Plymouth installation.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2.  Navigate to the project directory:
    ```bash
    cd plymouth-renderer
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the renderer, execute the `plymouth_renderer` module and provide the path to a Plymouth script file:

```bash
python -m plymouth_renderer sample.script
```

This will open a window and display the boot splash animation as defined in the script.
