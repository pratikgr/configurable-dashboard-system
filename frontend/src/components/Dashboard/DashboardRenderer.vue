<template>
  <div class="dashboard-container p-6">
    <!-- Dashboard Header -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ config?.title || 'Dashboard' }}</h1>
        <p v-if="config?.description" class="text-gray-600 mt-1">{{ config.description }}</p>
      </div>
      
      <!-- Edit Mode Toggle -->
      <button 
        @click="toggleEditMode" 
        :class="editMode ? 'btn-success' : 'btn-primary'"
        class="flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="!editMode" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M5 13l4 4L19 7" />
        </svg>
        {{ editMode ? '✓ Done Editing' : '✏️ Edit Layout' }}
      </button>
    </div>

    <!-- Edit Mode Info -->
    <div v-if="editMode" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div class="flex items-start gap-3">
        <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <h4 class="text-sm font-semibold text-blue-900">Edit Mode Active</h4>
          <p class="text-sm text-blue-700 mt-1">
            • Drag widgets by their headers to reorder<br>
            • Resize widgets by dragging corners and edges<br>
            • Click "Done Editing" to save your layout
          </p>
        </div>
      </div>
    </div>

    <!-- Global Filters -->
    <div v-if="config?.globalFilters && config.globalFilters.length > 0" 
         class="card mb-6">
      <div class="flex gap-4 flex-wrap">
        <div v-for="filter in config.globalFilters" :key="filter.id" class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ filter.label }}
          </label>
          
          <!-- Date Range Filter -->
          <input
            v-if="filter.type === 'daterange'"
            type="date"
            v-model="filters[filter.id]"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilterChange"
          />
          
          <!-- Dropdown Filter -->
          <select
            v-else-if="filter.type === 'dropdown'"
            v-model="filters[filter.id]"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilterChange"
          >
            <option value="">All</option>
            <option v-for="option in filter.options" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
        </div>
        
        <div class="flex items-end">
          <button @click="refreshAllWidgets" class="btn-primary">
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh All
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- GridStack Layout -->
    <div ref="gridContainer" class="grid-stack">
      <div
        v-for="widget in config?.widgets"
        :key="widget.id"
        class="grid-stack-item"
        :gs-x="widget.position.x"
        :gs-y="widget.position.y"
        :gs-w="widget.position.w"
        :gs-h="widget.position.h"
        :gs-id="widget.id"
      >
        <div class="grid-stack-item-content">
          <div class="card h-full flex flex-col">
            <!-- Widget Header -->
            <div class="widget-header flex justify-between items-center mb-2 p-2 rounded flex-shrink-0" 
                :class="{ 'cursor-move bg-gray-50': editMode }">
              <div class="flex items-center gap-2">
                <svg v-if="editMode" class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
                <h3 class="text-lg font-semibold text-gray-800">{{ widget.title }}</h3>
              </div>
              
              <div class="flex items-center gap-2">
                <!-- Refresh button -->
                <button 
                  @click.stop="refreshWidget(widget.id)"
                  class="text-gray-400 hover:text-gray-600 transition-colors"
                  :disabled="widgetLoading[widget.id]"
                >
                  <svg class="w-5 h-5" :class="{ 'animate-spin': widgetLoading[widget.id] }" 
                      fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                
                <!-- Delete button (only in edit mode) -->
                <button 
                  v-if="editMode"
                  @click.stop="deleteWidget(widget.id)"
                  class="text-red-400 hover:text-red-600 transition-colors"
                  title="Delete widget"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Widget Content -->
            <div class="widget-content flex-1">
              <component
                :is="getWidgetComponent(widget.type)"
                :key="`${widget.id}-${widgetRenderKey[widget.id] || 0}`"
                :config="widget"
                :data="widgetData[widget.id]"
                :loading="widgetLoading[widget.id]"
                :error="widgetErrors[widget.id]"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!config" class="flex justify-center items-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    </div>

    <!-- Save Widget Banner (AI Integration) -->
    <transition name="fade">
      <div v-if="showSaveBanner" class="save-widget-banner">
        <div class="banner-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <div class="banner-text">
            <strong>New widget added</strong>
            <span>Save to make it permanent on this dashboard</span>
          </div>
        </div>
        <div class="banner-actions">
          <button @click="discardPendingWidget" class="banner-btn secondary">
            Discard
          </button>
          <button @click="savePendingWidget" class="banner-btn primary">
            Save Widget
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { GridStack } from 'gridstack'
import 'gridstack/dist/gridstack.min.css'
import { useQueryExecutor } from '@/composables/useQueryExecutor'
import { getWidgetComponent } from '@/utils/widgetRegistry'
import { transformData } from '@/utils/dataTransformers'
import { useDashboardStore } from '@/stores/useDashboardStore'
import axios from '@/plugins/axios'

