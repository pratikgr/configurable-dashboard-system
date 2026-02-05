"""
Universal Query Executor
Executes any SQL query defined in YAML configuration files
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil import parser as date_parser

from app.core.config import settings


class QueryExecutor:
    """
    Universal query executor that loads YAML configurations
    and executes SQL queries dynamically
    """
    
    def __init__(self, queries_dir: str = "queries"):
        self.queries_dir = Path(queries_dir)
        self.queries: Dict[str, Dict[str, Any]] = {}
        self._load_all_queries()
    
    def _load_all_queries(self):
        """Load all YAML query definitions from queries directory"""
        if not self.queries_dir.exists():
            print(f"⚠️  Queries directory not found: {self.queries_dir}")
            return
        
        for yaml_file in self.queries_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'queries' in config:
                        self.queries.update(config['queries'])
                        print(f"✅ Loaded queries from: {yaml_file.name}")
            except Exception as e:
                print(f"❌ Error loading {yaml_file}: {e}")
        
        print(f"📊 Total queries loaded: {len(self.queries)}")
    
    def reload_queries(self):
        """Reload all query configurations"""
        self.queries = {}
        self._load_all_queries()
    
    def get_query_config(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Get query configuration by ID"""
        return self.queries.get(query_id)
    
    def list_queries(self) -> List[str]:
        """List all available query IDs"""
        return list(self.queries.keys())
    
    def _resolve_parameter_value(self, param_config: Dict[str, Any], provided_value: Any) -> Any:
        """
        Resolve parameter value with smart defaults
        """
        param_type = param_config.get('type', 'string')
        param_default = param_config.get('default')
        
        # Use provided value if available
        if provided_value is not None:
            value = provided_value
        elif param_default is not None:
            value = param_default
        else:
            return None
        
        # Type conversion and smart defaults
        if param_type == 'date':
            return self._resolve_date(value)
        elif param_type == 'int':
            return int(value)
        elif param_type == 'float':
            return float(value)
        elif param_type == 'bool':
            return str(value).lower() in ('true', '1', 'yes')
        
        return value
    
    def _resolve_date(self, value: Any) -> str:
        """
        Resolve date with smart defaults like 'today', '30_days_ago'
        """
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        
        value_str = str(value).lower()
        now = datetime.now()
        
        # Smart date shortcuts
        date_shortcuts = {
            'today': now,
            'yesterday': now - timedelta(days=1),
            'tomorrow': now + timedelta(days=1),
            '7_days_ago': now - timedelta(days=7),
            '30_days_ago': now - timedelta(days=30),
            '90_days_ago': now - timedelta(days=90),
            'start_of_month': now.replace(day=1),
            'start_of_year': now.replace(month=1, day=1),
        }
        
        if value_str in date_shortcuts:
            return date_shortcuts[value_str].strftime('%Y-%m-%d')
        
        # Try parsing as date string
        try:
            parsed_date = date_parser.parse(value_str)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            return value_str
    
    async def execute(
        self,
        query_id: str,
        params: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Execute a query by ID with parameters
        
        Args:
            query_id: Unique query identifier
            params: Query parameters
            db: Database session
            
        Returns:
            Dictionary with query results and metadata
        """
        if query_id not in self.queries:
            raise ValueError(f"Query '{query_id}' not found")
        
        query_config = self.queries[query_id]
        sql = query_config['sql']
        param_configs = query_config.get('parameters', [])
        
        # Resolve all parameters
        resolved_params = {}
        for param_config in param_configs:
            param_name = param_config['name']
            provided_value = params.get(param_name) if params else None
            resolved_params[param_name] = self._resolve_parameter_value(
                param_config, 
                provided_value
            )
        
        # Execute query
        try:
            start_time = datetime.now()
            
            result = await db.execute(
                text(sql),
                resolved_params
            )
            
            # Fetch results
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "query_id": query_id,
                "data": data,
                "row_count": len(data),
                "columns": list(columns),
                "execution_time_ms": round(execution_time * 1000, 2),
                "parameters": resolved_params,
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")


# Global query executor instance
query_executor = QueryExecutor()
