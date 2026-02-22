<template>
  <Teleport to="body">
    <!-- Floating Action Button -->
    <transition name="fab">
      <button
        v-if="!store.chatPanelOpen"
        @click="store.openChatPanel"
        class="ai-fab"
        aria-label="Open AI Assistant"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span class="ai-fab-pulse"></span>
      </button>
    </transition>

    <!-- Chat Panel -->
    <transition name="slide-panel">
      <div
        v-if="store.chatPanelOpen"
        class="chat-panel"
        :class="{ minimized: store.chatMinimized }"
      >
        <!-- Header -->
        <div class="chat-header">
          <div class="header-content">
            <div class="header-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
            </div>
            <div class="header-text">
              <h3 class="header-title">Dashboard AI</h3>
              <p class="header-subtitle">
                {{ streaming ? 'Thinking...' : 'Ask me anything' }}
              </p>
            </div>
          </div>
          
          <div class="header-actions">
            <button
              @click="handleClearChat"
              class="header-btn"
              title="Clear conversation"
              v-if="store.conversationLength > 0"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
            
            <button
              @click="store.toggleMinimized"
              class="header-btn"
              :title="store.chatMinimized ? 'Maximize' : 'Minimize'"
            >
              <svg v-if="!store.chatMinimized" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 9l-7 7-7-7"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 15l7-7 7 7"/>
              </svg>
            </button>
            
            <button
              @click="store.closeChatPanel"
              class="header-btn"
              title="Close"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages Area -->
        <div class="chat-messages" ref="messagesContainer" v-if="!store.chatMinimized">
          <!-- Welcome message -->
          <div v-if="store.conversationLength === 0" class="welcome-message">
            <div class="welcome-icon">✨</div>
            <h4 class="welcome-title">How can I help?</h4>
            <p class="welcome-text">
              I can build dashboard widgets or analyze your data. Try:
            </p>
            <div class="welcome-examples">
              <button
                v-for="(example, i) in examplePrompts"
                :key="i"
                @click="handleExampleClick(example)"
                class="example-btn"
              >
                {{ example }}
              </button>
            </div>
          </div>

          <!-- Messages -->
          <ChatMessage
            v-for="(message, index) in displayMessages"
            :key="index"
            :message="message"
            :is-last="index === displayMessages.length - 1"
          />

          <!-- Widget Preview Card -->
          <WidgetPreviewCard
            v-if="store.hasPendingWidget"
            :widget="store.pendingWidget"
            @save="handleSaveWidget"
            @discard="store.clearPendingWidget"
          />

          <!-- Data Preview Card -->
          <DataPreviewCard
            v-if="store.hasPreviewData"
            :data="store.previewData"
            @add-widget="handleAddDataAsWidget"
            @close="store.clearPreviewData"
          />

          <!-- Error Display -->
          <div v-if="error" class="error-message">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <span>{{ error }}</span>
            <button @click="clearError" class="error-dismiss">×</button>
          </div>
        </div>

        <!-- Input Area -->
        <div class="chat-input-area" v-if="!store.chatMinimized">
          <div class="input-container">
            <textarea
              v-model="userInput"
              @keydown.enter.exact.prevent="handleSend"
              @keydown.shift.enter="() => {}"
              placeholder="Ask me to build a widget or analyze data..."
              rows="1"
              ref="inputField"
              class="chat-input"
              :disabled="streaming"
            ></textarea>
            
            <button
              @click="streaming ? stopStream() : handleSend()"
              class="send-btn"
              :class="{ active: userInput.trim(), streaming }"
              :disabled="!userInput.trim() && !streaming"
            >
              <svg v-if="!streaming" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="1"/>
              </svg>
            </button>
          </div>
          
          <div class="input-hint" v-if="!streaming">
            <kbd>Enter</kbd> to send · <kbd>Shift + Enter</kbd> for new line
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/useDashboardStore'
import { useAiChat } from '@/composables/useAiChat'
import ChatMessage from './ChatMessage.vue'
import WidgetPreviewCard from './WidgetPreviewCard.vue'
import DataPreviewCard from './DataPreviewCard.vue'

const store = useDashboardStore()
const { streaming, error, streamingMessage, sendMessage, stopStream, clearError } = useAiChat()

const userInput = ref('')
const messagesContainer = ref(null)
const inputField = ref(null)

// Example prompts for welcome screen
const examplePrompts = [
  'Add a bar chart of revenue by region',
  'Show me top 5 products',
  'Create a metric card for total orders'
]

// Display messages (history + streaming)
const displayMessages = computed(() => {
  const messages = [...store.conversationHistory]
  if (streamingMessage.value) {
    messages.push(streamingMessage.value)
  }
  return messages
})

