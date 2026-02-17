/**
 * Universal Data Transformation Utilities
 * Transform raw query data into ANY widget format - NO CODE CHANGES NEEDED
 * Just change widget type in config!
 */

/**
 * Main transformation function - routes to appropriate transformer
 */
export const transformData = (data, mapping, widgetType = null) => {
  if (!data || !mapping) return data

  // Auto-detect widget type from mapping if not provided
  if (!widgetType) {
    widgetType = detectWidgetType(mapping)
  }

  console.log('Transforming data for widget type:', widgetType, 'Data length:', data.length)

  // Route to appropriate transformer
  switch (widgetType) {
    case 'line-chart':
    case 'bar-chart':
    case 'area-chart':
      return transformForChart(data, mapping)
    
    case 'pie-chart':
    case 'donut-chart':
      return transformForPieChart(data, mapping)
    
    case 'data-table':
      return transformForTable(data, mapping)
    
    case 'metric-card':
    case 'kpi-card':
      return transformForMetric(data, mapping)
    
    default:
      // If mapping has chart properties, transform for chart
      if (mapping.x && mapping.y) {
        return transformForChart(data, mapping)
      }
      // If mapping has table properties, transform for table
      if (mapping.columns) {
        return transformForTable(data, mapping)
      }
      // If mapping has metric properties, transform for metric
      if (mapping.value) {
        return transformForMetric(data, mapping)
      }
      // If mapping has pie properties, transform for pie
      if (mapping.name && mapping.value) {
        return transformForPieChart(data, mapping)
      }
      // Default: return as-is
      return data
  }
}

/**
 * Detect widget type from mapping structure
 */
const detectWidgetType = (mapping) => {
  if (mapping.x && mapping.y) return 'chart'
  if (mapping.name && mapping.value && !mapping.x) return 'pie-chart'
  if (mapping.columns) return 'data-table'
  if (mapping.value) return 'metric-card'
  return 'unknown'
}

/**
 * Transform for ANY chart type (line, bar, area)
 * Handles both single and multiple series
 */
export const transformForChart = (data, mapping) => {
  const { x, y, series } = mapping

  if (!x || !y) {
    console.warn('Chart mapping missing x or y field')
    return { xAxis: [], series: [] }
  }

  if (!series) {
    // Single series
    return {
      xAxis: data.map(row => row[x]),
      yAxis: data.map(row => row[y]),
      series: [{
        name: y,
        data: data.map(row => Number(row[y]) || 0)
      }]
    }
  }

  // Multiple series
  const seriesMap = {}
  const xAxisSet = new Set()

  data.forEach(row => {
    const seriesKey = row[series]
    const xValue = row[x]
    const yValue = Number(row[y]) || 0

    if (!seriesMap[seriesKey]) {
      seriesMap[seriesKey] = {}
    }

    seriesMap[seriesKey][xValue] = yValue
    xAxisSet.add(xValue)
  })

  const xAxisData = Array.from(xAxisSet).sort()
  const seriesData = Object.entries(seriesMap).map(([name, values]) => ({
    name,
    data: xAxisData.map(x => values[x] || 0)
  }))

  return {
    xAxis: xAxisData,
    series: seriesData
  }
}

/**
 * Transform for Pie/Donut charts
 * Can convert from:
 * - Table data (any two columns)
 * - Chart data (aggregates y values by category)
 * - Existing pie data
 */
export const transformForPieChart = (data, mapping) => {
  // If data is already in pie format, return it
  if (Array.isArray(data) && data[0]?.name && data[0]?.value) {
    return data
  }

  // Standard pie transformation
  if (mapping.name && mapping.value) {
    return data.map(row => ({
      name: row[mapping.name],
      value: Number(row[mapping.value]) || 0
    }))
  }

  // Convert from chart data (x/y) to pie data
  if (mapping.x && mapping.y) {
    return data.map(row => ({
      name: row[mapping.x],
      value: Number(row[mapping.y]) || 0
    }))
  }

  console.warn('Pie chart mapping requires name and value fields')
  return data
}

/**
 * Transform for Tables
 * Can display data from ANY query format
 */
export const transformForTable = (data, mapping) => {
  if (!mapping.columns) {
    // No column mapping - return all columns
    return data
  }

  // Filter and reorder columns
  return data.map(row => {
    const transformed = {}
    mapping.columns.forEach(col => {
      const field = typeof col === 'string' ? col : col.field
      transformed[field] = row[field]
    })
    return transformed
  })
}

/**
 * Transform for Metric/KPI cards
 * Can aggregate from ANY data source
 */
