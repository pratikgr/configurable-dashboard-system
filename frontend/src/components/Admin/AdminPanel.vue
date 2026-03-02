<template>
  <div class="admin-panel">
    <!-- Header -->
    <div class="admin-header">
      <h1>Admin Panel</h1>
      <p>Manage dashboards, queries, and configurations</p>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="['tab', { active: activeTab === 'dashboards' }]"
        @click="activeTab = 'dashboards'"
      >
        Dashboards
      </button>
      <button 
        :class="['tab', { active: activeTab === 'queries' }]"
        @click="activeTab = 'queries'"
      >
        Queries
      </button>
    </div>

    <!-- Content -->
    <div class="admin-content">
      <!-- Dashboards Tab -->
      <div v-if="activeTab === 'dashboards'" class="tab-content">
        <div class="section-header">
          <h2>Dashboards</h2>
          <button class="btn-primary" @click="showCreateDashboard = true">
            + New Dashboard
          </button>
        </div>

        <div v-if="loading" class="loading">Loading...</div>

        <div v-else class="items-grid">
          <div 
            v-for="dashboard in dashboards" 
            :key="dashboard.id"
            class="item-card"
          >
            <div class="item-header">
              <h3>{{ dashboard.title }}</h3>
              <div class="item-actions">
                <button @click="editDashboard(dashboard)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="deleteDashboard(dashboard.id)" class="btn-icon" title="Delete">
                  🗑️
                </button>
              </div>
            </div>
            <p class="item-description">{{ dashboard.description }}</p>
            <div class="item-meta">
              <span>{{ dashboard.widgets?.length || 0 }} widgets</span>
              <span>{{ dashboard.file }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Queries Tab -->
      <div v-if="activeTab === 'queries'" class="tab-content">
        <div class="section-header">
          <h2>Queries</h2>
          <div class="header-actions">
            <button class="btn-secondary" @click="uploadQueryFile">
              📤 Upload YAML
            </button>
            <button class="btn-primary" @click="showCreateQuery = true">
              + New Query
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading">Loading...</div>

        <div v-else class="items-grid">
          <div 
            v-for="query in queries" 
            :key="query.id"
            class="item-card"
          >
            <div class="item-header">
              <h3>{{ query.id }}</h3>
              <div class="item-actions">
                <button @click="editQuery(query)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="deleteQuery(query.id, query.file)" class="btn-icon" title="Delete">
                  🗑️
                </button>
              </div>
            </div>
            <p class="item-description">{{ query.description }}</p>
            <div class="item-meta">
              <span>{{ query.parameters?.length || 0 }} parameters</span>
              <span>{{ query.file }}</span>
              <span>Cache: {{ query.cache_ttl }}s</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dashboard Modal -->
    <Modal v-if="showCreateDashboard || editingDashboard" @close="closeDashboardModal">
      <h2>{{ editingDashboard ? 'Edit' : 'Create' }} Dashboard</h2>
      
      <div class="form-group">
        <label>Dashboard ID *</label>
        <input 
          v-model="dashboardForm.id" 
          :disabled="!!editingDashboard"
          placeholder="customer-analytics-dashboard"
        />
      </div>

      <div class="form-group">
        <label>Title *</label>
        <input v-model="dashboardForm.title" placeholder="Customer Analytics" />
      </div>

      <div class="form-group">
        <label>Description</label>
        <textarea v-model="dashboardForm.description" rows="3" />
      </div>

      <div class="form-group">
        <label>Widgets (JSON)</label>
        <textarea 
          v-model="dashboardForm.widgetsJson" 
          rows="10" 
          placeholder='[{"id": "widget-1", "type": "bar-chart", ...}]'
          class="code-input"
        />
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" @click="closeDashboardModal">Cancel</button>
        <button class="btn-primary" @click="saveDashboard">Save</button>
      </div>
    </Modal>

    <!-- Create/Edit Query Modal -->
    <Modal v-if="showCreateQuery || editingQuery" @close="closeQueryModal">
      <h2>{{ editingQuery ? 'Edit' : 'Create' }} Query</h2>
      
      <div class="form-group">
        <label>Query ID *</label>
        <input 
          v-model="queryForm.id" 
          :disabled="!!editingQuery"
          placeholder="customer_lifetime_value"
        />
      </div>

      <div class="form-group">
        <label>Description *</label>
        <input v-model="queryForm.description" placeholder="Calculate customer lifetime value" />
      </div>

      <div class="form-group">
        <label>SQL Query *</label>
        <textarea 
          v-model="queryForm.sql" 
          rows="10" 
          placeholder="SELECT * FROM customers..."
          class="code-input"
        />
      </div>

      <div class="form-group">
        <label>Parameters (JSON)</label>
        <textarea 
          v-model="queryForm.parametersJson" 
          rows="5" 
          placeholder='[{"name": "start_date", "type": "date", "default": "30_days_ago"}]'
          class="code-input"
        />
      </div>

      <div class="form-group">
        <label>Cache TTL (seconds)</label>
        <input v-model.number="queryForm.cache_ttl" type="number" min="0" />
      </div>

      <div class="form-group">
        <label>YAML File</label>
        <input v-model="queryForm.file_name" placeholder="custom.yaml" />
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" @click="closeQueryModal">Cancel</button>
        <button class="btn-primary" @click="saveQuery">Save</button>
      </div>
    </Modal>

    <!-- Hidden file input for uploads -->
    <input 
      ref="fileInput" 
      type="file" 
      accept=".yaml,.yml" 
      style="display: none" 
      @change="handleFileUpload"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/plugins/axios'
import Modal from './Modal.vue'

const activeTab = ref('dashboards')
const loading = ref(false)

// Dashboards
const dashboards = ref([])
const showCreateDashboard = ref(false)
const editingDashboard = ref(null)
const dashboardForm = ref({
  id: '',
  title: '',
  description: '',
  widgetsJson: '[]'
})

// Queries
const queries = ref([])
const showCreateQuery = ref(false)
const editingQuery = ref(null)
const queryForm = ref({
  id: '',
  description: '',
  sql: '',
  parametersJson: '[]',
  cache_ttl: 300,
  file_name: 'custom.yaml'
})

const fileInput = ref(null)

onMounted(() => {
  loadDashboards()
  loadQueries()
})

// ==================== DASHBOARDS ====================

async function loadDashboards() {
  loading.value = true
  try {
    const response = await axios.get('/api/dashboards')
    dashboards.value = response.data.dashboards
  } catch (error) {
    console.error('Failed to load dashboards:', error)
    alert('Failed to load dashboards')
  } finally {
    loading.value = false
  }
}

function editDashboard(dashboard) {
  editingDashboard.value = dashboard
  dashboardForm.value = {
    id: dashboard.id,
    title: dashboard.title,
    description: dashboard.description || '',
    widgetsJson: JSON.stringify(dashboard.widgets || [], null, 2)
  }
}

async function saveDashboard() {
  try {
    // Parse widgets
    let widgets = []
    if (dashboardForm.value.widgetsJson.trim()) {
      widgets = JSON.parse(dashboardForm.value.widgetsJson)
    }

    if (editingDashboard.value) {
      // Update
      await axios.put(`/api/admin/dashboards/${editingDashboard.value.id}`, {
        title: dashboardForm.value.title,
        description: dashboardForm.value.description,
        widgets: widgets
      })
    } else {
      // Create
      await axios.post('/api/admin/dashboards', {
        id: dashboardForm.value.id,
        title: dashboardForm.value.title,
        description: dashboardForm.value.description,
        widgets: widgets
      })
    }

    closeDashboardModal()
    loadDashboards()
  } catch (error) {
    console.error('Failed to save dashboard:', error)
    alert(`Failed to save dashboard: ${error.response?.data?.detail || error.message}`)
  }
}

async function deleteDashboard(id) {
  if (!confirm(`Delete dashboard "${id}"?`)) return

  try {
    await axios.delete(`/api/admin/dashboards/${id}`)
    loadDashboards()
  } catch (error) {
    console.error('Failed to delete dashboard:', error)
    alert('Failed to delete dashboard')
  }
}

function closeDashboardModal() {
  showCreateDashboard.value = false
  editingDashboard.value = null
  dashboardForm.value = {
    id: '',
    title: '',
    description: '',
    widgetsJson: '[]'
  }
}

// ==================== QUERIES ====================

async function loadQueries() {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/queries')
    queries.value = response.data.queries
  } catch (error) {
    console.error('Failed to load queries:', error)
    alert('Failed to load queries')
  } finally {
    loading.value = false
  }
}

