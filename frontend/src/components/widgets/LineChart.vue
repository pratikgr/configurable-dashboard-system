<template>
  <div class="line-chart-widget">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 p-4">
      Error: {{ error }}
    </div>
    
    <div v-else-if="!data || !data.xAxis || !data.series" class="text-gray-500 p-4 text-center">
      No data available
    </div>
    
    <div v-else ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  data: {
    type: [Object, Array],
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
    
    console.log('LineChart container size:', { width, height })
    
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
  if (!chartInstance || !props.data || !props.data.xAxis || !props.data.series) {
    console.warn('Cannot render chart:', { 
      hasInstance: !!chartInstance, 
      hasData: !!props.data,
      hasXAxis: !!props.data?.xAxis,
      hasSeries: !!props.data?.series
    })
    return
  }

  try {
    const chartOptions = buildChartOptions()
    chartInstance.setOption(chartOptions, true)
    console.log('LineChart rendered successfully')
  } catch (error) {
    console.error('Error rendering chart:', error)
  }
}

const buildChartOptions = () => {
  const { dataMapping, chartOptions = {} } = props.config
  const { xAxis, series } = props.data

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: series.map(s => s.name),
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxis,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 10,
        formatter: (value) => {
          if (chartOptions.yAxis?.format === 'currency') {
            return '$' + (value / 1000).toFixed(0) + 'k'
          }
          return value.toLocaleString()
        }
      }
    },
    series: series.map((s, index) => ({
      name: s.name,
      type: 'line',
      smooth: chartOptions.smooth ?? true,
      data: s.data,
      areaStyle: chartOptions.showArea ? {} : undefined,
      itemStyle: {
        color: chartOptions.colors?.[index] || undefined
      }
    }))
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
.line-chart-widget {
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
