/**
 * Query Executor Composable
 * Provides methods to execute queries from the backend
 */
import { ref } from 'vue'
import axios from '@/plugins/axios'

export function useQueryExecutor() {
  const loading = ref(false)
  const error = ref(null)

  const executeQuery = async (queryId, parameters = null) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/query/execute', {
        query_id: queryId,
        parameters: parameters
      })

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const listQueries = async () => {
    try {
      const response = await axios.get('/api/query/list')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  const getQueryInfo = async (queryId) => {
    try {
      const response = await axios.get(`/api/query/${queryId}`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  return {
    loading,
    error,
    executeQuery,
    listQueries,
    getQueryInfo
  }
}