function editQuery(query) {
  editingQuery.value = query
  queryForm.value = {
    id: query.id,
    description: query.description,
    sql: query.sql,
    parametersJson: JSON.stringify(query.parameters || [], null, 2),
    cache_ttl: query.cache_ttl,
    file_name: query.file
  }
}

async function saveQuery() {
  try {
    // Parse parameters
    let parameters = []
    if (queryForm.value.parametersJson.trim()) {
      parameters = JSON.parse(queryForm.value.parametersJson)
    }

    if (editingQuery.value) {
      // Update
      await axios.put(`/api/admin/queries/${editingQuery.value.id}`, {
        description: queryForm.value.description,
        sql: queryForm.value.sql,
        parameters: parameters,
        cache_ttl: queryForm.value.cache_ttl
      }, {
        params: { file_name: queryForm.value.file_name }
      })
    } else {
      // Create
      await axios.post('/api/admin/queries', {
        id: queryForm.value.id,
        description: queryForm.value.description,
        sql: queryForm.value.sql,
        parameters: parameters,
        cache_ttl: queryForm.value.cache_ttl
      }, {
        params: { file_name: queryForm.value.file_name }
      })
    }

    closeQueryModal()
    loadQueries()
  } catch (error) {
    console.error('Failed to save query:', error)
    alert(`Failed to save query: ${error.response?.data?.detail || error.message}`)
  }
}

async function deleteQuery(id, fileName) {
  if (!confirm(`Delete query "${id}"?`)) return

  try {
    await axios.delete(`/api/admin/queries/${id}`, {
      params: { file_name: fileName }
    })
    loadQueries()
  } catch (error) {
    console.error('Failed to delete query:', error)
    alert('Failed to delete query')
  }
}

function closeQueryModal() {
  showCreateQuery.value = false
  editingQuery.value = null
  queryForm.value = {
    id: '',
    description: '',
    sql: '',
    parametersJson: '[]',
    cache_ttl: 300,
    file_name: 'custom.yaml'
  }
}

function uploadQueryFile() {
  fileInput.value.click()
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post('/api/admin/queries/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    loadQueries()
    alert('Query file uploaded successfully')
  } catch (error) {
    console.error('Failed to upload file:', error)
    alert(`Failed to upload file: ${error.response?.data?.detail || error.message}`)
  }

  // Reset input
  event.target.value = ''
}
</script>

<style scoped>
.admin-panel {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.admin-header p {
  color: #6b7280;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 2rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab:hover {
  color: #374151;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.75rem;
}

.item-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.125rem;
  padding: 0.25rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 1;
}

.item-description {
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.item-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #9ca3af;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-family: inherit;
  font-size: 0.9375rem;
}

.form-group textarea.code-input {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}
</style>
