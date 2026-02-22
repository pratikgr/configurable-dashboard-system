<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-bubble">
      <div class="message-content" v-html="formattedContent"></div>
      <span v-if="isStreaming" class="streaming-cursor">▊</span>
      <div class="message-timestamp">{{ formattedTime }}</div>
      <div v-if="message.hasWidget || message.hasData" class="message-badges">
        <span v-if="message.hasWidget" class="badge badge-widget">Widget</span>
        <span v-if="message.hasData" class="badge badge-data">Data</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

const messageClass = computed(() => {
  return props.message.role === 'user' ? 'message-user' : 'message-assistant'
})

const formattedContent = computed(() => {
  let text = props.message.content || ''
  
  // === AGGRESSIVE CLEANING ===
  
  // Step 1: Remove bullet points before numbered items
  // Matches: "* 1." or "- 1." or "• 1." → "1."
  text = text.replace(/^[*\-•]\s*(\d+\.)/gm, '$1')
  text = text.replace(/([.!?:])\s*[*\-•]\s*(\d+\.)/g, '$1\n$2')
  
  // Step 2: Add space after numbers if missing
  // Matches: "1.text" → "1. text"
  text = text.replace(/(\d+\.)([A-Za-z_])/g, '$1 $2')
  
  // Step 3: Force line breaks before numbered items
  // Matches: "text1." → "text\n1."
  text = text.replace(/([.!?:])(\d+\.)/g, '$1\n$2')
  
  // Step 4: Force line breaks before questions
  text = text.replace(/([.!?])(What|How|Would|Can|Should)/g, '$1\n\n$2')
  
  // Step 5: Process line by line
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)
  let html = ''
  let paragraphBuffer = []
  
  for (const line of lines) {
    // Check if it's a numbered list item (after cleaning)
    if (/^\d+\.\s/.test(line)) {
      // Flush paragraph buffer
      if (paragraphBuffer.length > 0) {
        html += `<p>${paragraphBuffer.join(' ')}</p>`
        paragraphBuffer = []
      }
      
      // Add list item
      const match = line.match(/^(\d+)\.\s+(.+)$/)
      if (match) {
        const [, num, itemText] = match
        html += `<div class="list-item"><span class="list-number">${num}.</span><span>${formatInline(itemText)}</span></div>`
      }
    }
    // Regular text
    else {
      paragraphBuffer.push(formatInline(line))
    }
  }
  
  // Flush remaining paragraphs
  if (paragraphBuffer.length > 0) {
    html += `<p>${paragraphBuffer.join(' ')}</p>`
  }
  
  return html
})

function formatInline(text) {
  // Remove any stray bullets or dashes at start of inline text
  text = text.replace(/^[*\-•]\s+/, '')
  
  // Bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // Italic
  text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  
  // Code
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  return text
}

const formattedTime = computed(() => {
  const timestamp = props.message.timestamp
  if (!timestamp) return ''
  
  const now = new Date()
  const messageTime = new Date(timestamp)
  const diffMs = now - messageTime
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  return messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})
</script>

<style scoped>
.chat-message {
  display: flex;
  margin-bottom: 1rem;
  animation: slideIn 0.2s ease-out;
}

.message-user {
  justify-content: flex-end;
}

.message-assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 0.875rem 1.125rem;
  border-radius: 1rem;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.message-assistant .message-bubble {
  background: white;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 0.25rem;
}

.message-content {
  font-size: 15px;
  line-height: 1.6;
}

.message-content p {
  margin: 0 0 12px 0;
}

.message-content p:last-child {
  margin-bottom: 0;
}

.list-item {
  display: flex;
  gap: 8px;
  margin: 6px 0;
  line-height: 1.5;
}

.list-item .list-number {
  font-weight: 600;
  color: #667eea;
  min-width: 24px;
  flex-shrink: 0;
}

.message-user .list-item .list-number {
  color: rgba(255, 255, 255, 0.9);
}

.message-content strong {
  font-weight: 600;
}

.message-content em {
  font-style: italic;
}

.message-content code {
  background: rgba(0, 0, 0, 0.05);
  color: #e83e8c;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
}

.message-user code {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.streaming-cursor {
  display: inline-block;
  width: 8px;
  height: 18px;
  background: currentColor;
  margin-left: 2px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.message-timestamp {
  font-size: 11px;
  color: #999;
  margin-top: 6px;
}

.message-user .message-timestamp {
  color: rgba(255, 255, 255, 0.7);
}

.message-badges {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.badge-widget {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.badge-data {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.message-user .badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>