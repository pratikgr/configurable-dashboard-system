<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-bubble">
      <!-- Simple: Just display AI's text with pre-wrap -->
      <div class="message-content">{{ message.content }}</div>
      
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
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
}

.message-assistant .message-bubble {
  background: white;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 0.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.message-content {
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap; /* CRITICAL: Preserves AI's line breaks */
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.streaming-cursor {
  display: inline-block;
  width: 8px;
  height: 18px;
  background: currentColor;
  margin-left: 2px;
  animation: blink 1s infinite;
  vertical-align: text-bottom;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.message-timestamp {
  font-size: 11px;
  color: #999;
  margin-top: 6px;
  font-weight: 500;
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