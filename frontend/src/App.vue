<template>
  <div id="app">
    <router-view />
    
    <!-- AI Chat Panel (always mounted, controls its own visibility) -->
    <ChatPanel />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDashboardStore } from '@/stores/useDashboardStore'
import ChatPanel from '@/components/Chat/ChatPanel.vue'

const route = useRoute()
const store = useDashboardStore()

// Update dashboard context when route changes
onMounted(() => {
  updateDashboardContext()
})

// Watch route changes to update context
watch(() => route.params.dashboardId, () => {
  updateDashboardContext()
})

function updateDashboardContext() {
  const dashboardId = route.params.dashboardId || route.meta.dashboardId
  if (dashboardId) {
    store.setCurrentDashboard(dashboardId)
  }
}
</script>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Ensure proper z-index stacking */
.dashboard-container {
  position: relative;
  z-index: 1;
}

.chat-panel,
.ai-fab {
  z-index: 1000;
}
</style>
