import argparse
import json
import re
import sys
import os
from pathlib import Path
from markdown_it import MarkdownIt
from config import MindMapConfig, get_theme
from plugins import PluginManager
from layouts import LayoutManager, create_layout_selector_html, create_layout_javascript

class MindMap:
    def __init__(self, title="Mind Map", config=None):
        self.title = title
        self.config = config or MindMapConfig()
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        self.plugin_manager = PluginManager()
        self.layout_manager = LayoutManager()
        
        # Configure plugins based on config
        if self.config.plugins:
            self.plugin_manager.configure_plugins({"plugins": self.config.plugins})

    def add_node(self, label, level, parent_id=None, line_number=None):
        node_id = self.node_counter
        self.node_counter += 1
        
        # Process label through plugins
        node_data = {
            'id': node_id,
            'level': level,
            'parent_id': parent_id,
            'line_number': line_number
        }
        processed_label = self.plugin_manager.process_content(label, node_data)
        
        self.nodes.append({
            'id': node_id, 
            'label': processed_label, 
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
        
        # Get plugin assets
        plugin_assets = self.plugin_manager.get_all_assets()
        
        # Get layout-specific options
        layout_options = self.layout_manager.get_layout_options(self.config.layout)
        
        # Load HTML template from external file
        html_template = self._load_template()
        html_content_formatted = html_template.format(
            title=self.title,
            nodes_json=nodes_json,
            edges_json=edges_json,
            numbered_content=numbered_content,
            html_content=html_content,
            config_json=json.dumps(self.config.to_json()),
            plugin_css='\n'.join(f'<link rel="stylesheet" href="{css}">' for css in plugin_assets['css']),
            plugin_js='\n'.join(f'<script src="{js}"></script>' for js in plugin_assets['js']),
            plugin_inline_css='\n'.join(plugin_assets.get('inline_css', [])),
            layout_selector=create_layout_selector_html(),
            layout_javascript=create_layout_javascript(),
            layout_options=json.dumps(layout_options),
            layout_styles=self.layout_manager.get_layout_specific_styles(self.config.layout)
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

def parse_markdown(file_path, external_config=None):
    """Parse a markdown file and create a mind map structure.
    
    Args:
        file_path: Path to the markdown file
        external_config: Optional external configuration to override frontmatter
        
    Returns:
        tuple: (MindMap object, original_content)
        
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
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot read '{file_path}'. Check file permissions.")
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to decode '{file_path}' as UTF-8. Please ensure the file is a valid text file.") from e
    except OSError as e:
        raise OSError(f"Error reading '{file_path}': {e}") from e
    
    # Check if file is empty
    if not original_content.strip():
        raise ValueError(f"Input file '{file_path}' is empty.")
    
    # Extract configuration from frontmatter
    config, content = MindMapConfig.from_frontmatter(original_content)
    
    # Override with external config if provided
    if external_config:
        config = external_config
    
    try:
        md_parser = MarkdownIt()
        lines = content.split('\n')
        tokens = md_parser.parse(content)
    except Exception as e:
        raise RuntimeError(f"Error parsing markdown content: {e}") from e
    
    mind_map = MindMap(config=config)
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

    return mind_map, original_content

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
        epilog="Example: python main.py document.md -o my-mindmap --theme dark"
    )
    parser.add_argument("input_file", help="The path to the input Markdown file.")
    parser.add_argument("-o", "--output", default="mindmap", 
                       help="The output filename (without extension). Default: mindmap")
    parser.add_argument("-c", "--config", 
                       help="Path to configuration file (YAML)")
    parser.add_argument("-t", "--theme", choices=['default', 'dark', 'colorful', 'minimal'],
                       help="Theme to use (overrides config file and frontmatter)")
    parser.add_argument("-l", "--layout", choices=['hierarchical', 'radial', 'tree', 'force_directed', 'circular', 'timeline'],
                       help="Layout to use for the mindmap")
    parser.add_argument("--no-toolbar", action="store_true",
                       help="Disable the toolbar")
    parser.add_argument("--max-width", type=int,
                       help="Maximum width of nodes")
    parser.add_argument("--disable-plugins", nargs='+', 
                       help="Disable specific plugins (math, code-highlight, emoji, links)")
    parser.add_argument("--enable-only", nargs='+',
                       help="Enable only specified plugins")
    
    try:
        args = parser.parse_args()
        
        # Validate input file extension
        if not args.input_file.lower().endswith(('.md', '.markdown', '.txt')):
            print(f"Warning: '{args.input_file}' doesn't have a typical markdown extension (.md, .markdown, .txt)")
        
        # Validate output path
        output_path = f"{args.output}.html"
        validate_output_path(output_path)
        
        # Load configuration
        config = None
        if args.config:
            try:
                config = MindMapConfig.from_file(args.config)
                print(f"Loaded configuration from {args.config}")
            except Exception as e:
                print(f"Warning: Could not load config file '{args.config}': {e}")
        
        # Apply theme override
        if args.theme:
            config = get_theme(args.theme)
            print(f"Using theme: {args.theme}")
        
        # Apply command-line overrides
        if config and args.no_toolbar:
            config.toolbar = False
        if config and args.max_width:
            config.max_width = args.max_width
        if config and args.layout:
            config.layout = args.layout
            print(f"Using layout: {args.layout}")
        
        # Handle plugin configuration
        if config and args.disable_plugins:
            for plugin in args.disable_plugins:
                if plugin in config.plugins:
                    config.plugins[plugin] = False
            print(f"Disabled plugins: {', '.join(args.disable_plugins)}")
        
        if config and args.enable_only:
            # Disable all plugins first
            for plugin in config.plugins:
                config.plugins[plugin] = False
            # Enable only specified plugins
            for plugin in args.enable_only:
                if plugin in config.plugins:
                    config.plugins[plugin] = True
            print(f"Enabled only: {', '.join(args.enable_only)}")
        
        # Parse markdown and create mind map
        try:
            mind_map, markdown_content = parse_markdown(args.input_file, config)
            
            # Show configuration info
            if mind_map.config.theme != 'default':
                print(f"Using configuration: theme={mind_map.config.theme}, colors={len(mind_map.config.colors)} colors")
                
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