<template>
  <div class="dashboard-list p-6">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Available Dashboards</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link
          v-for="dashboard in dashboards"
          :key="dashboard.id"
          :to="`/dashboard/${dashboard.id}`"
          class="card hover:shadow-lg transition-shadow cursor-pointer"
        >
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-1">
                {{ dashboard.title }}
              </h3>
              <p class="text-sm text-gray-600">
                {{ dashboard.description }}
              </p>
            </div>
          </div>
        </router-link>
      </div>
      
      <div v-if="dashboards.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-600 text-lg">No dashboards available</p>
        <p class="text-gray-500 text-sm mt-2">Add dashboard configurations to get started</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const dashboards = ref([])

onMounted(async () => {
  // Load available dashboards
  // In production, this would call the backend API
  dashboards.value = [
    {
      id: 'sales-dashboard',
      title: 'Sales Analytics',
      description: 'Comprehensive overview of sales performance and key metrics'
    }
  ]
})
</script>
