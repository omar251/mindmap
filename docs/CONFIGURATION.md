# Configuration Guide

This guide covers all configuration options available in the mindmap generator.

## Configuration Methods

### 1. Frontmatter (Per-file)
Add YAML frontmatter to your markdown files:

```yaml
---
mindmap:
  theme: dark
  layout: radial
  colors: ["#64b5f6", "#81c784", "#ffb74d"]
  plugins:
    math: true
    emoji: false
---
```

### 2. External Config Files
Create reusable YAML configuration files:

```bash
python mindmap.py document.md -c configs/my-config.yaml
```

### 3. Command Line Arguments
Override any setting from the command line:

```bash
python mindmap.py document.md --theme dark --layout radial --max-width 300
```

## Configuration Options

### Visual Settings
- `theme`: Theme name (default, dark, colorful, minimal)
- `colors`: Array of hex colors for nodes
- `maxWidth`: Maximum width of nodes in pixels
- `lineWidth`: Width of connection lines

### Layout Settings
- `layout`: Layout type (hierarchical, radial, tree, force_directed, circular, timeline)
- `spacingHorizontal`: Horizontal spacing between nodes
- `spacingVertical`: Vertical spacing between nodes

### Animation Settings
- `duration`: Animation duration in milliseconds
- `initialExpandLevel`: Number of levels to expand initially (-1 for all)

### Interaction Settings
- `zoom`: Enable/disable zoom functionality
- `pan`: Enable/disable pan functionality
- `toolbar`: Show/hide the toolbar

### Plugin Settings
- `plugins.math`: Enable LaTeX math rendering
- `plugins.code-highlight`: Enable syntax highlighting
- `plugins.emoji`: Enable emoji shortcuts
- `plugins.links`: Enable enhanced links

## Example Configurations

### Minimal Configuration
```yaml
theme: minimal
layout: hierarchical
plugins:
  math: false
  emoji: false
```

### Presentation Mode
```yaml
theme: dark
layout: radial
maxWidth: 400
duration: 1000
initialExpandLevel: 2
```

### Documentation Mode
```yaml
theme: default
layout: tree
plugins:
  math: true
  code-highlight: true
  links: true
```