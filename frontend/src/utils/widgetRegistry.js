/**
 * Widget Registry
 * Maps widget types to Vue components
 */
import LineChart from '@/components/widgets/LineChart.vue'
import BarChart from '@/components/widgets/BarChart.vue'
import PieChart from '@/components/widgets/PieChart.vue'
import DataTable from '@/components/widgets/DataTable.vue'
import MetricCard from '@/components/widgets/MetricCard.vue'

export const widgetRegistry = {
  'line-chart': LineChart,
  'bar-chart': BarChart,
  'pie-chart': PieChart,
  'data-table': DataTable,
  'metric-card': MetricCard,
  'default': MetricCard
}

export const getWidgetComponent = (type) => {
  return widgetRegistry[type] || widgetRegistry.default
}

export const registerWidget = (type, component) => {
  widgetRegistry[type] = component
}
