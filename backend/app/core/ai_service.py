"""
AI Service for Azure OpenAI Integration
Provides natural language dashboard building and data analysis capabilities
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.core.config import settings
from app.core.query_executor import query_executor


# ══════════════════════════════════════════════════════════════
# Azure OpenAI Client Initialization
# ══════════════════════════════════════════════════════════════

def _initialize_client() -> AzureOpenAI:
    """
    Initialize Azure OpenAI client with automatic authentication
    Supports both API key (local/dev) and Managed Identity (production)
    """
    # If API key is provided, use it (local/dev environments)
    if settings.AZURE_OPENAI_API_KEY:
        return AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            timeout=60.0,
            max_retries=2
        )
    
    # Otherwise use Managed Identity (production)
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    
    return AzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=token.token,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        timeout=60.0,
        max_retries=2
    )


# Global client instance
client = _initialize_client()


# ══════════════════════════════════════════════════════════════
# System Prompt: Dual-mode behavior
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are an intelligent dashboard assistant with two distinct modes:

**MODE 1: DASHBOARD BUILDER**
When the user wants to ADD, CREATE, or BUILD a permanent widget:
- Call list_queries() to find available queries
- Call get_query_schema() to understand the data structure
- Call create_widget() to generate the widget configuration
- These widgets are PERMANENT and show ALL data (no filtering by default)
- Only use global date range filters if the dashboard has them

**MODE 2: DATA ANALYST**
When the user asks to SHOW, GET, or VIEW specific data:
- Call list_queries() to find the right query
- Call get_query_schema() to see required parameters
- Extract parameter values from the user's natural language request
- Call execute_query_preview() with those parameters
- Display results as a formatted table in the chat
- Ask: "Would you like to add this as a permanent widget?"

**PARAMETER EXTRACTION RULES:**
1. Explicit IDs: "customer 42" → {customer_id: 42}
2. Dates: "last 30 days" → calculate and pass as ISO format
3. Categories: "Electronics" → {category: "Electronics"}
4. Ambiguous values: ASK the user for clarification - never guess
5. Missing required parameters: ASK the user to provide them

**DECISION LOGIC:**
- "Add a bar chart" = Mode 1 (Dashboard Builder)
- "Show me customer 42" = Mode 2 (Data Analyst)
- "Create a widget for..." = Mode 1
- "What are the top 5..." = Mode 2

**CRITICAL FORMATTING RULES - YOU MUST FOLLOW EXACTLY:**

1. NUMBERED LISTS - Use this exact format:
   
   1. First item here
   2. Second item here
   3. Third item here
   
   Rules:
   - Start number on new line
   - Always put space after period: "1. " not "1."
   - Never use bullets with numbers
   - Put blank line before and after list

2. PARAGRAPHS:
   - Separate paragraphs with blank line
   - Keep sentences in same paragraph together
   
3. QUESTIONS:
   - Put questions on new line after lists
   - Blank line before question

4. NEVER use these patterns:
   - "* 1." (bullet + number)
   - "1.text" (no space after period)
   - "text1." (number without line break)

**GOOD EXAMPLE:**
Here are the queries:

1. sales_overview: Get sales data
2. revenue_by_region: Get revenue data

What would you like to do?

**BAD EXAMPLE:**
Here are the queries:* 1.sales_overview: Get sales data2.revenue_by_region: Get revenue data What would you like to do?

**WIDGET TYPES:**
- line-chart: needs {x: field, y: field}
- bar-chart: needs {x: field, y: field}
- pie-chart: needs {name: field, value: field}
- data-table: needs columns array
- metric-card: needs {value: field} with optional aggregation

Always call list_queries() first to understand available data sources.
Always format your responses with proper line breaks and spacing."""

# ══════════════════════════════════════════════════════════════
# Tool Definitions (4 tools)
# ══════════════════════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_queries",
            "description": "Returns all available query IDs with descriptions and parameters. Always call this first.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_query_schema",
            "description": "Returns detailed schema for a specific query including column names, data types, and parameter definitions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "The query ID from list_queries()"
                    }
                },
                "required": ["query_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_query_preview",
            "description": "Execute a query with specific parameter values and return first 5 rows. Use this when user asks about specific entities (customer 42, last 30 days, etc). Parameters must match the query's parameter definitions exactly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "The query ID to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Key-value pairs matching the query's parameter names. Keys must be exact matches from get_query_schema().",
                        "additionalProperties": True
                    }
                },
                "required": ["query_id", "parameters"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_widget",
            "description": "Creates a validated widget configuration for the dashboard. Use this when the user wants to ADD or CREATE a permanent widget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["line-chart", "bar-chart", "pie-chart", "data-table", "metric-card"],
                        "description": "The widget type"
                    },
                    "title": {
                        "type": "string",
                        "description": "Display title for the widget"
                    },
                    "queryId": {
                        "type": "string",
                        "description": "Query ID from list_queries()"
                    },
                    "dataMapping": {
                        "type": "object",
                        "description": "Maps query columns to widget fields. For line/bar: {x: field, y: field}. For pie: {name: field, value: field}. For metric: {value: field}",
                        "properties": {
                            "x": {"type": "string"},
                            "y": {"type": "string"},
                            "name": {"type": "string"},
                            "value": {"type": "string"}
                        }
                    },
                    "columns": {
                        "type": "array",
                        "description": "For data-table only: array of column definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "header": {"type": "string"},
                                "sortable": {"type": "boolean"}
                            }
                        }
                    },
                    "chartOptions": {
                        "type": "object",
                        "description": "Optional chart styling options",
                        "properties": {
                            "colors": {"type": "array", "items": {"type": "string"}},
                            "smooth": {"type": "boolean"},
                            "showArea": {"type": "boolean"}
                        }
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters to pre-filter the widget data"
                    }
                },
                "required": ["type", "title", "queryId"]
            }
        }
    }
]


