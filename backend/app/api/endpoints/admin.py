"""
Admin Management Endpoints
Full CRUD for dashboards, queries, and configurations
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import yaml
from pathlib import Path
from datetime import datetime

from app.core.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== PYDANTIC MODELS ====================

class DashboardCreateRequest(BaseModel):
    """Create new dashboard"""
    id: str
    title: str
    description: str
    globalFilters: Optional[List[Dict[str, Any]]] = []
    widgets: Optional[List[Dict[str, Any]]] = []


class DashboardUpdateRequest(BaseModel):
    """Update existing dashboard"""
    title: Optional[str] = None
    description: Optional[str] = None
    globalFilters: Optional[List[Dict[str, Any]]] = None
    widgets: Optional[List[Dict[str, Any]]] = None


class QueryCreateRequest(BaseModel):
    """Create new query"""
    id: str
    description: str
    sql: str
    parameters: Optional[List[Dict[str, Any]]] = []
    cache_ttl: Optional[int] = 300


class QueryUpdateRequest(BaseModel):
    """Update existing query"""
    description: Optional[str] = None
    sql: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    cache_ttl: Optional[int] = None


# ==================== DASHBOARD MANAGEMENT ====================

@router.post("/dashboards")
async def create_dashboard(dashboard: DashboardCreateRequest):
    """
    Create a new dashboard
    
    Creates a new JSON config file in the dashboards directory
    """
    try:
        dashboard_dir = Path(settings.DASHBOARD_CONFIG_DIR).resolve()
        dashboard_file = dashboard_dir / f"{dashboard.id}.json"
        
        # Check if already exists
        if dashboard_file.exists():
            raise HTTPException(status_code=409, detail=f"Dashboard '{dashboard.id}' already exists")
        
        # Create dashboard config
        config = {
            "id": dashboard.id,
            "title": dashboard.title,
            "description": dashboard.description,
            "globalFilters": dashboard.globalFilters or [],
            "widgets": dashboard.widgets or [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Save to file
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": f"Dashboard '{dashboard.id}' created successfully",
            "dashboard": config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dashboard: {str(e)}")


@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(dashboard_id: str, updates: DashboardUpdateRequest):
    """
    Update an existing dashboard
    
    Updates dashboard configuration (title, description, filters, widgets)
    """
    try:
        dashboard_dir = Path(settings.DASHBOARD_CONFIG_DIR).resolve()
        dashboard_file = dashboard_dir / f"{dashboard_id}.json"
        
        if not dashboard_file.exists():
            raise HTTPException(status_code=404, detail=f"Dashboard '{dashboard_id}' not found")
        
        # Read current config
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Apply updates
        if updates.title is not None:
            config['title'] = updates.title
        if updates.description is not None:
            config['description'] = updates.description
        if updates.globalFilters is not None:
            config['globalFilters'] = updates.globalFilters
        if updates.widgets is not None:
            config['widgets'] = updates.widgets
        
        config['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated config
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": f"Dashboard '{dashboard_id}' updated successfully",
            "dashboard": config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update dashboard: {str(e)}")


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """
    Delete a dashboard
    
    Removes the dashboard JSON file
    """
    try:
        dashboard_dir = Path(settings.DASHBOARD_CONFIG_DIR).resolve()
        dashboard_file = dashboard_dir / f"{dashboard_id}.json"
        
        if not dashboard_file.exists():
            raise HTTPException(status_code=404, detail=f"Dashboard '{dashboard_id}' not found")
        
        # Delete file
        dashboard_file.unlink()
        
        return {
            "success": True,
            "message": f"Dashboard '{dashboard_id}' deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dashboard: {str(e)}")


# ==================== QUERY MANAGEMENT ====================

@router.get("/queries")
async def list_all_queries():
    """
    List all queries from all YAML files
    
    Returns detailed information about each query including file location
    """
    try:
        queries_dir = Path("queries").resolve()
        all_queries = []
        
        for yaml_file in queries_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if 'queries' in content:
                    for query_id, query_config in content['queries'].items():
                        all_queries.append({
                            "id": query_id,
                            "description": query_config.get('description', ''),
                            "sql": query_config.get('sql', ''),
                            "parameters": query_config.get('parameters', []),
                            "cache_ttl": query_config.get('cache_ttl', 300),
                            "file": yaml_file.name
                        })
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
        
        return {
            "total": len(all_queries),
            "queries": all_queries
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list queries: {str(e)}")


@router.post("/queries")
async def create_query(query: QueryCreateRequest, file_name: str = "custom.yaml"):
    """
    Create a new query
    
    Adds query to specified YAML file (default: custom.yaml)
    """
    try:
        queries_dir = Path("queries").resolve()
        query_file = queries_dir / file_name
        
        # Load existing queries or create new file
        if query_file.exists():
            with open(query_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
        else:
            content = {}
        
        if 'queries' not in content:
            content['queries'] = {}
        
        # Check if query already exists
        if query.id in content['queries']:
            raise HTTPException(status_code=409, detail=f"Query '{query.id}' already exists in {file_name}")
        
        # Add new query
        content['queries'][query.id] = {
            "description": query.description,
            "sql": query.sql,
            "parameters": query.parameters or [],
            "cache_ttl": query.cache_ttl or 300
        }
        
        # Save to file
        with open(query_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        
        return {
            "success": True,
            "message": f"Query '{query.id}' created successfully in {file_name}",
            "query": content['queries'][query.id]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create query: {str(e)}")


@router.put("/queries/{query_id}")
async def update_query(query_id: str, updates: QueryUpdateRequest, file_name: Optional[str] = None):
    """
    Update an existing query
    
    If file_name not provided, searches all YAML files
    """
    try:
        queries_dir = Path("queries").resolve()
        
        # Find query in files
        query_file = None
        if file_name:
            query_file = queries_dir / file_name
            if not query_file.exists():
                raise HTTPException(status_code=404, detail=f"File '{file_name}' not found")
        else:
            # Search all files
            for yaml_file in queries_dir.glob("*.yaml"):
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f) or {}
                if 'queries' in content and query_id in content['queries']:
                    query_file = yaml_file
                    break
        
        if not query_file:
            raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found")
        
        # Load file
        with open(query_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f) or {}
        
        if query_id not in content.get('queries', {}):
            raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found in {query_file.name}")
        
        # Apply updates
        query_config = content['queries'][query_id]
        if updates.description is not None:
            query_config['description'] = updates.description
        if updates.sql is not None:
            query_config['sql'] = updates.sql
        if updates.parameters is not None:
            query_config['parameters'] = updates.parameters
        if updates.cache_ttl is not None:
            query_config['cache_ttl'] = updates.cache_ttl
        
        # Save
        with open(query_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        
        return {
            "success": True,
            "message": f"Query '{query_id}' updated successfully",
            "query": query_config
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update query: {str(e)}")


@router.delete("/queries/{query_id}")
async def delete_query(query_id: str, file_name: Optional[str] = None):
    """
    Delete a query
    
    Removes query from YAML file
    """
    try:
        queries_dir = Path("queries").resolve()
        
        # Find query
        query_file = None
        if file_name:
            query_file = queries_dir / file_name
        else:
            for yaml_file in queries_dir.glob("*.yaml"):
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f) or {}
                if 'queries' in content and query_id in content['queries']:
                    query_file = yaml_file
                    break
        
        if not query_file or not query_file.exists():
            raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found")
        
        # Load file
        with open(query_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f) or {}
        
        if query_id not in content.get('queries', {}):
            raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found")
        
        # Delete query
        del content['queries'][query_id]
        
        # Save
        with open(query_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        
        return {
            "success": True,
            "message": f"Query '{query_id}' deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete query: {str(e)}")


# ==================== FILE UPLOAD ====================

@router.post("/queries/upload")
async def upload_query_file(file: UploadFile = File(...)):
    """
    Upload a YAML query file
    
    Validates and saves the YAML file to queries directory
    """
    try:
        if not file.filename.endswith('.yaml') and not file.filename.endswith('.yml'):
            raise HTTPException(status_code=400, detail="File must be a YAML file (.yaml or .yml)")
        
        # Read and validate
        content = await file.read()
        try:
            yaml_data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
        
        if 'queries' not in yaml_data:
            raise HTTPException(status_code=400, detail="YAML must contain 'queries' key")
        
        # Save file
        queries_dir = Path("queries").resolve()
        file_path = queries_dir / file.filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Query file '{file.filename}' uploaded successfully",
            "queries_count": len(yaml_data['queries'])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/dashboards/upload")
async def upload_dashboard_file(file: UploadFile = File(...)):
    """
    Upload a dashboard JSON file
    
    Validates and saves the JSON file to dashboards directory
    """
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be a JSON file (.json)")
        
        # Read and validate
        content = await file.read()
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        if 'id' not in json_data or 'title' not in json_data:
            raise HTTPException(status_code=400, detail="JSON must contain 'id' and 'title' fields")
        
        # Save file
        dashboard_dir = Path(settings.DASHBOARD_CONFIG_DIR).resolve()
        file_path = dashboard_dir / file.filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Dashboard file '{file.filename}' uploaded successfully",
            "dashboard_id": json_data['id']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
