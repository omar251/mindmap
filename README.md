# Interactive Mindmap Generator

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python application that transforms Markdown files into beautiful, interactive mind maps with advanced features like plugins, multiple layouts, and rich content support.

## Features

### Multiple Themes & Layouts
- **4 Built-in Themes**: Default, Dark, Colorful, Minimal
- **6 Layout Types**: Hierarchical, Radial, Tree, Force-Directed, Circular, Timeline
- **Real-time Layout Switching**: Change layouts interactively in the browser

### Plugin System
- **Math Rendering**: LaTeX equations with KaTeX (`$E=mc^2$`, `$$\int f(x)dx$$`)
- **Code Highlighting**: Syntax highlighting for 10+ languages
- **Emoji Support**: Convert shortcuts (`:rocket:` → 🚀, `:check:` → ✅)
- **Smart Links**: Auto-detect and enhance links with icons

### Flexible Configuration
- **YAML Frontmatter**: Configure per-file settings
- **External Config Files**: Reusable configuration templates
- **Command-line Options**: Override any setting from CLI
- **Theme Inheritance**: Frontmatter → Config File → CLI → Defaults

### Interactive Features
- **Split-pane Interface**: Mind map + source text side-by-side
- **Section Highlighting**: Click nodes to highlight corresponding text
- **Expandable Nodes**: Click to expand/collapse branches
- **Zoom & Pan**: Navigate large mind maps easily
- **Keyboard Shortcuts**: `Esc` to clear, `Ctrl+H` to toggle views

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/omar251/mindmap.git
cd mindmap

# Install dependencies
uv pip install .
```

### Basic Usage

```bash
# Generate a basic mindmap
python mindmap.py examples/basic-example.md

# Use a specific theme and layout
python mindmap.py examples/advanced-example.md --theme dark --layout radial

# Use a configuration file
python mindmap.py document.md -c configs/advanced-config.yaml
```

## Usage Examples

### 1. Basic Command Line
```bash
# Simple generation
python mindmap.py document.md

# Custom output and theme
python mindmap.py document.md -o my-mindmap --theme dark

# Specific layout
python mindmap.py document.md --layout radial --max-width 300
```

### 2. With Configuration File
```bash
# Use predefined config
python mindmap.py document.md -c configs/advanced-config.yaml

# Override config settings
python mindmap.py document.md -c configs/basic-config.yaml --theme colorful
```

### 3. Plugin Management
```bash
# Disable specific plugins
python mindmap.py document.md --disable-plugins math emoji

# Enable only certain plugins
python mindmap.py document.md --enable-only code-highlight links
```

### 4. Frontmatter Configuration
```markdown
---
mindmap:
  theme: dark
  layout: radial
  colors: ["#64b5f6", "#81c784", "#ffb74d", "#ba68c8"]
  maxWidth: 300
  plugins:
    math: true
    code-highlight: true
    emoji: false
    links: true
---

