import argparse
import json
import re
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
        nodes_json, edges_json = self.to_vis_data()
        
        # Convert markdown to HTML for better display
        md_parser = MarkdownIt()
        html_content = md_parser.render(markdown_content)
        
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
        
        with open(f"{filename}.html", "w", encoding="utf-8") as f:
            f.write(html_content_formatted)

def parse_markdown(file_path):
    md_parser = MarkdownIt()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        tokens = md_parser.parse(content)
    
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

    return mind_map

def main():
    parser = argparse.ArgumentParser(description="Generate an interactive mind map from a Markdown file.")
    parser.add_argument("input_file", help="The path to the input Markdown file.")
    parser.add_argument("-o", "--output", default="mindmap", help="The output filename (without extension).")
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    mind_map = parse_markdown(args.input_file)
    mind_map.render(args.output, markdown_content)
    print(f"Interactive mind map saved to {args.output}.html")

if __name__ == "__main__":
    main()