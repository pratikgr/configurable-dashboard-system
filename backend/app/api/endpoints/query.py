"""
Query execution endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.query_executor import query_executor


router = APIRouter()


class QueryExecuteRequest(BaseModel):
    """Request model for query execution"""
    query_id: str
    parameters: Optional[Dict[str, Any]] = None


class QueryExecuteResponse(BaseModel):
    """Response model for query execution"""
    query_id: str
    data: List[Dict[str, Any]]
    row_count: int
    columns: List[str]
    execution_time_ms: float
    parameters: Dict[str, Any]
    executed_at: str


@router.post("/query/execute", response_model=QueryExecuteResponse)
async def execute_query(
    request: QueryExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a query by ID with optional parameters
    
    Example:
    ```json
    {
        "query_id": "sales_overview",
        "parameters": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    }
    ```
    """
    try:
        result = await query_executor.execute(
            query_id=request.query_id,
            params=request.parameters,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/list")
async def list_queries():
    """
    List all available queries
    """
    queries = query_executor.list_queries()
    query_details = []
    
    for query_id in queries:
        config = query_executor.get_query_config(query_id)
        query_details.append({
            "query_id": query_id,
            "parameters": config.get('parameters', []),
            "cache_ttl": config.get('cache_ttl'),
            "description": config.get('description', '')
        })
    
    return {
        "total": len(queries),
        "queries": query_details
    }


@router.get("/query/{query_id}")
async def get_query_info(query_id: str):
    """
    Get information about a specific query
    """
    config = query_executor.get_query_config(query_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Query '{query_id}' not found")
    
    return {
        "query_id": query_id,
        "sql": config.get('sql'),
        "parameters": config.get('parameters', []),
        "cache_ttl": config.get('cache_ttl'),
        "description": config.get('description', '')
    }


@router.post("/query/reload")
async def reload_queries():
    """
    Reload all query configurations from YAML files
    (useful during development)
    """
    try:
        query_executor.reload_queries()
        return {
            "message": "Queries reloaded successfully",
            "total_queries": len(query_executor.list_queries())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
