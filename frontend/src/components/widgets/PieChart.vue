<template>
  <div class="pie-chart-widget">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 p-4">
      Error: {{ error }}
    </div>
    
    <div v-else-if="!data || !Array.isArray(data) || data.length === 0" class="text-gray-500 p-4 text-center">
      No data available
    </div>
    
    <div v-else ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  config: Object,
  data: Array,
  loading: Boolean,
  error: String
})

const chartContainer = ref(null)
let chartInstance = null
let resizeObserver = null

onMounted(async () => {
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 100))
  initChart()
})

onUnmounted(() => {
  cleanup()
})

watch(() => props.data, async () => {
  await nextTick()
  renderChart()
}, { deep: true })

const initChart = () => {
  if (!chartContainer.value) {
    console.warn('Chart container not found')
    return
  }
  
  // Wait for container to have size
  const checkSize = () => {
    const width = chartContainer.value?.clientWidth
    const height = chartContainer.value?.clientHeight
    
    console.log('PieChart container size:', { width, height })
    
    if (!width || !height || width === 0 || height === 0) {
      console.warn('Container has no size, retrying...')
      setTimeout(checkSize, 100)
      return
    }
    
    try {
      chartInstance = echarts.init(chartContainer.value)
      renderChart()
      
      // Setup resize observer
      setupResizeObserver()
      
    } catch (error) {
      console.error('Error initializing chart:', error)
    }
  }
  
  checkSize()
}

const setupResizeObserver = () => {
  if (!chartContainer.value || !window.ResizeObserver) return
  
  resizeObserver = new ResizeObserver(() => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
  
  resizeObserver.observe(chartContainer.value)
}

const renderChart = () => {
  if (!chartInstance || !props.data || !Array.isArray(props.data) || props.data.length === 0) {
    console.warn('Cannot render chart:', { 
      hasInstance: !!chartInstance, 
      hasData: !!props.data,
      isArray: Array.isArray(props.data),
      length: props.data?.length
    })
    return
  }

  try {
    const { dataMapping } = props.config
    
    const pieData = props.data.map(row => ({
      name: row[dataMapping.name],
      value: row[dataMapping.value]
    }))

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'middle'
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],  // Donut chart
        center: ['60%', '50%'],   // Move right to make room for legend
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: pieData
      }]
    }

    chartInstance.setOption(option, true)
    console.log('PieChart rendered successfully')
  } catch (error) {
    console.error('Error rendering chart:', error)
  }
}

const cleanup = () => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}
</script>

<style scoped>
.pie-chart-widget {
  width: 100%;
  height: 100%;
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 300px;
}
</style>
