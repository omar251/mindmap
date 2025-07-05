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
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            display: flex;
            flex-direction: row;
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        #mynetwork {{
            width: 50%;
            height: 100vh;
            border: 1px solid lightgray;
        }}
        #markdown-content {{
            width: 50%;
            height: 100vh;
            border: 1px solid lightgray;
            padding: 10px;
            overflow: auto;
            white-space: pre-wrap;
            font-family: monospace;
            background-color: #f8f9fa;
        }}
        .line-number {{
            color: #666;
            margin-right: 10px;
            user-select: none;
        }}
        .highlighted-line {{
            background-color: #ffeb3b;
            padding: 2px 0;
            margin: 0 -10px;
            padding-left: 10px;
            border-left: 4px solid #ffc107;
        }}
        .highlighted-section {{
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
            margin: 0 -10px;
            padding-left: 10px;
        }}
        #markdown-html {{
            width: 50%;
            height: 100vh;
            border: 1px solid lightgray;
            padding: 20px;
            overflow: auto;
            background-color: white;
            display: none;
        }}
        .controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }}
        .controls button {{
            margin: 0 5px;
            padding: 5px 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}
        .controls button:hover {{
            background: #0056b3;
        }}
        .controls button.active {{
            background: #28a745;
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <div id="markdown-content">
        <pre><code>{numbered_content}</code></pre>
    </div>
    <div id="markdown-html">
        {html_content}
    </div>
    <div class="controls">
        <button id="toggle-view" onclick="toggleView()">HTML View</button>
        <button onclick="clearHighlights()">Clear Highlights</button>
    </div>
    
    <script type="text/javascript">
        var allNodes = new vis.DataSet({nodes_json});
        var allEdges = new vis.DataSet({edges_json});
        var isHtmlView = false;

        var container = document.getElementById('mynetwork');
        
        var data = {{
            nodes: allNodes,
            edges: allEdges
        }};

        var options = {{
            layout: {{
                hierarchical: {{
                    direction: "UD",
                    sortMethod: "directed"
                }}
            }},
            nodes: {{
                shape: 'box',
                margin: 10,
                widthConstraint: {{
                    maximum: 200
                }},
                font: {{
                    size: 14
                }},
                color: {{
                    background: '#e3f2fd',
                    border: '#1976d2',
                    highlight: {{
                        background: '#ffeb3b',
                        border: '#ff9800'
                    }}
                }}
            }},
            edges: {{
                arrows: 'to',
                color: {{
                    color: '#1976d2'
                }}
            }},
            physics: true
        }};

        var network = new vis.Network(container, data, options);

        // Helper function to get all descendants of a node
        function getDescendants(nodeId) {{
            var descendants = [];
            var stack = [nodeId];
            while (stack.length > 0) {{
                var current = stack.pop();
                var childEdges = allEdges.get({{
                    filter: function(edge) {{
                        return edge.from === current;
                    }}
                }});
                childEdges.forEach(function(edge) {{
                    descendants.push(edge.to);
                    stack.push(edge.to);
                }});
            }}
            return descendants;
        }}

        function highlightTextForNode(nodeId) {{
            var node = allNodes.get(nodeId);
            if (!node || !node.line_number) return;
            
            clearHighlights();
            
            var lineElement = document.getElementById('line-' + node.line_number);
            if (lineElement) {{
                var lineContainer = lineElement.parentElement;
                lineContainer.classList.add('highlighted-line');
                
                // Scroll to the highlighted line
                var markdownContent = document.getElementById('markdown-content');
                var elementTop = lineElement.offsetTop;
                var containerTop = markdownContent.scrollTop;
                var containerHeight = markdownContent.clientHeight;
                
                // Scroll to center the line in the view
                markdownContent.scrollTop = elementTop - containerHeight / 2;
            }}
        }}

        function clearHighlights() {{
            var highlighted = document.querySelectorAll('.highlighted-line, .highlighted-section');
            highlighted.forEach(function(el) {{
                el.classList.remove('highlighted-line', 'highlighted-section');
            }});
        }}

        function toggleView() {{
            var markdownContent = document.getElementById('markdown-content');
            var markdownHtml = document.getElementById('markdown-html');
            var toggleBtn = document.getElementById('toggle-view');
            
            if (isHtmlView) {{
                markdownContent.style.display = 'block';
                markdownHtml.style.display = 'none';
                toggleBtn.textContent = 'HTML View';
                toggleBtn.classList.remove('active');
            }} else {{
                markdownContent.style.display = 'none';
                markdownHtml.style.display = 'block';
                toggleBtn.textContent = 'Raw View';
                toggleBtn.classList.add('active');
            }}
            isHtmlView = !isHtmlView;
        }}

        network.on('click', function(properties) {{
            var ids = properties.nodes;
            if (ids.length > 0) {{
                var clickedNodeId = ids[0];
                
                // Highlight corresponding text
                highlightTextForNode(clickedNodeId);
                
                // Existing expand/collapse logic
                var childEdges = allEdges.get({{
                    filter: function(edge) {{
                        return edge.from === clickedNodeId;
                    }}
                }});

                if (childEdges.length > 0) {{
                    var childNodeIds = childEdges.map(function(edge) {{ return edge.to; }});
                    var childNodes = allNodes.get(childNodeIds);

                    var anyHidden = childNodes.some(function(node) {{ return node.hidden; }});

                    if (anyHidden) {{
                        // Show direct children
                        var updates = childNodeIds.map(function(id) {{
                            return {{ id: id, hidden: false }};
                        }});
                        allNodes.update(updates);
                    }} else {{
                        // Hide entire subtree (all descendants)
                        var descendants = getDescendants(clickedNodeId);
                        var updates = descendants.map(function(id) {{
                            return {{ id: id, hidden: true }};
                        }});
                        allNodes.update(updates);
                    }}
                }}
            }}
        }});
        
        // Initially hide nodes with level > 1
        var updates = [];
        allNodes.forEach(function(node) {{
            if (node.level > 1) {{
                updates.push({{id: node.id, hidden: true}});
            }} else {{
                updates.push({{id: node.id, hidden: false}});
            }}
        }});
        allNodes.update(updates);
        
        network.on("stabilizationIterationsDone", function () {{
            network.setOptions( {{ physics: false }} );
        }});

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                clearHighlights();
            }}
            if (e.key === 'h' && e.ctrlKey) {{
                e.preventDefault();
                toggleView();
            }}
        }});

    </script>
</body>
</html>
"""
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