const props = defineProps({
  dashboardId: {
    type: String,
    required: true
  }
})

const config = ref(null)
const filters = ref({})
const widgetData = ref({})
const widgetLoading = ref({})
const widgetErrors = ref({})
const widgetRenderKey = ref({})
const editMode = ref(false)
const gridContainer = ref(null)

// AI Integration
const dashboardStore = useDashboardStore()
const showSaveBanner = ref(false)

let grid = null

const { executeQuery } = useQueryExecutor()

onMounted(async () => {
  await loadDashboardConfig()
  
  // Set dashboard context for AI
  dashboardStore.setCurrentDashboard(props.dashboardId)
  
  initializeFilters()
  await nextTick()
  await nextTick() // Double nextTick for GridStack
  await initializeGrid()
  // Wait for grid to be fully rendered
  await new Promise(resolve => setTimeout(resolve, 100))
  await loadAllWidgets()
})

onUnmounted(() => {
  if (grid) {
    grid.destroy(false)
  }
})

// ══════════════════════════════════════════════════════════════
// AI Integration: Watch for Pending Widget
// ══════════════════════════════════════════════════════════════

/**
 * Watch for pending widget from AI and add it to the grid as preview
 */
watch(() => dashboardStore.pendingWidget, async (widget) => {
  if (!widget || !grid) return
  
  console.log('Pending widget received:', widget)
  
  // Assign next available position if not already assigned
  if (!widget.position || widget.position.y === 0) {
    widget.position = getNextAvailablePosition(widget)
  }
  
  // Add widget to config (will render via v-for)
  config.value.widgets.push(widget)
  
  await nextTick()
  
  // Tell GridStack about the new item
  const widgetElement = document.querySelector(`[gs-id="${widget.id}"]`)
  if (widgetElement && grid) {
    grid.makeWidget(widgetElement)
    
    // Add preview styling
    widgetElement.classList.add('pending-widget-preview')
  }
  
  // Load data for the widget
  await loadWidgetData(widget.id)
  
  // Show save banner
  showSaveBanner.value = true
  
  // Scroll to the new widget
  widgetElement?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}, { deep: true })

/**
 * Get next available position on the grid
 */
function getNextAvailablePosition(widget) {
  if (!config.value.widgets.length) {
    return { x: 0, y: 0, w: widget.position?.w || 6, h: widget.position?.h || 4 }
  }
  
  // Find the maximum Y position + height
  const maxY = Math.max(...config.value.widgets.map(w => {
    const pos = w.position || { y: 0, h: 4 }
    return (pos.y || 0) + (pos.h || 4)
  }))
  
  return {
    x: 0,
    y: maxY,
    w: widget.position?.w || 6,
    h: widget.position?.h || 4
  }
}

/**
 * Save the pending widget permanently
 */
async function savePendingWidget() {
  const widget = dashboardStore.pendingWidget
  if (!widget) return
  
  try {
    // Call API - axios already has baseURL configured
    await axios.post(`/api/dashboard/${props.dashboardId}/widget`, widget)
    
    // Remove preview styling
    const widgetElement = document.querySelector(`[gs-id="${widget.id}"]`)
    widgetElement?.classList.remove('pending-widget-preview')
    
    // Clear from store
    dashboardStore.confirmPendingWidget()
    showSaveBanner.value = false
    
    console.log('Widget saved successfully')
  } catch (error) {
    console.error('Failed to save widget:', error)
    alert('Failed to save widget. Please try again.')
  }
}

async function deleteWidget(widgetId) {
  if (!confirm('Are you sure you want to delete this widget?')) {
    return
  }
  
  try {
    // Call backend to delete
    await axios.delete(`/api/dashboard/${props.dashboardId}/widget/${widgetId}`)
    
    // Remove from local config
    const index = config.value.widgets.findIndex(w => w.id === widgetId)
    if (index !== -1) {
      config.value.widgets.splice(index, 1)
    }
    
    // Remove from GridStack
    const widgetElement = document.querySelector(`[gs-id="${widgetId}"]`)
    if (widgetElement && grid) {
      grid.removeWidget(widgetElement)
    }
    
    console.log('Widget deleted successfully')
  } catch (error) {
    console.error('Failed to delete widget:', error)
    alert('Failed to delete widget. Please try again.')
  }
}
/**
 * Discard the pending widget
 */
