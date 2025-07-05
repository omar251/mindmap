import argparse
from markdown_it import MarkdownIt

class MindMap:
    def __init__(self, title="Mind Map"):
        self.title = title
        self.nodes = []
        self.edges = []

    def add_node(self, node_id, label):
        self.nodes.append({'id': node_id, 'label': label})

    def add_edge(self, parent_id, child_id):
        self.edges.append({'from': parent_id, 'to': child_id})

    def to_mermaid(self):
        mermaid_string = "graph TD\n"
        for node in self.nodes:
            mermaid_string += f"    {node['id']}[\"{node['label']}\"]\n"
        for edge in self.edges:
            mermaid_string += f"    {edge['from']} --> {edge['to']}\n"
        return mermaid_string

    def render(self, filename):
        mermaid_script = self.to_mermaid()
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
</head>
<body>
    <div class="mermaid">
{mermaid_script}
    </div>
</body>
</html>
"""
        with open(f"{filename}.html", "w", encoding="utf-8") as f:
            f.write(html_content)

def parse_markdown(file_path):
    md_parser = MarkdownIt()
    with open(file_path, 'r', encoding='utf-8') as f:
        tokens = md_parser.parse(f.read())
    
    mind_map = MindMap()
    path = []
    node_counter = 0

    for token in tokens:
        if token.type == 'heading_open':
            level = int(token.tag[1])
            content_token = tokens[tokens.index(token) + 1]
            if content_token.type == 'inline':
                node_text = content_token.content
                node_id = f"node_{node_counter}"
                node_counter += 1

                while len(path) >= level:
                    path.pop()

                parent_id = path[-1] if path else None
                
                mind_map.add_node(node_id, node_text)
                
                if parent_id:
                    mind_map.add_edge(parent_id, node_id)
                
                path.append(node_id)

    return mind_map

def main():
    parser = argparse.ArgumentParser(description="Generate a mind map from a Markdown file.")
    parser.add_argument("input_file", help="The path to the input Markdown file.")
    parser.add_argument("-o", "--output", default="mindmap", help="The output filename (without extension).")
    args = parser.parse_args()

    mind_map = parse_markdown(args.input_file)
    mind_map.render(args.output)
    print(f"Mind map saved to {args.output}.html")

if __name__ == "__main__":
    main()