# Your Content Here
```

## Themes & Layouts

### Available Themes
- **`default`**: Clean blue theme
- **`dark`**: Dark background with light colors  
- **`colorful`**: Vibrant multi-color palette
- **`minimal`**: Subtle gray tones

### Available Layouts
- **`hierarchical`**: Traditional top-down tree (default)
- **`radial`**: Central hub with radiating branches
- **`tree`**: Left-to-right tree structure
- **`force_directed`**: Physics-based dynamic layout
- **`circular`**: Circular arrangement of nodes
- **`timeline`**: Horizontal timeline layout

## Plugin System

### Math Plugin
Render LaTeX equations with KaTeX:
```markdown
- Inline: $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$
- Block: $$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
```

### Code Highlighting Plugin
Syntax highlighting for multiple languages:
```markdown
```python
def fibonacci(n):
    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
```
```

### Emoji Plugin
Convert text shortcuts to emojis:
```markdown
- Success: :check: → ✅
- Rocket: :rocket: → 🚀
- Warning: :warning: → ⚠️
```

### Link Enhancement Plugin
Smart link detection with icons:
```markdown
- [GitHub Repo](https://github.com/user/repo) → 🐙 GitHub Repo
- [YouTube Video](https://youtube.com/watch?v=xyz) → 📺 YouTube Video
- [Documentation](https://example.com/doc.pdf) → 📄 Documentation
```

## Configuration

### Configuration Hierarchy
1. **Command-line arguments** (highest priority)
2. **External config file** (`-c config.yaml`)
3. **Frontmatter** (in markdown file)
4. **Defaults** (lowest priority)

### Configuration Options
```yaml
# Theme and layout
theme: dark                    # default, dark, colorful, minimal
layout: radial                 # hierarchical, radial, tree, force_directed, circular, timeline

# Visual settings
colors: ["#64b5f6", "#81c784"] # Custom color palette
maxWidth: 300                  # Maximum node width
lineWidth: 2                   # Connection line width

# Animation
duration: 500                  # Animation duration (ms)
initialExpandLevel: 2          # Auto-expand levels

# Interaction
zoom: true                     # Enable zoom
pan: true                      # Enable pan
toolbar: true                  # Show toolbar

# Plugins
plugins:
  math: true                   # LaTeX math rendering
  code-highlight: true         # Syntax highlighting
  emoji: true                  # Emoji shortcuts
  links: true                  # Enhanced links
```

## Project Structure

```
mindmap/
├── src/                     # Source code
│   ├── main.py             # Main application
│   ├── config.py           # Configuration system
│   ├── plugins.py          # Plugin architecture
│   ├── layouts.py          # Layout management
│   └── template.html       # HTML template
├── examples/               # Example files
│   ├── basic-example.md    # Simple example
│   └── advanced-example.md # Advanced features demo
├── configs/                # Configuration templates
│   ├── basic-config.yaml   # Basic configuration
│   └── advanced-config.yaml # Advanced configuration
├── docs/                   # Documentation
├── mindmap.py              # Entry point script
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Command Line Reference

```bash
python mindmap.py [-h] [-o OUTPUT] [-c CONFIG] 
                  [-t {default,dark,colorful,minimal}]
                  [-l {hierarchical,radial,tree,force_directed,circular,timeline}]
                  [--no-toolbar] [--max-width MAX_WIDTH]
                  [--disable-plugins PLUGIN [PLUGIN ...]]
                  [--enable-only PLUGIN [PLUGIN ...]]
                  input_file

Options:
  -h, --help            Show help message
  -o, --output OUTPUT   Output filename (without extension)
  -c, --config CONFIG   Path to configuration file (YAML)
  -t, --theme THEME     Theme to use
  -l, --layout LAYOUT   Layout to use
  --no-toolbar          Disable the toolbar
  --max-width WIDTH     Maximum width of nodes
  --disable-plugins     Disable specific plugins
  --enable-only         Enable only specified plugins

Examples:
  python mindmap.py document.md
  python mindmap.py document.md --theme dark --layout radial
  python mindmap.py document.md -c configs/advanced-config.yaml
```

## Use Cases

### Documentation
- Project documentation
- API references
- User guides
- Knowledge bases

### Education
- Course outlines
- Study guides
- Concept maps
- Research organization

### Business
- Project planning
- Process flows
- Organizational charts
- Strategy mapping

### Research
- Literature reviews
- Methodology outlines
- Data organization
- Hypothesis mapping

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [markmap](https://markmap.js.org/) for design patterns
- Built with [vis.js](https://visjs.org/) for network visualization
- Uses [markdown-it-py](https://github.com/executablebooks/markdown-it-py) for parsing
- Math rendering powered by [KaTeX](https://katex.org/)
- Code highlighting by [Prism.js](https://prismjs.com/)

---

**Transform your markdown into beautiful, interactive mind maps!**