# ══════════════════════════════════════════════════════════════
# Tool Execution Functions
# ══════════════════════════════════════════════════════════════

async def execute_tool(
    name: str,
    arguments: dict,
    db: Any = None
) -> Dict[str, Any]:
    """
    Execute a tool call from the AI model
    
    Args:
        name: Tool function name
        arguments: Tool arguments from AI
        db: Database session (for execute_query_preview)
    
    Returns:
        Tool result as dictionary
    """
    
    print(f"\n{'='*60}")
    print(f"🔧 Executing Tool: {name}")
    print(f"📝 Arguments: {arguments}")
    
    try:
        if name == "list_queries":
            result = _execute_list_queries()
            print(f"✅ Result: {len(result.get('queries', []))} queries found")
            return result
        
        elif name == "get_query_schema":
            result = _execute_get_query_schema(arguments["query_id"])
            print(f"✅ Result: Schema retrieved")
            return result
        
        elif name == "execute_query_preview":
            if not db:
                print("❌ Error: Database session required")
                return {"error": "Database session required for query execution"}
            result = await _execute_query_preview(
                arguments["query_id"],
                arguments.get("parameters", {}),
                db
            )
            print(f"✅ Result: Query executed, {result.get('total_rows', 0)} rows")
            return result
        
        elif name == "create_widget":
            result = _execute_create_widget(arguments)
            print(f"✅ Result: Widget created")
            return result
        
        else:
            print(f"❌ Error: Unknown tool: {name}")
            return {"error": f"Unknown tool: {name}"}
    
    except Exception as e:
        print(f"❌ Tool execution error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e) if str(e) else "Unknown error in tool execution"}
    finally:
        print(f"{'='*60}\n")


def _execute_list_queries() -> Dict[str, Any]:
    """Tool: list_queries() - return all available queries"""
    try:
        queries = query_executor.list_queries()
        
        result = []
        for query_id in queries:
            try:
                config = query_executor.get_query_config(query_id)
                if config:
                    result.append({
                        "query_id": query_id,
                        "description": config.get("description", "No description"),
                        "parameters": config.get("parameters", [])
                    })
            except Exception as e:
                print(f"Warning: Error loading config for {query_id}: {e}")
                result.append({
                    "query_id": query_id,
                    "description": f"Query: {query_id}",
                    "parameters": []
                })
        
        return {
            "total": len(result),
            "queries": result
        }
    
    except Exception as e:
        print(f"Error in list_queries: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e) if str(e) else "Failed to list queries",
            "total": 0,
            "queries": []
        }


def _execute_get_query_schema(query_id: str) -> Dict[str, Any]:
    """Tool: get_query_schema() - return query columns and parameters"""
    try:
        config = query_executor.get_query_config(query_id)
        
        if not config:
            return {"error": f"Query '{query_id}' not found"}
        
        # Extract column names from SQL
        columns = _extract_columns_from_sql(config.get("sql", ""))
        
        return {
            "query_id": query_id,
            "description": config.get("description", ""),
            "parameters": config.get("parameters", []),
            "columns": columns,
            "cache_ttl": config.get("cache_ttl")
        }
    
    except Exception as e:
        print(f"Error in get_query_schema for {query_id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e) if str(e) else "Failed to get query schema",
            "query_id": query_id
        }


async def _execute_query_preview(
    query_id: str,
    parameters: Dict[str, Any],
    db: Any
) -> Dict[str, Any]:
    """Tool: execute_query_preview() - run query with parameters and return preview"""
    try:
        result = await query_executor.execute(
            query_id=query_id,
            params=parameters,
            db=db
        )
        
        # Return only first 5 rows to keep token usage low
        return {
            "query_id": query_id,
            "parameters_used": parameters,
            "data": result["data"][:5],
            "total_rows": result["row_count"],
            "columns": result["columns"],
            "showing": f"First 5 of {result['row_count']} rows",
            "execution_time_ms": result.get("execution_time_ms", 0)
        }
    
    except ValueError as e:
        return {"error": f"Query error: {str(e)}"}
    except Exception as e:
        print(f"Error executing query preview: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Execution failed: {str(e)}"}


def _execute_create_widget(config: Dict[str, Any]) -> Dict[str, Any]:
    """Tool: create_widget() - validate and return widget configuration"""
    try:
        from app.core.widget_validator import validate_widget
        validated = validate_widget(config)
        return validated
    
    except ValueError as e:
        return {"error": f"Invalid widget configuration: {str(e)}"}
    except Exception as e:
        print(f"Error creating widget: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Widget creation failed: {str(e)}"}


# ══════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════

def _extract_columns_from_sql(sql: str) -> List[Dict[str, str]]:
    """
    Extract column names and aliases from SQL SELECT statement
    """
    if not sql or not sql.strip():
        return [{"name": "data", "type": "unknown"}]
    
    try:
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Find SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return [{"name": "data", "type": "unknown"}]
        
        select_clause = select_match.group(1).strip()
        
        # Split by commas (simplified)
        parts = select_clause.split(',')
        
        columns = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Look for AS alias
            as_match = re.search(r'\s+[aA][sS]\s+(\w+)\s*$', part)
            if as_match:
                col_name = as_match.group(1)
            else:
                # Extract last word
                cleaned = re.sub(r'\([^)]*\)', '', part)
                words = re.findall(r'\w+', cleaned)
                col_name = words[-1] if words else 'column'
            
            columns.append({
                "name": col_name,
                "type": "unknown"
            })
        
        return columns if columns else [{"name": "data", "type": "unknown"}]
    
    except Exception as e:
        print(f"Error parsing SQL: {e}")
        return [{"name": "data", "type": "unknown"}]


# ══════════════════════════════════════════════════════════════
# Main Chat Function (used by endpoint)
# ══════════════════════════════════════════════════════════════

async def create_chat_stream(
    message: str,
    conversation_history: List[Dict[str, Any]],
    dashboard_id: str,
    db: Any = None
):
    """
    Create streaming chat completion with tool use
    
    This is an async generator that yields SSE events
    """
    
    print(f"\n{'*'*60}")
    print(f"🚀 New Chat Request")
    print(f"Message: {message}")
    print(f"Dashboard: {dashboard_id}")
    print(f"{'*'*60}\n")
    
    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})
    
    # Agentic loop: keep calling API until no more tool calls
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        try:
            # Call Azure OpenAI with streaming
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=True,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE
            )
            
            # Accumulate response
            text_buffer = ""
            tool_calls_dict = {}
            
            # Stream chunks
            for chunk in response:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason
                
                # Stream text content
                if delta.content:
                    # IMPORTANT: Add the content exactly as received
                    # Azure OpenAI should include spaces in delta.content
                    # DEBUG: Print what we're receiving
                    print(f"📨 Streaming chunk: '{delta.content}' (length: {len(delta.content)})")
                    text_buffer += delta.content
                    
                    # Yield each chunk
                    yield {
                        "event": "text",
                        "data": delta.content  # This should include spaces
                    }
                
                # Accumulate tool calls
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_dict:
                            tool_calls_dict[idx] = {
                                "id": tc_delta.id or f"call_{idx}",
                                "type": "function",
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            }
                        
                        if tc_delta.id:
                            tool_calls_dict[idx]["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_dict[idx]["function"]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_dict[idx]["function"]["arguments"] += tc_delta.function.arguments
                
                    if finish_reason:
                        break
            # Convert tool calls dict to list
            tool_calls = list(tool_calls_dict.values()) if tool_calls_dict else []
            
            # Build message for history
            current_message = {
                "role": "assistant",
                "content": text_buffer or ""
            }
            
            if tool_calls:
                current_message["tool_calls"] = tool_calls
            
            messages.append(current_message)
            
            # If no tool calls, we're done
            if not tool_calls:
                print("✅ No tool calls - conversation complete")
                yield {"event": "done", "data": ""}
                break
            
            # Execute tool calls
            print(f"\n📞 Executing {len(tool_calls)} tool call(s)...")
            
            for tc in tool_calls:
                func_name = tc["function"]["name"]
                func_args_str = tc["function"]["arguments"]
                
                print(f"\n🔧 Tool: {func_name}")
                print(f"📝 Raw args: {func_args_str[:100]}...")
                
                try:
                    func_args = json.loads(func_args_str) if func_args_str else {}
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    func_args = {}
                
                # Execute tool
                tool_result = await execute_tool(func_name, func_args, db)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tool_result)
                })
                
                # Emit special events
                if func_name == "create_widget" and "error" not in tool_result:
                    yield {
                        "event": "widget",
                        "data": json.dumps(tool_result)
                    }
                
                if func_name == "execute_query_preview" and "error" not in tool_result:
                    yield {
                        "event": "data",
                        "data": json.dumps({
                            "query_id": tool_result.get("query_id"),
                            "rows": tool_result.get("data", []),
                            "total": tool_result.get("total_rows", 0),
                            "columns": tool_result.get("columns", [])
                        })
                    }
        
        except Exception as e:
            print(f"❌ Error in chat stream: {e}")
            import traceback
            traceback.print_exc()
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e) if str(e) else "Unknown error occurred"})
            }
            break
    
    # Safety: max iterations reached
    if iteration >= max_iterations:
        print("⚠️ Max iterations reached")
        yield {
            "event": "error",
            "data": json.dumps({"error": "Maximum iterations reached"})
        }
