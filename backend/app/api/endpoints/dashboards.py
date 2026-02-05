"""
Dashboard configuration endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
from pathlib import Path

router = APIRouter()


class DashboardService:
    """Service to manage dashboard configurations"""
    
    def __init__(self, config_dir: str = "dashboards"):
        self.config_dir = Path(config_dir)
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all available dashboards"""
        dashboards = []
        
        if not self.config_dir.exists():
            return dashboards
        
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
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
            raise ValueError("Dashboard config directory not found")
        
        # Try to find dashboard file
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    config = json.load(f)
                    if config.get('id') == dashboard_id:
                        return config
            except Exception as e:
                print(f"Error loading dashboard {json_file}: {e}")
        
        raise ValueError(f"Dashboard '{dashboard_id}' not found")


dashboard_service = DashboardService()


@router.get("/dashboards")
async def list_dashboards():
    """
    List all available dashboards
    """
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
    """
    Get dashboard configuration by ID
    """
    try:
        config = dashboard_service.get_dashboard(dashboard_id)
        return config
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