function discardPendingWidget() {
  const widget = dashboardStore.pendingWidget
  if (!widget) return
  
  // Remove from config
  const index = config.value.widgets.findIndex(w => w.id === widget.id)
  if (index !== -1) {
    config.value.widgets.splice(index, 1)
  }
  
  // Clear from store
  dashboardStore.clearPendingWidget()
  showSaveBanner.value = false
  
  // Remove from GridStack
  const widgetElement = document.querySelector(`[gs-id="${widget.id}"]`)
  if (widgetElement && grid) {
    grid.removeWidget(widgetElement)
  }
}

// ══════════════════════════════════════════════════════════════
// Original Functions
// ══════════════════════════════════════════════════════════════

const loadDashboardConfig = async () => {
  try {
    const module = await import(`@/config/dashboards/${props.dashboardId}.json`)
    config.value = module.default || module
    
    // Load saved layout from localStorage
    const savedLayout = localStorage.getItem(`dashboard-layout-${props.dashboardId}`)
    if (savedLayout) {
      try {
        const layout = JSON.parse(savedLayout)
        // Apply saved positions
        config.value.widgets = config.value.widgets.map(widget => {
          const saved = layout.find(l => l.id === widget.id)
          if (saved) {
            return { 
              ...widget, 
              position: { 
                x: saved.x, 
                y: saved.y, 
                w: saved.w, 
                h: saved.h 
              } 
            }
          }
          return widget
        })
      } catch (e) {
        console.error('Error loading saved layout:', e)
      }
    }
  } catch (error) {
    console.error('Error loading dashboard config:', error)
  }
}

const initializeGrid = async () => {
  if (!gridContainer.value || !config.value?.widgets) return

  try {
    grid = GridStack.init({
      column: 12,
      cellHeight: 80,
      margin: 16,
      animate: true,
      float: false,
      disableResize: !editMode.value,
      disableDrag: !editMode.value,
      draggable: {
        handle: '.widget-header'
      },
      resizable: {
        handles: 'e,se,s,sw,w'
      }
    }, gridContainer.value)

    // Listen to layout changes
    grid.on('change', (event, items) => {
      if (editMode.value && items && items.length > 0) {
        saveLayout(items)
      }
    })
    
    // Listen to resize end to trigger chart re-render
    grid.on('resizestop', (event, element) => {
      const widgetId = element.getAttribute('gs-id')
      if (widgetId) {
        // Force widget to re-render
        widgetRenderKey.value[widgetId] = (widgetRenderKey.value[widgetId] || 0) + 1
      }
    })
    
    console.log('GridStack initialized successfully')
  } catch (error) {
    console.error('Error initializing GridStack:', error)
  }
}

const toggleEditMode = () => {
  editMode.value = !editMode.value
  
  if (grid) {
    if (editMode.value) {
      grid.enable()
      console.log('Edit mode enabled')
    } else {
      grid.disable()
      console.log('Edit mode disabled, layout saved')
    }
  }
}

const saveLayout = (items) => {
  const layout = items.map(item => ({
    id: item.id,
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h
  }))
  
  localStorage.setItem(
    `dashboard-layout-${props.dashboardId}`, 
    JSON.stringify(layout)
  )
  
  console.log('Layout saved:', layout)
}

const initializeFilters = () => {
  if (!config.value?.globalFilters) return
  
  config.value.globalFilters.forEach(filter => {
    filters.value[filter.id] = filter.default || ''
  })
}

const loadAllWidgets = async () => {
  if (!config.value?.widgets) return
  
  // Load widgets sequentially to ensure proper rendering
  for (const widget of config.value.widgets) {
    await loadWidgetData(widget.id)
    // Small delay to ensure DOM updates
    await new Promise(resolve => setTimeout(resolve, 50))
  }
}

const loadWidgetData = async (widgetId) => {
  const widget = config.value.widgets.find(w => w.id === widgetId)
  if (!widget) return

  widgetLoading.value[widgetId] = true
  widgetErrors.value[widgetId] = null

  try {
    const params = buildQueryParams(widget)
    const result = await executeQuery(widget.queryId, params)
    
    console.log(`Widget ${widgetId} data:`, result.data)
    
    const transformedData = transformData(result.data, widget.dataMapping)
    widgetData.value[widgetId] = transformedData
    
    // Trigger re-render after data loads
    await nextTick()
    widgetRenderKey.value[widgetId] = (widgetRenderKey.value[widgetId] || 0) + 1
    
  } catch (error) {
    console.error(`Error loading widget ${widgetId}:`, error)
    widgetErrors.value[widgetId] = error.message
  } finally {
    widgetLoading.value[widgetId] = false
  }
}

