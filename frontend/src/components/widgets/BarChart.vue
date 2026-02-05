<template>
  <div class="bar-chart-widget">
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
  config: Object,
  data: [Object, Array],
  loading: Boolean,
  error: String
})

const chartContainer = ref(null)
let chartInstance = null

onMounted(() => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value)
    renderChart()
  }
})

watch(() => props.data, renderChart, { deep: true })

const renderChart = async () => {
  if (!chartInstance || !props.data) return
  await nextTick()

  const { xAxis, series } = props.data
  const { chartOptions = {} } = props.config

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
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
      data: xAxis,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value'
    },
    series: series.map((s, i) => ({
      name: s.name,
      type: 'bar',
      data: s.data,
      itemStyle: {
        color: chartOptions.colors?.[i]
      }
    }))
  })
}
</script>
