import argparse
import json
import re
import sys
import os
from pathlib import Path
from markdown_it import MarkdownIt

class MindMap:
    def __init__(self, title="Mind Map"):
        self.title = title
        self.nodes = []
        self.edges = []
        self.node_counter = 0

    def add_node(self, label, level, parent_id=None, line_number=None):
        node_id = self.node_counter
        self.node_counter += 1
        self.nodes.append({
            'id': node_id, 
            'label': label, 
            'level': level, 
            'hidden': level > 1,
            'line_number': line_number
        })
        if parent_id is not None:
            self.edges.append({'from': parent_id, 'to': node_id})
        return node_id

    def to_vis_data(self):
        return json.dumps(self.nodes), json.dumps(self.edges)
    
    def _load_template(self, template_path="template.html"):
        """Load the HTML template from an external file.
        
        Args:
            template_path: Path to the HTML template file
            
        Returns:
            str: The template content
            
        Raises:
            FileNotFoundError: If template file is not found
            OSError: If unable to read template file
        """
        # Try to find template relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_full_path = os.path.join(script_dir, template_path)
        
        # If not found relative to script, try current working directory
        if not os.path.exists(template_full_path):
            template_full_path = template_path
        
        try:
            with open(template_full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {template_path}. Please ensure 'template.html' exists in the same directory as the script.")
        except OSError as e:
            raise OSError(f"Error reading template file '{template_path}': {e}") from e

    def render(self, filename, markdown_content):
        """Render the mind map to an HTML file.
        
        Args:
            filename: Output filename (without extension)
            markdown_content: Original markdown content for display
            
        Raises:
            PermissionError: If unable to write to output file
            OSError: If other file system errors occur
        """
        try:
            nodes_json, edges_json = self.to_vis_data()
            
            # Convert markdown to HTML for better display
            md_parser = MarkdownIt()
            html_content = md_parser.render(markdown_content)
        except Exception as e:
            raise RuntimeError(f"Error processing markdown content: {e}") from e
        
        # Add line numbers to the HTML content for easier targeting
        lines = markdown_content.split('\n')
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f'<span id="line-{i}" class="line-number">{i:3d}</span> {line}')
        numbered_content = '\n'.join(numbered_lines)
        
        # Load HTML template from external file
        html_template = self._load_template()
        html_content_formatted = html_template.format(
            title=self.title,
            nodes_json=nodes_json,
            edges_json=edges_json,
            numbered_content=numbered_content,
            html_content=html_content
        )
        
        output_path = f"{filename}.html"
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content_formatted)
        except PermissionError:
            raise PermissionError(f"Permission denied: Cannot write to '{output_path}'. Check file permissions and ensure the directory is writable.")
        except OSError as e:
            raise OSError(f"Error writing to '{output_path}': {e}") from e

def parse_markdown(file_path):
    """Parse a markdown file and create a mind map structure.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        MindMap: The parsed mind map object
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        PermissionError: If unable to read the input file
        ValueError: If the file is empty or contains no valid headings
    """
    # Validate input file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file '{file_path}' not found.")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"'{file_path}' is not a file.")
    
    try:
        md_parser = MarkdownIt()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot read '{file_path}'. Check file permissions.")
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to decode '{file_path}' as UTF-8. Please ensure the file is a valid text file.") from e
    except OSError as e:
        raise OSError(f"Error reading '{file_path}': {e}") from e
    
    # Check if file is empty
    if not content.strip():
        raise ValueError(f"Input file '{file_path}' is empty.")
    
    try:
        lines = content.split('\n')
        tokens = md_parser.parse(content)
    except Exception as e:
        raise RuntimeError(f"Error parsing markdown content: {e}") from e
    
    mind_map = MindMap()
    path = []

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == 'heading_open':
            level = int(token.tag[1])
            if i + 1 < len(tokens):
                content_token = tokens[i + 1]
                if content_token.type == 'inline':
                    node_text = content_token.content
                    
                    # Find the line number of this heading
                    line_number = None
                    if hasattr(token, 'map') and token.map:
                        line_number = token.map[0] + 1  # markdown_it uses 0-based indexing

                    while len(path) >= level:
                        path.pop()

                    parent_id = path[-1] if path else None
                    
                    node_id = mind_map.add_node(node_text, level, parent_id, line_number)
                    
                    path.append(node_id)
        i += 1

    # Validate that we found at least one heading
    if not mind_map.nodes:
        raise ValueError(f"No valid headings found in '{file_path}'. Please ensure the file contains markdown headings (# ## ### etc.).")

    return mind_map

def validate_output_path(output_path):
    """Validate that the output path is writable.
    
    Args:
        output_path: The output file path to validate
        
    Raises:
        ValueError: If the output path is invalid
        PermissionError: If the output directory is not writable
    """
    # Check if output path contains invalid characters
    if not output_path or output_path.strip() == "":
        raise ValueError("Output filename cannot be empty.")
    
    # Get the directory part of the output path
    output_dir = os.path.dirname(output_path)
    if output_dir == "":
        output_dir = "."
    
    # Check if directory exists and is writable
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Cannot create output directory '{output_dir}'. Check permissions.")
        except OSError as e:
            raise OSError(f"Error creating output directory '{output_dir}': {e}") from e
    
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Output directory '{output_dir}' is not writable. Check permissions.")

def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive mind map from a Markdown file.",
        epilog="Example: python main.py document.md -o my-mindmap"
    )
    parser.add_argument("input_file", help="The path to the input Markdown file.")
    parser.add_argument("-o", "--output", default="mindmap", 
                       help="The output filename (without extension). Default: mindmap")
    
    try:
        args = parser.parse_args()
        
        # Validate input file extension
        if not args.input_file.lower().endswith(('.md', '.markdown', '.txt')):
            print(f"Warning: '{args.input_file}' doesn't have a typical markdown extension (.md, .markdown, .txt)")
        
        # Validate output path
        output_path = f"{args.output}.html"
        validate_output_path(output_path)
        
        # Read markdown content
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied reading '{args.input_file}'.", file=sys.stderr)
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Error: Unable to decode '{args.input_file}' as UTF-8. Please ensure it's a valid text file.", file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print(f"Error: Unable to read '{args.input_file}': {e}", file=sys.stderr)
            sys.exit(1)
        
        # Parse markdown and create mind map
        try:
            mind_map = parse_markdown(args.input_file)
        except (FileNotFoundError, PermissionError, ValueError, RuntimeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Render the mind map
        try:
            mind_map.render(args.output, markdown_content)
            print(f"Success: Interactive mind map saved to {args.output}.html")
            print(f"  Open the file in your web browser to view the mind map.")
        except (PermissionError, OSError, RuntimeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()