const buildQueryParams = (widget) => {
  const params = {}
  
  if (config.value.globalFilters) {
    config.value.globalFilters.forEach(filter => {
      if (filter.applyTo === '*' || filter.applyTo?.includes(widget.id)) {
        params[filter.id] = filters.value[filter.id]
      }
    })
  }
  
  if (widget.parameters) {
    Object.assign(params, widget.parameters)
  }
  
  return params
}

const handleFilterChange = () => {
  loadAllWidgets()
}

const refreshWidget = async (widgetId) => {
  await loadWidgetData(widgetId)
}

const refreshAllWidgets = () => {
  loadAllWidgets()
}
</script>

<style scoped>
/* GridStack Core Styles */
.grid-stack {
  background: transparent;
}

.grid-stack-item {
  overflow: visible;
}

.grid-stack-item-content {
  overflow: visible;
  inset: 0 !important;
}

.grid-stack-item.ui-draggable-dragging,
.grid-stack-item.ui-resizable-resizing {
  opacity: 0.9;
  z-index: 1000;
  transition: opacity 0.2s;
}

.grid-stack-item.ui-draggable-dragging .card {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: scale(1.02);
}

/* Widget Header - Drag Handle */
.widget-header {
  user-select: none;
  transition: background-color 0.2s;
}

.widget-header.cursor-move:hover {
  background-color: #f3f4f6;
}

/* Widget Content - CRITICAL for charts */
.widget-content {
  min-height: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

/* Ensure chart containers get full size */
.widget-content > div {
  flex: 1;
  min-height: 250px;
}

/* Resize Handles Styling */
.ui-resizable-handle {
  position: absolute;
  font-size: 0.1px;
  display: block;
  touch-action: none;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.ui-resizable-handle:hover {
  opacity: 1;
}

.ui-resizable-e {
  cursor: e-resize;
  width: 7px;
  right: -5px;
  top: 0;
  height: 100%;
}

.ui-resizable-w {
  cursor: w-resize;
  width: 7px;
  left: -5px;
  top: 0;
  height: 100%;
}

.ui-resizable-s {
  cursor: s-resize;
  height: 7px;
  width: 100%;
  bottom: -5px;
  left: 0;
}

.ui-resizable-se {
  cursor: se-resize;
  width: 20px;
  height: 20px;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 50%, #3b82f6 50%);
  border-radius: 0 0 0.5rem 0;
}

.ui-resizable-sw {
  cursor: sw-resize;
  width: 20px;
  height: 20px;
  left: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 50%, #3b82f6 50%);
  border-radius: 0 0 0 0.5rem;
}

.dashboard-container {
  min-height: 100vh;
}

/* Success Button Style */
.btn-success {
  background-color: #10b981;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.btn-success:hover {
  background-color: #059669;
}

/* ══════════════════════════════════════════════════════════════
   AI Integration Styles
   ══════════════════════════════════════════════════════════════ */

.pending-widget-preview {
  position: relative;
  animation: pulseGlow 2s ease-in-out infinite;
}

.pending-widget-preview::before {
  content: '';
  position: absolute;
  inset: -3px;
  border: 3px solid #3b82f6;
  border-radius: 0.75rem;
  pointer-events: none;
  z-index: 10;
}

.pending-widget-preview::after {
  content: 'PREVIEW';
  position: absolute;
  top: -3px;
  right: -3px;
  background: #3b82f6;
  color: white;
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 0.25rem 0.625rem;
  border-radius: 0 0.5rem 0 0.5rem;
  z-index: 11;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 20px 5px rgba(59, 130, 246, 0.2);
  }
}

.save-widget-banner {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 1.5rem;
  z-index: 900;
  max-width: calc(100vw - 4rem);
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.banner-content svg {
  color: #3b82f6;
  flex-shrink: 0;
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.banner-text strong {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
}

.banner-text span {
  font-size: 0.8125rem;
  color: #6b7280;
}

.banner-actions {
  display: flex;
  gap: 0.75rem;
}

.banner-btn {
  padding: 0.5rem 1.125rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.banner-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.banner-btn.secondary:hover {
  background: #e5e7eb;
}

.banner-btn.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.banner-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>