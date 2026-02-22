<template>
  <div class="data-preview-card">
    <div class="card-header">
      <div class="header-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 3h7v7H3z"/>
          <path d="M14 3h7v7h-7z"/>
          <path d="M14 14h7v7h-7z"/>
          <path d="M3 14h7v7H3z"/>
        </svg>
      </div>
      <div class="header-text">
        <h4 class="card-title">Query Results</h4>
        <p class="card-subtitle">
          Showing {{ data.rows?.length || 0 }} of {{ data.total || 0 }} rows
        </p>
      </div>
      
      <button @click="$emit('close')" class="close-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Data Table -->
    <div class="data-table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in data.columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in data.rows" :key="idx">
            <td v-for="col in data.columns" :key="col">
              {{ formatValue(row[col]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Actions -->
    <div class="card-actions">
      <button @click="$emit('add-widget')" class="action-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        <span>Add as Widget</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    required: true
  }
})

defineEmits(['add-widget', 'close'])

function formatValue(value) {
  if (value === null || value === undefined) {
    return '-'
  }
  
  if (typeof value === 'number') {
    // Format large numbers
    if (value > 1000) {
      return value.toLocaleString()
    }
    // Format decimals
    if (value % 1 !== 0) {
      return value.toFixed(2)
    }
  }
  
  if (typeof value === 'boolean') {
    return value ? '✓' : '✗'
  }
  
  return String(value)
}
</script>

<style scoped>
.data-preview-card {
  background: white;
  border: 2px solid #10b981;
  border-radius: 0.75rem;
  overflow: hidden;
  animation: slideIn 0.4s ease-out;
}

.card-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
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

.header-text {
  flex: 1;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}

.card-subtitle {
  font-size: 0.75rem;
  opacity: 0.9;
  margin: 0.125rem 0 0 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.data-table-container {
  max-height: 300px;
  overflow: auto;
  border-bottom: 1px solid #e5e7eb;
}

.data-table {
  width: 100%;
  font-size: 0.8125rem;
  border-collapse: collapse;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: #f9fafb;
  z-index: 1;
}

.data-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  color: #1f2937;
  border-bottom: 1px solid #f3f4f6;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.card-actions {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: center;
}

.action-btn {
  padding: 0.625rem 1.125rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  transition: all 0.2s;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
