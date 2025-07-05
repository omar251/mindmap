# Plugin System Guide

The mindmap generator includes a powerful plugin system that enhances content rendering.

## Available Plugins

### Math Plugin
Renders LaTeX mathematical expressions using KaTeX.

**Features:**
- Inline math: `$E = mc^2$`
- Block math: `$$\int f(x) dx$$`
- Automatic error handling

**Configuration:**
```yaml
plugins:
  math: true
```

### Code Highlighting Plugin
Provides syntax highlighting for code blocks using Prism.js.

**Supported Languages:**
- JavaScript, Python, Java, C++
- CSS, HTML, JSON, YAML
- Bash, SQL, Markdown

**Usage:**
```markdown
```python
def hello_world():
    print("Hello, World!")
```
```

**Configuration:**
```yaml
plugins:
  code-highlight: true
```

### Emoji Plugin
Converts text shortcuts to emoji characters.

**Available Shortcuts:**
- `:smile:` → 😊
- `:heart:` → ❤️
- `:star:` → ⭐
- `:fire:` → 🔥
- `:check:` → ✅
- `:cross:` → ❌
- `:warning:` → ⚠️
- `:info:` → ℹ️
- `:rocket:` → 🚀
- `:bulb:` → 💡
- `:gear:` → ⚙️
- `:book:` → 📚
- `:computer:` → 💻
- `:mobile:` → 📱
- `:email:` → 📧
- `:calendar:` → 📅

**Configuration:**
```yaml
plugins:
  emoji: true
```

### Link Enhancement Plugin
Enhances markdown links with appropriate icons and styling.

**Features:**
- GitHub links get 🐙 icon
- YouTube links get 📺 icon
- Google Docs get 📄 icon
- PDF files get 📄 icon
- Images get 🖼️ icon
- Generic links get 🔗 icon

**Configuration:**
```yaml
plugins:
  links: true
```

## Plugin Management

### Enable/Disable via CLI
```bash
# Disable specific plugins
python mindmap.py document.md --disable-plugins math emoji

# Enable only certain plugins
python mindmap.py document.md --enable-only code-highlight links
```

### Configuration File
```yaml
plugins:
  math: true              # Enable math rendering
  code-highlight: false   # Disable code highlighting
  emoji: true             # Enable emoji shortcuts
  links: true             # Enable link enhancement
```

## Creating Custom Plugins

The plugin system is extensible. To create a custom plugin:

1. Inherit from the `Plugin` base class
2. Implement `process_content()` method
3. Implement `get_assets()` method
4. Register with the plugin manager

Example:
```python
class CustomPlugin(Plugin):
    def __init__(self):
        super().__init__("custom", "1.0.0")
    
    def process_content(self, content, node_data):
        # Process and return modified content
        return content
    
    def get_assets(self):
        return {"css": [], "js": []}
```