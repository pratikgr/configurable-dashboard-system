"""
AI Chat API Endpoint
Server-Sent Events (SSE) streaming endpoint for AI-powered dashboard building
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import get_db
from app.core.ai_service import create_chat_stream


router = APIRouter()


# ══════════════════════════════════════════════════════════════
# Request/Response Models
# ══════════════════════════════════════════════════════════════

class Message(BaseModel):
    """Single message in conversation"""
    role: str = Field(..., description="Message role: user, assistant, or tool")
    content: str = Field(..., description="Message content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tool calls made by assistant"
    )


class ChatRequest(BaseModel):
    """AI chat request"""
    message: str = Field(..., description="User's message")
    dashboard_id: str = Field(..., description="Current dashboard context")
    conversation_history: List[Message] = Field(
        default=[],
        description="Previous messages in conversation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Show me details for customer 42",
                "dashboard_id": "sales-dashboard",
                "conversation_history": []
            }
        }


class ChatStreamEvent(BaseModel):
    """Single SSE event"""
    event: str = Field(..., description="Event type: text, widget, data, error, done")
    data: str = Field(..., description="Event data (may be JSON string)")


# ══════════════════════════════════════════════════════════════
# Endpoints
# ══════════════════════════════════════════════════════════════

@router.post(
    "/ai/chat",
    response_class=StreamingResponse,
    summary="AI Chat with Dashboard Assistant",
    description="""
    Stream-based AI chat endpoint for natural language dashboard building and data analysis.
    
    **Features:**
    - Natural language widget creation: "Add a bar chart of revenue by region"
    - Data analysis with parameters: "Show me customer 42's orders"
    - Parameter extraction from natural language
    - Real-time streaming responses
    
    **SSE Event Types:**
    - `text`: Streamed text content from AI
    - `widget`: Widget configuration ready to add to dashboard
    - `data`: Query results when user asks to see specific data
    - `error`: Error occurred during processing
    - `done`: Conversation turn complete
    
    **Example Usage:**
    ```javascript
    const es = new EventSource('/api/ai/chat?message=...');
    es.addEventListener('text', e => console.log(e.data));
    es.addEventListener('widget', e => {
        const widget = JSON.parse(e.data);
        // Add widget to dashboard
    });
    ```
    """
)
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI chat endpoint with Server-Sent Events streaming
    
    Returns a stream of events:
    - text: Assistant's response text (streamed token by token)
    - widget: Complete widget configuration (when assistant creates a widget)
    - data: Query results (when assistant executes a query preview)
    - error: Error message
    - done: End of response
    """
    
    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if not request.dashboard_id:
        raise HTTPException(status_code=400, detail="dashboard_id is required")
    
    # Convert Pydantic models to dicts for AI service
    history = [
        {
            "role": msg.role,
            "content": msg.content,
            "tool_calls": msg.tool_calls
        }
        for msg in request.conversation_history
    ]
    
    # Create SSE stream
    async def event_generator():
        """Generate SSE events"""
        try:
            async for event in create_chat_stream(
                message=request.message,
                conversation_history=history,
                dashboard_id=request.dashboard_id,
                db=db
            ):
                # Format as SSE
                event_type = event.get("event", "message")
                event_data = event.get("data", "")
                
                # SSE format: event: <type>\ndata: <data>\n\n
                yield f"event: {event_type}\n"
                yield f"data: {event_data}\n\n"
        
        except Exception as e:
            # Stream error event
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        finally:
            # Always send done event
            yield f"event: done\n"
            yield f"data: \n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive"
        }
    )


@router.get(
    "/ai/status",
    summary="Check AI Service Status",
    description="Verify Azure OpenAI connection and configuration"
)
async def ai_status():
    """Check if AI service is properly configured"""
    from app.core.config import settings
    
    # Check if required settings are present
    has_endpoint = bool(settings.AZURE_OPENAI_ENDPOINT)
    has_auth = bool(settings.AZURE_OPENAI_API_KEY) or True  # Managed Identity always available
    has_deployment = bool(settings.AZURE_OPENAI_DEPLOYMENT)
    
    is_configured = has_endpoint and has_auth and has_deployment
    
    return {
        "status": "configured" if is_configured else "not_configured",
        "endpoint": settings.AZURE_OPENAI_ENDPOINT if has_endpoint else None,
        "deployment": settings.AZURE_OPENAI_DEPLOYMENT if has_deployment else None,
        "api_version": settings.AZURE_OPENAI_API_VERSION,
        "authentication": "api_key" if settings.AZURE_OPENAI_API_KEY else "managed_identity",
        "max_tokens": settings.AI_MAX_TOKENS,
        "temperature": settings.AI_TEMPERATURE,
        "message": "AI service is ready" if is_configured else "AI service requires configuration"
    }


@router.post(
    "/ai/test",
    summary="Test AI Service",
    description="Send a simple test message to verify AI is working"
)
async def ai_test():
    """Quick test endpoint to verify AI connectivity"""
    from app.core.ai_service import client
    from app.core.config import settings
    
    try:
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": "Say 'AI service is working' and nothing else."}],
            max_tokens=20,
            temperature=0
        )
        
        return {
            "status": "success",
            "message": response.choices[0].message.content,
            "model": settings.AZURE_OPENAI_DEPLOYMENT
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service test failed: {str(e)}"
        )
