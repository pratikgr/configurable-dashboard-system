"""
Widget Configuration Validator
Validates widget configurations before they're added to dashboards
"""
import uuid
from typing import Dict, Any, List
from datetime import datetime


def validate_widget(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and enrich a widget configuration
    
    Args:
        config: Widget configuration from AI
    
    Returns:
        Validated and enriched widget config with:
        - Unique ID
        - Default position
        - Validated structure
    
    Raises:
        ValueError: If configuration is invalid
    """
    
    # Required fields
    if "type" not in config:
        raise ValueError("Widget type is required")
    
    if "title" not in config:
        raise ValueError("Widget title is required")
    
    if "queryId" not in config:
        raise ValueError("Widget queryId is required")
    
    # Validate type
    valid_types = ["line-chart", "bar-chart", "pie-chart", "data-table", "metric-card"]
    if config["type"] not in valid_types:
        raise ValueError(f"Invalid widget type. Must be one of: {', '.join(valid_types)}")
    
    # Type-specific validation
    widget_type = config["type"]
    
    if widget_type in ["line-chart", "bar-chart"]:
        _validate_chart_widget(config)
    elif widget_type == "pie-chart":
        _validate_pie_widget(config)
    elif widget_type == "data-table":
        _validate_table_widget(config)
    elif widget_type == "metric-card":
        _validate_metric_widget(config)
    
    # Generate unique ID if not provided
    if "id" not in config:
        config["id"] = _generate_widget_id(config["type"])
    
    # Add default position if not provided
    if "position" not in config:
        config["position"] = _get_default_position(config["type"])
    
    # Add metadata
    config["created_at"] = datetime.utcnow().isoformat()
    config["created_by"] = "ai_assistant"
    
    return config


def _validate_chart_widget(config: Dict[str, Any]) -> None:
    """Validate line-chart or bar-chart configuration"""
    if "dataMapping" not in config:
        raise ValueError(f"{config['type']} requires dataMapping")
    
    mapping = config["dataMapping"]
    
    if "x" not in mapping:
        raise ValueError(f"{config['type']} dataMapping requires 'x' field")
    
    if "y" not in mapping:
        raise ValueError(f"{config['type']} dataMapping requires 'y' field")
    
    # Validate x and y are strings
    if not isinstance(mapping["x"], str):
        raise ValueError("dataMapping.x must be a string (column name)")
    
    if not isinstance(mapping["y"], str):
        raise ValueError("dataMapping.y must be a string (column name)")


def _validate_pie_widget(config: Dict[str, Any]) -> None:
    """Validate pie-chart configuration"""
    if "dataMapping" not in config:
        raise ValueError("pie-chart requires dataMapping")
    
    mapping = config["dataMapping"]
    
    if "name" not in mapping:
        raise ValueError("pie-chart dataMapping requires 'name' field")
    
    if "value" not in mapping:
        raise ValueError("pie-chart dataMapping requires 'value' field")
    
    # Validate types
    if not isinstance(mapping["name"], str):
        raise ValueError("dataMapping.name must be a string (column name)")
    
    if not isinstance(mapping["value"], str):
        raise ValueError("dataMapping.value must be a string (column name)")


def _validate_table_widget(config: Dict[str, Any]) -> None:
    """Validate data-table configuration"""
    # Columns can be auto-generated from query schema, so not strictly required
    # But if provided, validate structure
    if "columns" in config:
        columns = config["columns"]
        
        if not isinstance(columns, list):
            raise ValueError("columns must be an array")
        
        if len(columns) == 0:
            raise ValueError("columns array cannot be empty if provided")
        
        for i, col in enumerate(columns):
            if not isinstance(col, dict):
                raise ValueError(f"Column {i} must be an object")
            
            if "field" not in col:
                raise ValueError(f"Column {i} missing 'field' property")
            
            if "header" not in col:
                # Auto-generate header from field name
                col["header"] = col["field"].replace("_", " ").title()
            
            # Set defaults
            if "sortable" not in col:
                col["sortable"] = True
            
            if "align" not in col:
                col["align"] = "left"


def _validate_metric_widget(config: Dict[str, Any]) -> None:
    """Validate metric-card configuration"""
    if "dataMapping" not in config:
        raise ValueError("metric-card requires dataMapping")
    
    mapping = config["dataMapping"]
    
    if "value" not in mapping:
        raise ValueError("metric-card dataMapping requires 'value' field")
    
    if not isinstance(mapping["value"], str):
        raise ValueError("dataMapping.value must be a string (field or aggregation)")
    
    # Set defaults
    if "format" not in config:
        config["format"] = {"type": "number"}
    
    if "icon" not in config:
        config["icon"] = "chart"
    
    if "color" not in config:
        config["color"] = "blue"


def _generate_widget_id(widget_type: str) -> str:
    """Generate unique widget ID"""
    # Format: type_uuid (e.g., line_chart_a1b2c3d4)
    type_prefix = widget_type.replace("-", "_")
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{type_prefix}_{unique_suffix}"


def _get_default_position(widget_type: str) -> Dict[str, int]:
    """
    Get default grid position based on widget type
    These are sensible defaults - frontend should override based on actual layout
    """
    defaults = {
        "metric-card": {"x": 0, "y": 0, "w": 3, "h": 2},
        "line-chart": {"x": 0, "y": 2, "w": 8, "h": 4},
        "bar-chart": {"x": 0, "y": 2, "w": 6, "h": 4},
        "pie-chart": {"x": 6, "y": 2, "w": 6, "h": 4},
        "data-table": {"x": 0, "y": 6, "w": 12, "h": 4}
    }
    
    return defaults.get(widget_type, {"x": 0, "y": 0, "w": 6, "h": 4})


def validate_widget_update(widget_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate updates to an existing widget
    
    Args:
        widget_id: ID of widget being updated
        updates: Partial widget configuration with updates
    
    Returns:
        Validated updates
    
    Raises:
        ValueError: If updates are invalid
    """
    
    # Cannot change type or queryId of existing widget
    forbidden_fields = ["type", "queryId", "id", "created_at", "created_by"]
    
    for field in forbidden_fields:
        if field in updates:
            raise ValueError(f"Cannot modify '{field}' of existing widget")
    
    # Validate position if provided
    if "position" in updates:
        pos = updates["position"]
        required_pos_fields = ["x", "y", "w", "h"]
        
        for field in required_pos_fields:
            if field not in pos:
                raise ValueError(f"position.{field} is required")
            
            if not isinstance(pos[field], int):
                raise ValueError(f"position.{field} must be an integer")
            
            if pos[field] < 0:
                raise ValueError(f"position.{field} cannot be negative")
    
    # Add update metadata
    updates["updated_at"] = datetime.utcnow().isoformat()
    updates["updated_by"] = "user"
    
    return updates


def merge_widget_config(
    base_config: Dict[str, Any],
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge widget updates into base configuration
    
    Args:
        base_config: Original widget configuration
        updates: Updates to apply
    
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in updates.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            # Deep merge for nested objects
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    
    return merged
