"""Configuration system inspired by markmap."""

import yaml
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class MindMapConfig:
    """Configuration options for mind map generation."""
    
    # Visual appearance
    colors: List[str] = None
    color_freeze_level: int = 0
    theme: str = "default"
    
    # Layout
    max_width: int = 200
    spacing_horizontal: int = 80
    spacing_vertical: int = 5
    line_width: int = 2
    
    # Animation
    duration: int = 500
    initial_expand_level: int = -1
    
    # Interaction
    zoom: bool = True
    pan: bool = True
    
    # Features
    toolbar: bool = True
    layout: str = "hierarchical"
    
    # Plugins
    plugins: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                "#1976d2", "#388e3c", "#f57c00", "#7b1fa2", 
                "#c2185b", "#00796b", "#5d4037", "#455a64"
            ]
        if self.plugins is None:
            self.plugins = {
                "math": True,
                "code-highlight": True,
                "emoji": True,
                "links": True
            }
    
    @classmethod
    def from_frontmatter(cls, markdown_content: str) -> tuple['MindMapConfig', str]:
        """Extract configuration from markdown frontmatter.
        
        Returns:
            tuple: (config, markdown_without_frontmatter)
        """
        # Check for YAML frontmatter
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, markdown_content, re.DOTALL)
        
        if not match:
            return cls(), markdown_content
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            mindmap_config = frontmatter.get('mindmap', {})
            
            # Remove frontmatter from content
            content_without_frontmatter = markdown_content[match.end():]
            
            # Create config with frontmatter values
            config = cls()
            for key, value in mindmap_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config, content_without_frontmatter
            
        except yaml.YAMLError:
            # If YAML parsing fails, return default config
            return cls(), markdown_content
    
    @classmethod
    def from_file(cls, config_file: str) -> 'MindMapConfig':
        """Load configuration from a file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            config = cls()
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config
        except (FileNotFoundError, yaml.YAMLError):
            return cls()
    
    def to_json(self) -> Dict[str, Any]:
        """Convert config to JSON-serializable dict for JavaScript."""
        return {
            'colors': self.colors,
            'colorFreezeLevel': self.color_freeze_level,
            'maxWidth': self.max_width,
            'spacingHorizontal': self.spacing_horizontal,
            'spacingVertical': self.spacing_vertical,
            'lineWidth': self.line_width,
            'duration': self.duration,
            'initialExpandLevel': self.initial_expand_level,
            'zoom': self.zoom,
            'pan': self.pan,
            'toolbar': self.toolbar,
            'theme': self.theme,
            'layout': self.layout,
            'plugins': self.plugins
        }


# Predefined themes
THEMES = {
    'default': MindMapConfig(
        colors=["#1976d2", "#388e3c", "#f57c00", "#7b1fa2"],
        theme="default"
    ),
    'dark': MindMapConfig(
        colors=["#64b5f6", "#81c784", "#ffb74d", "#ba68c8"],
        theme="dark"
    ),
    'colorful': MindMapConfig(
        colors=["#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#00bcd4"],
        theme="colorful"
    ),
    'minimal': MindMapConfig(
        colors=["#424242", "#616161", "#757575", "#9e9e9e"],
        theme="minimal"
    )
}


def get_theme(theme_name: str) -> MindMapConfig:
    """Get a predefined theme configuration."""
    return THEMES.get(theme_name, THEMES['default'])