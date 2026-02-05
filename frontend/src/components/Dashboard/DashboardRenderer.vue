<template>
  <div class="dashboard-container p-6">
    <!-- Dashboard Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">{{ config?.title || 'Dashboard' }}</h1>
      <p v-if="config?.description" class="text-gray-600 mt-1">{{ config.description }}</p>
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
              Refresh
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Widgets Grid -->
    <div v-if="config && config.widgets" class="grid grid-cols-12 gap-4">
      <div
        v-for="widget in config.widgets"
        :key="widget.id"
        :class="getGridClass(widget.position)"
      >
        <div class="card h-full">
          <!-- Widget Header -->
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-800">{{ widget.title }}</h3>
            <button 
              @click="refreshWidget(widget.id)"
              class="text-gray-400 hover:text-gray-600"
              :disabled="widgetLoading[widget.id]"
            >
              <svg class="w-5 h-5" :class="{ 'animate-spin': widgetLoading[widget.id] }" 
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>

          <!-- Widget Content -->
          <div class="widget-content">
            <component
              :is="getWidgetComponent(widget.type)"
              :config="widget"
              :data="widgetData[widget.id]"
              :loading="widgetLoading[widget.id]"
              :error="widgetErrors[widget.id]"
            />
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQueryExecutor } from '@/composables/useQueryExecutor'
import { getWidgetComponent } from '@/utils/widgetRegistry'
import { transformData } from '@/utils/dataTransformers'

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

const { executeQuery } = useQueryExecutor()

onMounted(async () => {
  await loadDashboardConfig()
  initializeFilters()
  await loadAllWidgets()
})

const loadDashboardConfig = async () => {
  try {
    // Import dashboard configuration
    const module = await import(`@/config/dashboards/${props.dashboardId}.json`)
    config.value = module.default || module
  } catch (error) {
    console.error('Error loading dashboard config:', error)
  }
}

const initializeFilters = () => {
  if (!config.value?.globalFilters) return
  
  config.value.globalFilters.forEach(filter => {
    filters.value[filter.id] = filter.default || ''
  })
}

const loadAllWidgets = async () => {
  if (!config.value?.widgets) return
  
  const promises = config.value.widgets.map(widget => loadWidgetData(widget.id))
  await Promise.all(promises)
}

const loadWidgetData = async (widgetId) => {
  const widget = config.value.widgets.find(w => w.id === widgetId)
  if (!widget) return

  widgetLoading.value[widgetId] = true
  widgetErrors.value[widgetId] = null

  try {
    const params = buildQueryParams(widget)
    const result = await executeQuery(widget.queryId, params)
    
    // Transform data according to widget's dataMapping
    const transformedData = transformData(result.data, widget.dataMapping)
    widgetData.value[widgetId] = transformedData
    
  } catch (error) {
    console.error(`Error loading widget ${widgetId}:`, error)
    widgetErrors.value[widgetId] = error.message
  } finally {
    widgetLoading.value[widgetId] = false
  }
}

const buildQueryParams = (widget) => {
  const params = {}
  
  // Add global filters
  if (config.value.globalFilters) {
    config.value.globalFilters.forEach(filter => {
      if (filter.applyTo === '*' || filter.applyTo?.includes(widget.id)) {
        params[filter.id] = filters.value[filter.id]
      }
    })
  }
  
  // Add widget-specific parameters
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

const getGridClass = (position) => {
  if (!position) return 'col-span-12'
  
  const { w = 12, h = 4 } = position
  return `col-span-${w}`
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
}

.widget-content {
  min-height: 200px;
}
</style>
