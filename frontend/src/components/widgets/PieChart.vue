<template>
  <div class="pie-chart-widget">
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
  data: Array,
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

  const { dataMapping } = props.config
  const pieData = props.data.map(row => ({
    name: row[dataMapping.name],
    value: row[dataMapping.value]
  }))

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '50%',
      data: pieData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}
</script>
