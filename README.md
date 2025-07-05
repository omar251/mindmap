# Markdown to Mind Map

This project is a Python application that takes a Markdown file and generates a mind map visualization in an HTML file.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/omar251/mindmap.git
    cd mindmap
    ```

2.  **Install dependencies using uv:**
    ```bash
    uv pip install .
    ```

## Usage

To generate a mind map, run the following command in your terminal:

```bash
uv run python main.py <your_markdown_file.md>
```

This will create an HTML file named `mindmap.html` in the same directory. You can customize the output file name using the `-o` or `--output` option:

```bash
uv run python main.py <your_markdown_file.md> -o my-mindmap
```

This will create `my-mindmap.html`.

## How it works

The script parses the headings in the Markdown file to create the nodes of the mind map. The hierarchy of the headings (e.g., `#`, `##`, `###`) determines the structure of the mind map.
