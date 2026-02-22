/**
 * Dashboard Store
 * Manages dashboard state including AI chat and pending widgets
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDashboardStore = defineStore('dashboard', () => {
  // ══════════════════════════════════════════════════════════════
  // State
  // ══════════════════════════════════════════════════════════════
  
  // Current dashboard being viewed
  const currentDashboardId = ref(null)
  
  // Chat panel state
  const chatPanelOpen = ref(false)
  const chatMinimized = ref(false)
  
  // Pending widget from AI (waiting to be saved)
  const pendingWidget = ref(null)
  
  // Temporary data results from AI (for analyst mode)
  const previewData = ref(null)
  
  // AI conversation history for current dashboard
  const conversationHistory = ref([])
  
  // Loading/error states
  const isGeneratingWidget = ref(false)
  const widgetGenerationError = ref(null)
  
  
  // ══════════════════════════════════════════════════════════════
  // Computed
  // ══════════════════════════════════════════════════════════════
  
  const hasPendingWidget = computed(() => pendingWidget.value !== null)
  const hasPreviewData = computed(() => previewData.value !== null)
  const conversationLength = computed(() => conversationHistory.value.length)
  
  
  // ══════════════════════════════════════════════════════════════
  // Actions
  // ══════════════════════════════════════════════════════════════
  
  /**
   * Set the current dashboard context
   */
  function setCurrentDashboard(dashboardId) {
    if (currentDashboardId.value !== dashboardId) {
      currentDashboardId.value = dashboardId
      // Clear conversation when switching dashboards
      conversationHistory.value = []
      clearPendingWidget()
      clearPreviewData()
    }
  }
  
  /**
   * Toggle chat panel open/closed
   */
  function toggleChatPanel() {
    chatPanelOpen.value = !chatPanelOpen.value
    if (chatPanelOpen.value) {
      chatMinimized.value = false
    }
  }
  
  /**
   * Open chat panel
   */
  function openChatPanel() {
    chatPanelOpen.value = true
    chatMinimized.value = false
  }
  
  /**
   * Close chat panel
   */
  function closeChatPanel() {
    chatPanelOpen.value = false
  }
  
  /**
   * Minimize/maximize chat panel
   */
  function toggleMinimized() {
    chatMinimized.value = !chatMinimized.value
  }
  
  /**
   * Set pending widget from AI
   */
  function setPendingWidget(widget) {
    pendingWidget.value = widget
    isGeneratingWidget.value = false
    widgetGenerationError.value = null
  }
  
  /**
   * Clear pending widget
   */
  function clearPendingWidget() {
    pendingWidget.value = null
    widgetGenerationError.value = null
  }
  
  /**
   * Set preview data from AI query execution
   */
  function setPreviewData(data) {
    previewData.value = data
  }
  
  /**
   * Clear preview data
   */
  function clearPreviewData() {
    previewData.value = null
  }
  
  /**
   * Add message to conversation history
   */
  function addMessage(message) {
    conversationHistory.value.push({
      ...message,
      timestamp: new Date().toISOString()
    })
  }
  
  /**
   * Clear conversation history
   */
  function clearConversation() {
    conversationHistory.value = []
    clearPendingWidget()
    clearPreviewData()
  }
  
  /**
   * Set widget generation loading state
   */
  function setGenerating(isGenerating) {
    isGeneratingWidget.value = isGenerating
    if (isGenerating) {
      widgetGenerationError.value = null
    }
  }
  
  /**
   * Set widget generation error
   */
  function setGenerationError(error) {
    widgetGenerationError.value = error
    isGeneratingWidget.value = false
  }
  
  /**
   * Convert pending widget to confirmed widget (after save)
   */
  function confirmPendingWidget() {
    const widget = pendingWidget.value
    clearPendingWidget()
    return widget
  }
  
  /**
   * Get conversation history formatted for API
   */
  function getConversationForAPI() {
    return conversationHistory.value.map(msg => ({
      role: msg.role,
      content: msg.content,
      tool_calls: msg.tool_calls || undefined
    }))
  }
  
  /**
   * Reset all state (e.g., on logout or dashboard change)
   */
  function resetState() {
    currentDashboardId.value = null
    chatPanelOpen.value = false
    chatMinimized.value = false
    pendingWidget.value = null
    previewData.value = null
    conversationHistory.value = []
    isGeneratingWidget.value = false
    widgetGenerationError.value = null
  }
  
  
  // ══════════════════════════════════════════════════════════════
  // Return
  // ══════════════════════════════════════════════════════════════
  
  return {
    // State
    currentDashboardId,
    chatPanelOpen,
    chatMinimized,
    pendingWidget,
    previewData,
    conversationHistory,
    isGeneratingWidget,
    widgetGenerationError,
    
    // Computed
    hasPendingWidget,
    hasPreviewData,
    conversationLength,
    
    // Actions
    setCurrentDashboard,
    toggleChatPanel,
    openChatPanel,
    closeChatPanel,
    toggleMinimized,
    setPendingWidget,
    clearPendingWidget,
    setPreviewData,
    clearPreviewData,
    addMessage,
    clearConversation,
    setGenerating,
    setGenerationError,
    confirmPendingWidget,
    getConversationForAPI,
    resetState
  }
})
