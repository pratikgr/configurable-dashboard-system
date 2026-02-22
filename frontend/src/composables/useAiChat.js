/**
 * AI Chat Composable
 * Handles Server-Sent Events (SSE) streaming from AI chat endpoint
 */
import { ref } from 'vue'
import { useDashboardStore } from '@/stores/useDashboardStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useAiChat() {
  const store = useDashboardStore()
  
  // ══════════════════════════════════════════════════════════════
  // State
  // ══════════════════════════════════════════════════════════════
  
  const streaming = ref(false)
  const error = ref(null)
  const currentEventSource = ref(null)
  
  // Current assistant message being built from stream
  const streamingMessage = ref(null)
  
  
  // ══════════════════════════════════════════════════════════════
  // Send Message
  // ══════════════════════════════════════════════════════════════
  
  /**
   * Send a message to the AI and handle streaming response
   */
  async function sendMessage(message) {
    if (!message || !message.trim()) {
      return
    }
    
    if (!store.currentDashboardId) {
      error.value = 'No dashboard selected'
      return
    }
    
    // Add user message to history
    store.addMessage({
      role: 'user',
      content: message
    })
    
    // Clear previous errors
    error.value = null
    streaming.value = true
    
    // Initialize streaming assistant message
    streamingMessage.value = {
      role: 'assistant',
      content: '',
      isStreaming: true
    }
    
    try {
      // Build request body
      const requestBody = {
        message: message,
        dashboard_id: store.currentDashboardId,
        conversation_history: store.getConversationForAPI()
      }
      
      // Use fetch instead of EventSource for POST requests
      const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(requestBody)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let currentEventType = 'text'

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        
        // Process complete SSE messages
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEventType = line.substring(6).trim()
            continue
          }
          
          if (line.startsWith('data:')) {
            // Extract data - DON'T trim text content to preserve spaces
            let data = line.substring(5)
            
            // For non-text events (JSON), trim whitespace
            if (currentEventType !== 'text') {
              data = data.trim()
            } else {
              // For text, only remove the single space after "data:"
              if (data.startsWith(' ')) {
                data = data.substring(1)
              }
            }
            
            // Skip empty data (except for text which might be a space)
            if (!data && currentEventType !== 'text') continue
            
            await handleSSEEvent(currentEventType, data)
            
            // Reset event type for safety
            if (currentEventType !== 'text') {
              currentEventType = 'text'
            }
          }
        }
      }
      
      // Finalize streaming message
      if (streamingMessage.value) {
        streamingMessage.value.isStreaming = false
        store.addMessage(streamingMessage.value)
        streamingMessage.value = null
      }
      
    } catch (err) {
      console.error('AI chat error:', err)
      error.value = err.message || 'Failed to communicate with AI service'
      
      // Add error message to chat
      store.addMessage({
        role: 'assistant',
        content: `❌ Error: ${error.value}`,
        isError: true
      })
    } finally {
      streaming.value = false
    }
  }
  
  
  // ══════════════════════════════════════════════════════════════
  // SSE Event Handlers
  // ══════════════════════════════════════════════════════════════
  
  let currentEventType = 'text'
  
  async function handleSSEEvent(eventType, data) {
    currentEventType = eventType
    
    switch (eventType) {
      case 'text':
        handleTextEvent(data)
        break
      
      case 'widget':
        handleWidgetEvent(data)
        break
      
      case 'data':
        handleDataEvent(data)
        break
      
      case 'error':
        handleErrorEvent(data)
        break
      
      case 'done':
        handleDoneEvent()
        break
    }
  }
  
  /**
   * Handle streaming text tokens
   */
  function handleTextEvent(data) {
    if (streamingMessage.value) {
      streamingMessage.value.content += data
    }
  }
  
  /**
   * Handle widget creation event
   */
  function handleWidgetEvent(data) {
    try {
      const widget = JSON.parse(data)
      
      // Check for error in widget response
      if (widget.error) {
        console.error('Widget generation error:', widget.error)
        store.setGenerationError(widget.error)
        return
      }
      
      // Set as pending widget
      store.setPendingWidget(widget)
      
      // Add a visual indicator in the chat
      if (streamingMessage.value) {
        streamingMessage.value.content += '\n\n✨ Widget created! You can preview it on the dashboard.'
        streamingMessage.value.hasWidget = true
      }
      
    } catch (err) {
      console.error('Failed to parse widget:', err)
      error.value = 'Failed to parse widget configuration'
    }
  }
  
  /**
   * Handle query data preview event
   */
  function handleDataEvent(data) {
    try {
      const result = JSON.parse(data)
      
      // Check for error in data response
      if (result.error) {
        console.error('Query execution error:', result.error)
        if (streamingMessage.value) {
          streamingMessage.value.content += `\n\n❌ ${result.error}`
        }
        return
      }
      
      // Set preview data in store
      store.setPreviewData(result)
      
      // Add visual indicator in chat
      if (streamingMessage.value) {
        streamingMessage.value.content += `\n\n📊 Showing ${result.rows?.length || 0} of ${result.total || 0} results.`
        streamingMessage.value.hasData = true
      }
      
    } catch (err) {
      console.error('Failed to parse data:', err)
      error.value = 'Failed to parse query results'
    }
  }
  
  /**
   * Handle error event
   */
  function handleErrorEvent(data) {
    try {
      const errorData = JSON.parse(data)
      error.value = errorData.error || 'An error occurred'
    } catch {
      error.value = data || 'An error occurred'
    }
    
    if (streamingMessage.value) {
      streamingMessage.value.content += `\n\n❌ Error: ${error.value}`
      streamingMessage.value.isError = true
    }
  }
  
  /**
   * Handle done event
   */
  function handleDoneEvent() {
    // Stream complete - cleanup will happen in finally block
  }
  
  
  // ══════════════════════════════════════════════════════════════
  // Utilities
  // ══════════════════════════════════════════════════════════════
  
  /**
   * Stop current stream
   */
  function stopStream() {
    if (currentEventSource.value) {
      currentEventSource.value.close()
      currentEventSource.value = null
    }
    
    streaming.value = false
    
    // Finalize any pending message
    if (streamingMessage.value) {
      streamingMessage.value.isStreaming = false
      streamingMessage.value.content += ' [Stopped by user]'
      store.addMessage(streamingMessage.value)
      streamingMessage.value = null
    }
  }
  
  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }
  
  /**
   * Check if AI is available
   */
  async function checkAiStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/status`)
      const status = await response.json()
      return status.status === 'configured'
    } catch {
      return false
    }
  }
  
  
  // ══════════════════════════════════════════════════════════════
  // Return
  // ══════════════════════════════════════════════════════════════
  
  return {
    // State
    streaming,
    error,
    streamingMessage,
    
    // Actions
    sendMessage,
    stopStream,
    clearError,
    checkAiStatus
  }
}
