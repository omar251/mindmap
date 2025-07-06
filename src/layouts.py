"""Advanced layout system for mindmaps."""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


class LayoutType(Enum):
    """Available layout types."""
    HIERARCHICAL = "hierarchical"
    RADIAL = "radial"
    TREE = "tree"
    FORCE_DIRECTED = "force_directed"
    CIRCULAR = "circular"
    TIMELINE = "timeline"


@dataclass
class LayoutConfig:
    """Configuration for a specific layout."""
    layout_type: LayoutType
    options: Dict[str, Any]
    description: str
    best_for: List[str]


class LayoutManager:
    """Manages different layout configurations."""
    
    def __init__(self):
        self.layouts = self._initialize_layouts()
    
    def _initialize_layouts(self) -> Dict[str, LayoutConfig]:
        """Initialize all available layouts."""
        return {
            "hierarchical": LayoutConfig(
                layout_type=LayoutType.HIERARCHICAL,
                options={
                    "layout": {
                        "hierarchical": {
                            "direction": "UD",
                            "sortMethod": "directed",
                            "nodeSpacing": 100,
                            "levelSeparation": 150,
                            "treeSpacing": 200
                        }
                    },
                    "physics": {
                        "enabled": False
                    }
                },
                description="Traditional top-down hierarchical layout",
                best_for=["Documentation", "Organizational charts", "Process flows"]
            ),
            
            "radial": LayoutConfig(
                layout_type=LayoutType.RADIAL,
                options={
                    "layout": {
                        "hierarchical": {
                            "direction": "UD",
                            "sortMethod": "directed"
                        }
                    },
                    "physics": {
                        "enabled": True,
                        "solver": "forceAtlas2Based",
                        "forceAtlas2Based": {
                            "gravitationalConstant": -50,
                            "centralGravity": 0.01,
                            "springLength": 100,
                            "springConstant": 0.08,
                            "damping": 0.4,
                            "avoidOverlap": 1
                        },
                        "stabilization": {"iterations": 150}
                    }
                },
                description="Radial layout with central root node",
                best_for=["Brainstorming", "Concept maps", "Knowledge networks"]
            ),
            
            "tree": LayoutConfig(
                layout_type=LayoutType.TREE,
                options={
                    "layout": {
                        "hierarchical": {
                            "direction": "LR",
                            "sortMethod": "directed",
                            "nodeSpacing": 120,
                            "levelSeparation": 200
                        }
                    },
                    "physics": {
                        "enabled": False
                    }
                },
                description="Left-to-right tree layout",
                best_for=["Decision trees", "File structures", "Taxonomies"]
            ),
            
            "force_directed": LayoutConfig(
                layout_type=LayoutType.FORCE_DIRECTED,
                options={
                    "layout": {
                        "randomSeed": 2
                    },
                    "physics": {
                        "enabled": True,
                        "solver": "barnesHut",
                        "barnesHut": {
                            "gravitationalConstant": -2000,
                            "centralGravity": 0.3,
                            "springLength": 95,
                            "springConstant": 0.04,
                            "damping": 0.09,
                            "avoidOverlap": 0.1
                        },
                        "stabilization": {"iterations": 200}
                    }
                },
                description="Physics-based force-directed layout",
                best_for=["Network analysis", "Relationship mapping", "Complex structures"]
            ),
            
            "circular": LayoutConfig(
                layout_type=LayoutType.CIRCULAR,
                options={
                    "layout": {
                        "randomSeed": 1
                    },
                    "physics": {
                        "enabled": True,
                        "solver": "forceAtlas2Based",
                        "forceAtlas2Based": {
                            "gravitationalConstant": -26,
                            "centralGravity": 0.005,
                            "springLength": 230,
                            "springConstant": 0.18,
                            "damping": 0.15
                        },
                        "stabilization": {"iterations": 100}
                    }
                },
                description="Circular arrangement of nodes",
                best_for=["Cyclical processes", "Equal importance items", "Balanced views"]
            ),
            
            "timeline": LayoutConfig(
                layout_type=LayoutType.TIMELINE,
                options={
                    "layout": {
                        "hierarchical": {
                            "direction": "LR",
                            "sortMethod": "directed",
                            "nodeSpacing": 80,
                            "levelSeparation": 300,
                            "treeSpacing": 100
                        }
                    },
                    "physics": {
                        "enabled": False
                    }
                },
                description="Timeline-style horizontal layout",
                best_for=["Project timelines", "Historical events", "Sequential processes"]
            )
        }
    
    def get_layout(self, layout_name: str) -> LayoutConfig:
        """Get layout configuration by name."""
        return self.layouts.get(layout_name, self.layouts["hierarchical"])
    
    def get_available_layouts(self) -> Dict[str, str]:
        """Get all available layouts with descriptions."""
        return {
            name: config.description 
            for name, config in self.layouts.items()
        }
    
    def get_layout_options(self, layout_name: str, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get vis.js options for a specific layout."""
        layout_config = self.get_layout(layout_name)
        options = layout_config.options.copy()
        
        # Merge with custom configuration
        if custom_config:
            options = self._deep_merge(options, custom_config)
        
        return options
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_layout_specific_styles(self, layout_name: str) -> str:
        """Get CSS styles specific to a layout."""
        layout_styles = {
            "radial": """
                .vis-network {
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(240,240,240,0.3) 100%);
                }
            """,
            "circular": """
                .vis-network {
                    background: conic-gradient(from 0deg, rgba(255,255,255,0.1), rgba(240,240,240,0.2), rgba(255,255,255,0.1));
                }
            """,
            "timeline": """
                .vis-network {
                    background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(240,240,240,0.2) 50%, rgba(255,255,255,0.1) 100%);
                }
                .vis-network::before {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, transparent 0%, #ccc 20%, #ccc 80%, transparent 100%);
                    z-index: 0;
                }
            """,
            "force_directed": """
                .vis-network {
                    background: radial-gradient(ellipse at center, rgba(255,255,255,0.1) 0%, rgba(230,230,230,0.3) 100%);
                }
            """
        }
        
        return layout_styles.get(layout_name, "")
    
    def get_layout_recommendations(self, node_count: int, max_depth: int) -> List[str]:
        """Recommend layouts based on content characteristics."""
        recommendations = []
        
        if node_count <= 10:
            recommendations.extend(["radial", "circular"])
        elif node_count <= 30:
            recommendations.extend(["hierarchical", "tree", "radial"])
        else:
            recommendations.extend(["hierarchical", "force_directed"])
        
        if max_depth <= 3:
            recommendations.append("circular")
        elif max_depth >= 5:
            recommendations.extend(["hierarchical", "tree"])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(recommendations))


def create_layout_selector_html() -> str:
    """Create HTML for layout selection interface."""
    # This function is now deprecated - layout selection is handled by the settings panel
    return ""


def create_layout_javascript() -> str:
    """Create JavaScript functions for layout switching."""
    return """
    function changeLayout(layoutName) {
        if (!layoutName) return;
        
        // Get layout configuration
        var layoutConfigs = {
            'hierarchical': {
                layout: {
                    hierarchical: {
                        direction: "UD",
                        sortMethod: "directed",
                        nodeSpacing: 100,
                        levelSeparation: 150,
                        treeSpacing: 200
                    }
                },
                physics: { enabled: false }
            },
            'radial': {
                layout: {
                    hierarchical: {
                        direction: "UD",
                        sortMethod: "directed"
                    }
                },
                physics: {
                    enabled: true,
                    solver: "forceAtlas2Based",
                    forceAtlas2Based: {
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 100,
                        springConstant: 0.08,
                        damping: 0.4,
                        avoidOverlap: 1
                    },
                    stabilization: { iterations: 150 }
                }
            },
            'tree': {
                layout: {
                    hierarchical: {
                        direction: "LR",
                        sortMethod: "directed",
                        nodeSpacing: 120,
                        levelSeparation: 200
                    }
                },
                physics: { enabled: false }
            },
            'force_directed': {
                layout: { randomSeed: 2 },
                physics: {
                    enabled: true,
                    solver: "barnesHut",
                    barnesHut: {
                        gravitationalConstant: -2000,
                        centralGravity: 0.3,
                        springLength: 95,
                        springConstant: 0.04,
                        damping: 0.09,
                        avoidOverlap: 0.1
                    },
                    stabilization: { iterations: 200 }
                }
            },
            'circular': {
                layout: { randomSeed: 1 },
                physics: {
                    enabled: true,
                    solver: "forceAtlas2Based",
                    forceAtlas2Based: {
                        gravitationalConstant: -26,
                        centralGravity: 0.005,
                        springLength: 230,
                        springConstant: 0.18,
                        damping: 0.15
                    },
                    stabilization: { iterations: 100 }
                }
            },
            'timeline': {
                layout: {
                    hierarchical: {
                        direction: "LR",
                        sortMethod: "directed",
                        nodeSpacing: 80,
                        levelSeparation: 300,
                        treeSpacing: 100
                    }
                },
                physics: { enabled: false }
            }
        };
        
        var newOptions = layoutConfigs[layoutName];
        if (newOptions) {
            // Merge with existing options
            var mergedOptions = Object.assign({}, options, newOptions);
            
            // Apply new layout
            network.setOptions(mergedOptions);
            
            // Fit the network
            setTimeout(function() {
                network.fit();
            }, 500);
            
            console.log('Layout changed to:', layoutName);
        }
    }
    
    function getLayoutRecommendations() {
        var nodeCount = allNodes.length;
        var maxDepth = Math.max(...allNodes.get().map(node => node.level));
        
        var recommendations = [];
        
        if (nodeCount <= 10) {
            recommendations.push('radial', 'circular');
        } else if (nodeCount <= 30) {
            recommendations.push('hierarchical', 'tree', 'radial');
        } else {
            recommendations.push('hierarchical', 'force_directed');
        }
        
        if (maxDepth <= 3) {
            recommendations.push('circular');
        } else if (maxDepth >= 5) {
            recommendations.push('hierarchical', 'tree');
        }
        
        return [...new Set(recommendations)];
    }
    """