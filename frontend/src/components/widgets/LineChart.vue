<template>
  <div class="line-chart-widget">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 p-4">
      Error: {{ error }}
    </div>
    
    <div v-else ref="chartContainer" class="w-full h-80"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
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

onMounted(() => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    renderChart()
  }
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })

const renderChart = async () => {
  if (!chartInstance || !props.data) return

  await nextTick()

  const chartOptions = buildChartOptions()
  chartInstance.setOption(chartOptions)

  // Resize on window resize
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
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
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxis,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value) => {
          if (chartOptions.yAxis?.format === 'currency') {
            return '$' + value.toLocaleString()
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
</script>
