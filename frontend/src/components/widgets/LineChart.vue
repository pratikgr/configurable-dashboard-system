<template>
  <div class="line-chart-widget">
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
  props.data && props.data.xAxis?.length > 0 && props.data.series?.length > 0
)

// Watch for data to arrive (loading finishes) then initialize/render
watch(
  () => [props.data, props.loading],
  async ([newData, isLoading]) => {
    if (isLoading || !newData) return
    await nextTick()           // let v-if/v-else settle
    initOrRender()
  },
  { deep: true }
)

onMounted(async () => {
  // In case data is already present on mount (e.g. cached)
  if (!props.loading && hasData.value) {
    await nextTick()
    initOrRender()
  }
})

onUnmounted(cleanup)

const initOrRender = () => {
  if (!chartContainer.value) {
    // container ref is null - shouldn't happen with always-rendered div, but guard anyway
    return
  }

  if (!chartInstance) {
    try {
      chartInstance = echarts.init(chartContainer.value)
      setupResizeObserver()
    } catch (e) {
      console.error('[LineChart] init failed', e)
      return
    }
  }

  renderChart()
}

const renderChart = () => {
  if (!chartInstance || !hasData.value) return

  const { chartOptions = {} } = props.config
  const { xAxis, series } = props.data

  chartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend:  { data: series.map(s => s.name), bottom: 0 },
    grid:    { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxis,
      axisLabel: { rotate: 30, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 11,
        formatter: v =>
          chartOptions.yAxis?.format === 'currency'
            ? '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v)
            : v.toLocaleString()
      }
    },
    series: series.map((s, i) => ({
      name:      s.name,
      type:      'line',
      smooth:    chartOptions.smooth ?? true,
      data:      s.data,
      areaStyle: chartOptions.showArea ? { opacity: 0.15 } : undefined,
      itemStyle: { color: chartOptions.colors?.[i] }
    }))
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

.chart-container.hidden {
  display: none;
}
</style>
