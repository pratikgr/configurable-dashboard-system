<template>
  <div class="widget-preview-card">
    <div class="card-header">
      <div class="header-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
      </div>
      <div class="header-text">
        <h4 class="card-title">Widget Created</h4>
        <p class="card-subtitle">Ready to add to dashboard</p>
      </div>
    </div>

    <div class="widget-info">
      <div class="info-row">
        <span class="info-label">Type</span>
        <span class="info-value">{{ formatWidgetType(widget.type) }}</span>
      </div>
      
      <div class="info-row">
        <span class="info-label">Title</span>
        <span class="info-value">{{ widget.title }}</span>
      </div>
      
      <div class="info-row">
        <span class="info-label">Query</span>
        <span class="info-value query-id">{{ widget.queryId }}</span>
      </div>
      
      <div v-if="widget.parameters" class="info-row">
        <span class="info-label">Parameters</span>
        <div class="params-list">
          <div v-for="(value, key) in widget.parameters" :key="key" class="param-item">
            <code>{{ key }}</code>: <span>{{ value }}</span>
          </div>
        </div>
      </div>

      <div v-if="dataMapping" class="info-row">
        <span class="info-label">Data Mapping</span>
        <div class="mapping-list">
          <div v-for="(value, key) in dataMapping" :key="key" class="mapping-item">
            <span class="mapping-key">{{ key }}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            <span class="mapping-value">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview visualization hint -->
    <div class="preview-hint">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4M12 8h.01"/>
      </svg>
      <span>A live preview will appear on the dashboard above</span>
    </div>

    <div class="card-actions">
      <button @click="$emit('discard')" class="action-btn secondary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
        <span>Discard</span>
      </button>
      
      <button @click="$emit('save')" class="action-btn primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
        <span>Save to Dashboard</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

defineEmits(['save', 'discard'])

const dataMapping = computed(() => {
  return props.widget.dataMapping || null
})

function formatWidgetType(type) {
  const typeMap = {
    'line-chart': 'Line Chart',
    'bar-chart': 'Bar Chart',
    'pie-chart': 'Pie Chart',
    'data-table': 'Data Table',
    'metric-card': 'Metric Card'
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.widget-preview-card {
  background: white;
  border: 2px solid #3b82f6;
  border-radius: 0.75rem;
  overflow: hidden;
  animation: slideIn 0.4s ease-out;
}

.card-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
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

.widget-info {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: #1f2937;
  font-weight: 500;
}

.query-id {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 0.375rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  display: inline-block;
}

.params-list,
.mapping-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.param-item,
.mapping-item {
  font-size: 0.8125rem;
  color: #374151;
}

.param-item code {
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.mapping-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f9fafb;
  border-radius: 0.375rem;
}

.mapping-key {
  font-weight: 500;
  color: #6b7280;
}

.mapping-value {
  font-family: 'Courier New', monospace;
  color: #3b82f6;
  font-size: 0.8125rem;
}

.preview-hint {
  padding: 0.875rem 1.25rem;
  background: #eff6ff;
  border-top: 1px solid #dbeafe;
  border-bottom: 1px solid #dbeafe;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.8125rem;
  color: #1e40af;
}

.preview-hint svg {
  flex-shrink: 0;
}

.card-actions {
  padding: 1rem 1.25rem;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
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
  transition: all 0.2s;
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
}

.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
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
