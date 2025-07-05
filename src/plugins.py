"""Plugin system for mindmap enhancements."""

import re
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Process node content and return modified content."""
        pass
    
    @abstractmethod
    def get_assets(self) -> Dict[str, List[str]]:
        """Return CSS and JS assets needed by this plugin."""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this plugin."""
        return {}


class MathPlugin(Plugin):
    """Plugin for rendering mathematical expressions using KaTeX."""
    
    def __init__(self):
        super().__init__("math", "1.0.0")
        self.katex_version = "0.16.8"
    
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Convert LaTeX math expressions to KaTeX-renderable format."""
        # Inline math: $...$
        content = re.sub(
            r'\$([^$]+)\$',
            r'<span class="katex-inline" data-katex="\\(\1\\)">$\1$</span>',
            content
        )
        
        # Block math: $$...$$
        content = re.sub(
            r'\$\$([^$]+)\$\$',
            r'<div class="katex-block" data-katex="\\[\1\\]">$$\1$$</div>',
            content
        )
        
        return content
    
    def get_assets(self) -> Dict[str, List[str]]:
        """Return KaTeX CSS and JS assets."""
        return {
            "css": [
                f"https://cdn.jsdelivr.net/npm/katex@{self.katex_version}/dist/katex.min.css"
            ],
            "js": [
                f"https://cdn.jsdelivr.net/npm/katex@{self.katex_version}/dist/katex.min.js",
                f"https://cdn.jsdelivr.net/npm/katex@{self.katex_version}/dist/contrib/auto-render.min.js"
            ]
        }


class CodeHighlightPlugin(Plugin):
    """Plugin for syntax highlighting using Prism.js."""
    
    def __init__(self):
        super().__init__("code-highlight", "1.0.0")
        self.prism_version = "1.29.0"
        self.supported_languages = [
            "javascript", "python", "java", "cpp", "css", "html", 
            "json", "yaml", "bash", "sql", "markdown"
        ]
    
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Add syntax highlighting classes to code blocks."""
        # Inline code
        content = re.sub(
            r'`([^`]+)`',
            r'<code class="language-text">\1</code>',
            content
        )
        
        # Block code with language specification
        def replace_code_block(match):
            language = match.group(1) or "text"
            code = match.group(2)
            if language in self.supported_languages:
                return f'<pre><code class="language-{language}">{code}</code></pre>'
            else:
                return f'<pre><code class="language-text">{code}</code></pre>'
        
        content = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            replace_code_block,
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def get_assets(self) -> Dict[str, List[str]]:
        """Return Prism.js CSS and JS assets."""
        return {
            "css": [
                f"https://cdn.jsdelivr.net/npm/prismjs@{self.prism_version}/themes/prism.min.css"
            ],
            "js": [
                f"https://cdn.jsdelivr.net/npm/prismjs@{self.prism_version}/components/prism-core.min.js",
                f"https://cdn.jsdelivr.net/npm/prismjs@{self.prism_version}/plugins/autoloader/prism-autoloader.min.js"
            ]
        }


class EmojiPlugin(Plugin):
    """Plugin for rendering emoji shortcuts."""
    
    def __init__(self):
        super().__init__("emoji", "1.0.0")
        self.emoji_map = {
            ":smile:": "😊", ":heart:": "❤️", ":star:": "⭐", ":fire:": "🔥",
            ":check:": "✅", ":cross:": "❌", ":warning:": "⚠️", ":info:": "ℹ️",
            ":rocket:": "🚀", ":bulb:": "💡", ":gear:": "⚙️", ":book:": "📚",
            ":computer:": "💻", ":mobile:": "📱", ":email:": "📧", ":calendar:": "📅"
        }
    
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Replace emoji shortcuts with actual emoji."""
        for shortcut, emoji in self.emoji_map.items():
            content = content.replace(shortcut, emoji)
        return content
    
    def get_assets(self) -> Dict[str, List[str]]:
        """No external assets needed for emoji."""
        return {"css": [], "js": []}


class LinkPlugin(Plugin):
    """Plugin for enhancing links with icons and previews."""
    
    def __init__(self):
        super().__init__("links", "1.0.0")
    
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Enhance markdown links with icons."""
        # Regular markdown links
        def enhance_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Add appropriate icon based on URL
            icon = self._get_link_icon(url)
            return f'<a href="{url}" target="_blank" class="enhanced-link">{icon} {text}</a>'
        
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', enhance_link, content)
        return content
    
    def _get_link_icon(self, url: str) -> str:
        """Get appropriate icon for URL."""
        if "github.com" in url:
            return "🐙"
        elif "youtube.com" in url or "youtu.be" in url:
            return "📺"
        elif "docs.google.com" in url:
            return "📄"
        elif url.endswith(('.pdf', '.doc', '.docx')):
            return "📄"
        elif url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return "🖼️"
        else:
            return "🔗"
    
    def get_assets(self) -> Dict[str, List[str]]:
        """Return CSS for enhanced links."""
        return {
            "css": [],
            "js": [],
            "inline_css": """
                .enhanced-link {
                    text-decoration: none;
                    color: #1976d2;
                    border-bottom: 1px dotted #1976d2;
                }
                .enhanced-link:hover {
                    background-color: #e3f2fd;
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        }


class PluginManager:
    """Manages all plugins and their lifecycle."""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.load_default_plugins()
    
    def load_default_plugins(self):
        """Load default plugins."""
        self.register_plugin(MathPlugin())
        self.register_plugin(CodeHighlightPlugin())
        self.register_plugin(EmojiPlugin())
        self.register_plugin(LinkPlugin())
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin."""
        self.plugins[plugin.name] = plugin
    
    def enable_plugin(self, name: str):
        """Enable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = True
    
    def disable_plugin(self, name: str):
        """Disable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = False
    
    def process_content(self, content: str, node_data: Dict[str, Any]) -> str:
        """Process content through all enabled plugins."""
        for plugin in self.plugins.values():
            if plugin.enabled:
                content = plugin.process_content(content, node_data)
        return content
    
    def get_all_assets(self) -> Dict[str, List[str]]:
        """Get all assets from enabled plugins."""
        all_assets = {"css": [], "js": [], "inline_css": []}
        
        for plugin in self.plugins.values():
            if plugin.enabled:
                assets = plugin.get_assets()
                all_assets["css"].extend(assets.get("css", []))
                all_assets["js"].extend(assets.get("js", []))
                if "inline_css" in assets:
                    all_assets["inline_css"].append(assets["inline_css"])
        
        return all_assets
    
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        return [name for name, plugin in self.plugins.items() if plugin.enabled]
    
    def configure_plugins(self, config: Dict[str, Any]):
        """Configure plugins based on configuration."""
        plugins_config = config.get("plugins", {})
        
        for plugin_name, plugin_config in plugins_config.items():
            if plugin_name in self.plugins:
                if isinstance(plugin_config, bool):
                    # Simple enable/disable
                    if plugin_config:
                        self.enable_plugin(plugin_name)
                    else:
                        self.disable_plugin(plugin_name)
                elif isinstance(plugin_config, dict):
                    # Advanced configuration
                    enabled = plugin_config.get("enabled", True)
                    if enabled:
                        self.enable_plugin(plugin_name)
                    else:
                        self.disable_plugin(plugin_name)