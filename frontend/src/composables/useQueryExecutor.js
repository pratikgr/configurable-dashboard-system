/**
 * Query Executor Composable
 * Provides methods to execute queries from the backend
 */
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useQueryExecutor() {
  const loading = ref(false)
  const error = ref(null)

  const executeQuery = async (queryId, parameters = null) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_BASE_URL}/api/query/execute`, {
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
      const response = await axios.get(`${API_BASE_URL}/api/query/list`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  const getQueryInfo = async (queryId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/query/${queryId}`)
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
