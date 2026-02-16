<template>
  <div class="metric-card-widget">
    <div v-if="loading" class="flex justify-center items-center h-32">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 p-4">
      Error: {{ error }}
    </div>
    
    <div v-else class="flex items-center justify-between">
      <div class="flex-1">
        <div class="text-3xl font-bold" :class="textColorClass">
          {{ formattedValue }}
        </div>
        <div v-if="change" class="mt-2 flex items-center gap-2">
          <span :class="changeColorClass" class="text-sm font-medium flex items-center gap-1">
            <svg v-if="changeValue > 0" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="changeValue < 0" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            {{ Math.abs(changeValue) }}%
          </span>
          <span class="text-sm text-gray-500">vs previous period</span>
        </div>
      </div>
      
      <div v-if="icon" class="flex-shrink-0">
        <div class="w-12 h-12 rounded-full flex items-center justify-center" :class="iconBgClass">
          <svg class="w-6 h-6" :class="iconColorClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="icon === 'users'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            <path v-else-if="icon === 'chart'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            <path v-else-if="icon === 'dollar'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatValue } from '@/utils/dataTransformers'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  data: {
    type: [Number, String, Object],
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

const formattedValue = computed(() => {
  if (props.data === null || props.data === undefined) return '-'
  return formatValue(props.data, props.config.format)
})

const icon = computed(() => props.config.icon)
const color = computed(() => props.config.color || 'blue')

const change = computed(() => props.config.dataMapping?.change)
const changeValue = computed(() => {
  // Calculate change percentage (mock for now)
  return 12.5
})

const textColorClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600',
    purple: 'text-purple-600'
  }
  return colors[color.value] || colors.blue
})

const iconBgClass = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    red: 'bg-red-100',
    yellow: 'bg-yellow-100',
    purple: 'bg-purple-100'
  }
  return colors[color.value] || colors.blue
})

const iconColorClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600',
    purple: 'text-purple-600'
  }
  return colors[color.value] || colors.blue
})

const changeColorClass = computed(() => {
  return changeValue.value >= 0 ? 'text-green-600' : 'text-red-600'
})
</script>