export const transformForMetric = (data, mapping) => {
  if (!data || data.length === 0) return null

  const field = mapping.value
  
  // If it's an aggregation function
  if (field.includes('COUNT') || field.includes('SUM') || field.includes('AVG') || 
      field.includes('MAX') || field.includes('MIN')) {
    
    const aggregateField = field.match(/\(([^)]+)\)/)?.[1] || Object.keys(data[0])[0]
    
    if (field.startsWith('COUNT')) {
      return data.length
    } else if (field.startsWith('SUM')) {
      return data.reduce((sum, row) => sum + (Number(row[aggregateField]) || 0), 0)
    } else if (field.startsWith('AVG')) {
      const sum = data.reduce((s, row) => s + (Number(row[aggregateField]) || 0), 0)
      return sum / data.length
    } else if (field.startsWith('MAX')) {
      return Math.max(...data.map(row => Number(row[aggregateField]) || 0))
    } else if (field.startsWith('MIN')) {
      return Math.min(...data.map(row => Number(row[aggregateField]) || 0))
    }
  }

  // Direct field value from first row
  return data[0]?.[field]
}

/**
 * Format values for display
 */
export const formatValue = (value, format) => {
  if (value === null || value === undefined) return '-'

  if (!format) return value

  switch (format.type) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: format.currency || 'USD',
        minimumFractionDigits: format.decimals ?? 2,
        maximumFractionDigits: format.decimals ?? 2
      }).format(value)

    case 'number':
      return new Intl.NumberFormat('en-US', {
        notation: format.notation || 'standard',
        minimumFractionDigits: format.decimals ?? 0,
        maximumFractionDigits: format.decimals ?? 0
      }).format(value)

    case 'percent':
      return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: format.decimals ?? 1,
        maximumFractionDigits: format.decimals ?? 1
      }).format(value / 100)

    case 'date':
      return new Date(value).toLocaleDateString('en-US', format.options || {})
    
    case 'datetime':
      return new Date(value).toLocaleString('en-US', format.options || {})

    case 'compact':
      if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M'
      } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K'
      }
      return value.toString()

    default:
      return value
  }
}

/**
 * UNIVERSAL ADAPTER: Convert any widget type to any other widget type!
 * Examples:
 * - Table → Line Chart
 * - Bar Chart → Pie Chart
 * - Line Chart → Table
 * - Pie Chart → Bar Chart
 */
export const convertWidgetType = (data, currentMapping, fromType, toType) => {
  console.log(`Converting from ${fromType} to ${toType}`)

  // Get the raw data format first
  let rawData = data

  // Convert to intermediate format (array of objects)
  if (fromType === 'line-chart' || fromType === 'bar-chart') {
    // Chart to raw data
    if (data.xAxis && data.series) {
      rawData = data.xAxis.map((x, i) => ({
        x: x,
        y: data.series[0].data[i]
      }))
    }
  } else if (fromType === 'pie-chart') {
    // Pie to raw data
    if (Array.isArray(data)) {
      rawData = data.map(item => ({
        name: item.name,
        value: item.value
      }))
    }
  }

  // Transform to target format
  const newMapping = adaptMapping(currentMapping, fromType, toType)
  return transformData(rawData, newMapping, toType)
}

/**
 * Adapt mapping when converting between widget types
 */
const adaptMapping = (currentMapping, fromType, toType) => {
  const newMapping = { ...currentMapping }

  // Table → Chart
  if (fromType === 'data-table' && (toType === 'line-chart' || toType === 'bar-chart')) {
    if (currentMapping.columns && currentMapping.columns.length >= 2) {
      newMapping.x = currentMapping.columns[0].field || currentMapping.columns[0]
      newMapping.y = currentMapping.columns[1].field || currentMapping.columns[1]
    }
  }

  // Chart → Pie
  if ((fromType === 'line-chart' || fromType === 'bar-chart') && toType === 'pie-chart') {
    newMapping.name = currentMapping.x
    newMapping.value = currentMapping.y
  }

  // Pie → Chart
  if (fromType === 'pie-chart' && (toType === 'line-chart' || toType === 'bar-chart')) {
    newMapping.x = currentMapping.name
    newMapping.y = currentMapping.value
  }

  // Chart → Table
  if ((fromType === 'line-chart' || fromType === 'bar-chart') && toType === 'data-table') {
    newMapping.columns = [
      { field: currentMapping.x, header: currentMapping.x },
      { field: currentMapping.y, header: currentMapping.y }
    ]
  }

  return newMapping
}
