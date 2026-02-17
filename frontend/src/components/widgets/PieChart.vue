<template>
  <div class="pie-chart-widget">
    <div v-if="loading" class="flex justify-center items-center h-full">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="error" class="flex items-center justify-center h-full text-red-500 p-4">
      {{ error }}
    </div>

    <div v-else-if="!hasData" class="flex items-center justify-center h-full text-gray-400 p-4">
      No data available
    </div>

    <!-- Always rendered, hidden via CSS when no data - this keeps the ref alive -->
    <div
      ref="chartContainer"
      class="chart-container"
      :class="{ hidden: loading || error || !hasData }"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  config: { type: Object, required: true },
  data:    { type: [Object, Array], default: null },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: null }
})

const chartContainer = ref(null)
let chartInstance    = null
let resizeObserver   = null

const hasData = computed(() =>
  Array.isArray(props.data) && props.data.length > 0
)

watch(
  () => [props.data, props.loading],
  async ([newData, isLoading]) => {
    if (isLoading || !newData) return
    await nextTick()
    initOrRender()
  },
  { deep: true }
)

onMounted(async () => {
  if (!props.loading && hasData.value) {
    await nextTick()
    initOrRender()
  }
})

onUnmounted(cleanup)

const initOrRender = () => {
  if (!chartContainer.value) return

  if (!chartInstance) {
    try {
      chartInstance = echarts.init(chartContainer.value)
      setupResizeObserver()
    } catch (e) {
      console.error('[PieChart] init failed', e)
      return
    }
  }

  renderChart()
}

const renderChart = () => {
  if (!chartInstance || !hasData.value) return

  const { dataMapping } = props.config
  const pieData = props.data.map(row => ({
    name:  row[dataMapping.name],
    value: Number(row[dataMapping.value]) || 0
  }))

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left:   'left',
      top:    'middle'
    },
    series: [{
      type:   'pie',
      radius: ['35%', '65%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor:  '#fff',
        borderWidth:  2
      },
      label: {
        show:      true,
        formatter: '{b}: {d}%',
        fontSize:  11
      },
      emphasis: {
        label: { show: true, fontSize: 13, fontWeight: 'bold' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' }
      },
      data: pieData
    }]
  }, true)
}

const setupResizeObserver = () => {
  if (!chartContainer.value || !window.ResizeObserver) return
  resizeObserver = new ResizeObserver(() => chartInstance?.resize())
  resizeObserver.observe(chartContainer.value)
}

function cleanup () {
  resizeObserver?.disconnect()
  resizeObserver = null
  chartInstance?.dispose()
  chartInstance = null
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

.chart-container.hidden {
  display: none;
}
</style>
