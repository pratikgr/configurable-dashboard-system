"""
Dashboard configuration endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from app.core.config import settings

router = APIRouter()


class WidgetCreateRequest(BaseModel):
    """Request to add a widget to a dashboard"""
    id: str
    type: str
    title: str
    queryId: str
    position: Dict[str, int]
    dataMapping: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    chartOptions: Optional[Dict[str, Any]] = None
    columns: Optional[list] = None


class DashboardService:
    """Service to manage dashboard configurations"""
    
    def __init__(self):
        # Use configurable path from settings
        self.config_dir = Path(settings.DASHBOARD_CONFIG_DIR).resolve()
        
        print(f"📂 Dashboard config directory: {self.config_dir}")
        print(f"📂 Directory exists: {self.config_dir.exists()}")
        
        if self.config_dir.exists():
            json_files = list(self.config_dir.glob("*.json"))
            print(f"📂 Found {len(json_files)} dashboard file(s)")
            for f in json_files:
                print(f"   - {f.name}")
        else:
            print(f"⚠️  Dashboard directory not found. Please check DASHBOARD_CONFIG_DIR in .env")
            print(f"   Current value: {settings.DASHBOARD_CONFIG_DIR}")
            print(f"   Resolved to: {self.config_dir}")
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all available dashboards"""
        dashboards = []
        
        if not self.config_dir.exists():
            print(f"❌ Config directory does not exist: {self.config_dir}")
            return dashboards
        
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    dashboards.append({
                        "id": config.get('id'),
                        "title": config.get('title'),
                        "description": config.get('description', ''),
                        "file": json_file.name
                    })
            except Exception as e:
                print(f"Error loading dashboard {json_file}: {e}")
        
        return dashboards
    
    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard configuration by ID"""
        if not self.config_dir.exists():
            raise ValueError(f"Dashboard config directory not found: {self.config_dir}")
        
        # Try to find dashboard file
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('id') == dashboard_id:
                        return config
            except Exception as e:
                print(f"Error loading dashboard {json_file}: {e}")
        
        raise ValueError(f"Dashboard '{dashboard_id}' not found")
    
    def get_dashboard_file_path(self, dashboard_id: str) -> Path:
        """Get the file path for a dashboard"""
        if not self.config_dir.exists():
            raise ValueError(f"Dashboard config directory not found: {self.config_dir}")
        
        # Try to find dashboard file
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('id') == dashboard_id:
                        print(f"✅ Found dashboard file: {json_file}")
                        return json_file
            except Exception as e:
                print(f"Error loading dashboard {json_file}: {e}")
        
        raise ValueError(f"Dashboard file for '{dashboard_id}' not found")
    
    def add_widget_to_dashboard(self, dashboard_id: str, widget: Dict[str, Any]) -> Dict[str, Any]:
        """Add a widget to a dashboard configuration"""
        # Get dashboard file path
        dashboard_file = self.get_dashboard_file_path(dashboard_id)
        
        print(f"📝 Adding widget to: {dashboard_file}")
        
        # Read current config
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Add widget
        if 'widgets' not in config:
            config['widgets'] = []
        
        config['widgets'].append(widget)
        
        # Save updated config
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Widget '{widget['id']}' saved successfully")
        
        return {"success": True, "widget_id": widget['id']}


dashboard_service = DashboardService()


@router.get("/dashboards")
async def list_dashboards():
    """List all available dashboards"""
    try:
        dashboards = dashboard_service.list_dashboards()
        return {
            "total": len(dashboards),
            "dashboards": dashboards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard configuration by ID"""
    try:
        config = dashboard_service.get_dashboard(dashboard_id)
        return config
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/{dashboard_id}/widget")
async def add_widget_to_dashboard(
    dashboard_id: str,
    widget: WidgetCreateRequest
):
    """
    Add a widget to a dashboard configuration
    Saves to the JSON file
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 Received request to add widget to '{dashboard_id}'")
        print(f"📦 Widget ID: {widget.id}")
        print(f"📦 Widget Type: {widget.type}")
        print(f"{'='*60}\n")
        
        # Convert to dict
        widget_dict = widget.dict(exclude_none=True)
        
        # Add to dashboard
        result = dashboard_service.add_widget_to_dashboard(dashboard_id, widget_dict)
        
        return {
            "success": True,
            "message": "Widget added successfully",
            "widget_id": widget.id
        }
    
    except ValueError as e:
        print(f"❌ ValueError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save widget: {str(e)}")
    
@router.delete("/dashboard/{dashboard_id}/widget/{widget_id}")
async def delete_widget_from_dashboard(
    dashboard_id: str,
    widget_id: str
):
    """Delete a widget from a dashboard"""
    try:
        dashboard_file = dashboard_service.get_dashboard_file_path(dashboard_id)
        
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Remove widget
        if 'widgets' in config:
            config['widgets'] = [w for w in config['widgets'] if w.get('id') != widget_id]
        
        # Save
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "message": "Widget deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete widget: {str(e)}")