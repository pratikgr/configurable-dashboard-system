<template>
  <div class="data-table-widget">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 p-4">
      Error: {{ error }}
    </div>
    
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.field"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              @click="sort(column.field)"
            >
              <div class="flex items-center gap-2">
                {{ column.header }}
                <svg v-if="sortField === column.field" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path v-if="sortOrder === 'asc'" d="M5 10l5-5 5 5H5z" />
                  <path v-else d="M5 10l5 5 5-5H5z" />
                </svg>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(row, index) in paginatedData" :key="index" class="hover:bg-gray-50">
            <td
              v-for="column in columns"
              :key="column.field"
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="column.align === 'right' ? 'text-right' : 'text-left'"
            >
              {{ formatCellValue(row[column.field], column.format) }}
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-6 py-4 border-t border-gray-200">
        <div class="text-sm text-gray-700">
          Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, sortedData.length) }} of {{ sortedData.length }} results
        </div>
        <div class="flex gap-2">
          <button
            @click="previousPage"
            :disabled="currentPage === 1"
            class="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatValue } from '@/utils/dataTransformers'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  data: {
    type: Array,
    default: () => []
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

const sortField = ref(null)
const sortOrder = ref('asc')
const currentPage = ref(1)
const pageSize = computed(() => props.config.options?.pageSize || 20)

const columns = computed(() => {
  return props.config.columns || []
})

const sortedData = computed(() => {
  if (!props.data || props.data.length === 0) return []
  
  let data = [...props.data]
  
  if (sortField.value) {
    data.sort((a, b) => {
      const aVal = a[sortField.value]
      const bVal = b[sortField.value]
      
      if (aVal === bVal) return 0
      
      const comparison = aVal > bVal ? 1 : -1
      return sortOrder.value === 'asc' ? comparison : -comparison
    })
  }
  
  return data
})

const totalPages = computed(() => {
  return Math.ceil(sortedData.value.length / pageSize.value)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * pageSize.value
})

const endIndex = computed(() => {
  return startIndex.value + pageSize.value
})

const paginatedData = computed(() => {
  return sortedData.value.slice(startIndex.value, endIndex.value)
})

const sort = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  currentPage.value = 1
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const formatCellValue = (value, format) => {
  return formatValue(value, format)
}
</script>