// Auto-scroll to bottom on new messages
watch(displayMessages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// Focus input when panel opens
watch(() => store.chatPanelOpen, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      inputField.value?.focus()
    })
  }
})

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handleSend() {
  const message = userInput.value.trim()
  if (!message || streaming.value) return
  
  sendMessage(message)
  userInput.value = ''
  
  // Auto-resize textarea
  if (inputField.value) {
    inputField.value.style.height = 'auto'
  }
}

function handleExampleClick(example) {
  userInput.value = example
  handleSend()
}

function handleClearChat() {
  if (confirm('Clear conversation history?')) {
    store.clearConversation()
  }
}

function handleSaveWidget() {
  // Emit event to parent (DashboardRenderer)
  // The actual save logic is in DashboardRenderer
  const widget = store.pendingWidget
  if (widget) {
    // This will be handled by DashboardRenderer watching pendingWidget
    console.log('Widget ready to save:', widget)
  }
}

function handleAddDataAsWidget() {
  // Convert preview data into a widget request
  const data = store.previewData
  if (data) {
    userInput.value = `Add this data as a widget on the dashboard`
    handleSend()
  }
}

// Auto-resize textarea
watch(userInput, () => {
  nextTick(() => {
    if (inputField.value) {
      inputField.value.style.height = 'auto'
      inputField.value.style.height = inputField.value.scrollHeight + 'px'
    }
  })
})

onMounted(() => {
  // Check AI status on mount
  // checkAiStatus()
  console.log('Chat panel loaded')
})
</script>

<style scoped>
/* ══════════════════════════════════════════════════════════════
   Floating Action Button
   ══════════════════════════════════════════════════════════════ */

.ai-fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 24px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.ai-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.5);
}

.ai-fab:active {
  transform: scale(0.95);
}

.ai-fab-pulse {
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0.3;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.15); opacity: 0; }
}


/* ══════════════════════════════════════════════════════════════
   Chat Panel
   ══════════════════════════════════════════════════════════════ */

.chat-panel {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 420px;
  max-width: calc(100vw - 4rem);
  max-height: calc(100vh - 4rem);
  background: #ffffff;
  border-radius: 1rem;
  box-shadow: 
    0 0 0 1px rgba(0, 0, 0, 0.05),
    0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1001;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-panel.minimized {
  height: 64px;
}


/* ══════════════════════════════════════════════════════════════
   Header
   ══════════════════════════════════════════════════════════════ */

.chat-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-title {
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
}

.header-subtitle {
  font-size: 0.75rem;
  opacity: 0.9;
  margin: 0;
  margin-top: 0.125rem;
}

.header-actions {
  display: flex;
  gap: 0.25rem;
}

.header-btn {
  width: 32px;
  height: 32px;
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}


/* ══════════════════════════════════════════════════════════════
   Messages Area
   ══════════════════════════════════════════════════════════════ */

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #fafafa;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}


/* ══════════════════════════════════════════════════════════════
   Welcome Message
   ══════════════════════════════════════════════════════════════ */

.welcome-message {
  text-align: center;
  padding: 2rem 1rem;
  animation: fadeIn 0.5s ease-out;
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: bounce 2s ease-in-out infinite;
}

.welcome-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.welcome-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
}

.welcome-examples {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.example-btn {
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.example-btn:hover {
  border-color: #667eea;
  background: #f9fafb;
  transform: translateX(2px);
}


/* ══════════════════════════════════════════════════════════════
   Error Message
   ══════════════════════════════════════════════════════════════ */

.error-message {
  padding: 0.875rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  color: #dc2626;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  animation: slideUp 0.3s ease-out;
}

.error-dismiss {
  margin-left: auto;
  background: none;
  border: none;
  color: #dc2626;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.error-dismiss:hover {
  opacity: 1;
}


/* ══════════════════════════════════════════════════════════════
   Input Area
   ══════════════════════════════════════════════════════════════ */

.chat-input-area {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-family: inherit;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  transition: all 0.2s;
}

.chat-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 0.75rem;
  background: #e5e7eb;
  border: none;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.send-btn.streaming {
  background: #ef4444;
  color: white;
}

.send-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
}

.input-hint kbd {
  padding: 0.125rem 0.375rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  border: 1px solid #e5e7eb;
  font-size: 0.7rem;
  font-family: monospace;
}


/* ══════════════════════════════════════════════════════════════
   Animations
   ══════════════════════════════════════════════════════════════ */

.fab-enter-active,
.fab-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-enter-from,
.fab-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-panel-enter-from,
.slide-panel-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}


/* ══════════════════════════════════════════════════════════════
   Responsive
   ══════════════════════════════════════════════════════════════ */

@media (max-width: 640px) {
  .chat-panel {
    width: 100%;
    max-width: 100%;
    bottom: 0;
    right: 0;
    border-radius: 1rem 1rem 0 0;
    max-height: calc(100vh - 2rem);
  }
  
  .ai-fab {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
