<template>
  <div id="app">
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center gap-3">
              <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <span class="text-xl font-bold text-gray-900">Dashboard System</span>
            </router-link>
          </div>
          
          <div class="flex items-center gap-4">
            <router-link
              to="/"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Dashboards
            </router-link>
            
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              API Docs
            </a>
          </div>
        </div>
      </div>
    </nav>
    
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// Main app component
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: #f9fafb;
}

main {
  min-height: calc(100vh - 4rem);
}
</style>
