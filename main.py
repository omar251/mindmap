import argparse
import json
from markdown_it import MarkdownIt

class MindMap:
    def __init__(self, title="Mind Map"):
        self.title = title
        self.nodes = []
        self.edges = []
        self.node_counter = 0

    def add_node(self, label, level, parent_id=None):
        node_id = self.node_counter
        self.node_counter += 1
        self.nodes.append({'id': node_id, 'label': label, 'level': level, 'hidden': level > 1})
        if parent_id is not None:
            self.edges.append({'from': parent_id, 'to': node_id})
        return node_id

    def to_vis_data(self):
        return json.dumps(self.nodes), json.dumps(self.edges)

    def render(self, filename, markdown_content):
        nodes_json, edges_json = self.to_vis_data()
        
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
        }}
        #mynetwork {{
            width: 50%;
            height: 800px;
            border: 1px solid lightgray;
        }}
        #markdown-content {{
            width: 50%;
            height: 800px;
            border: 1px solid lightgray;
            padding: 10px;
            overflow: auto;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <div id="markdown-content">
        <pre><code>{markdown_content}</code></pre>
    </div>
    <script type="text/javascript">
        var allNodes = new vis.DataSet({nodes_json});
        var allEdges = new vis.DataSet({edges_json});

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
                }}
            }},
            edges: {{
                arrows: 'to'
            }},
            physics: true
        }};

        var network = new vis.Network(container, data, options);

        network.on('click', function(properties) {{
            var ids = properties.nodes;
            if (ids.length > 0) {{
                var clickedNodeId = ids[0];
                var childEdges = allEdges.get({{
                    filter: function(edge) {{
                        return edge.from === clickedNodeId;
                    }}
                }});

                var updates = [];
                childEdges.forEach(function(edge) {{
                    var childNode = allNodes.get(edge.to);
                    updates.push({{ id: childNode.id, hidden: !childNode.hidden }});
                }});
                allNodes.update(updates);
            }}
        }});
        
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

    </script>
</body>
</html>
"""
        html_content = html_template.format(
            title=self.title,
            nodes_json=nodes_json,
            edges_json=edges_json,
            markdown_content=markdown_content
        )
        
        with open(f"{filename}.html", "w", encoding="utf-8") as f:
            f.write(html_content)

def parse_markdown(file_path):
    md_parser = MarkdownIt()
    with open(file_path, 'r', encoding='utf-8') as f:
        tokens = md_parser.parse(f.read())
    
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

                    while len(path) >= level:
                        path.pop()

                    parent_id = path[-1] if path else None
                    
                    node_id = mind_map.add_node(node_text, level, parent_id)
                    
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
