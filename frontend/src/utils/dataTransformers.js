/**
 * Data Transformation Utilities
 * Transform raw query data into format expected by widgets
 */

export const transformData = (data, mapping) => {
  if (!data || !mapping) return data

  // For chart data transformation
  if (mapping.x && mapping.y) {
    return transformForChart(data, mapping)
  }

  // For table data transformation
  if (mapping.columns) {
    return transformForTable(data, mapping)
  }

  // For metric card transformation
  if (mapping.value) {
    return transformForMetric(data, mapping)
  }

  return data
}

export const transformForChart = (data, mapping) => {
  const { x, y, series } = mapping

  if (!series) {
    // Single series
    return {
      xAxis: data.map(row => row[x]),
      yAxis: data.map(row => row[y]),
      series: [{
        name: y,
        data: data.map(row => row[y])
      }]
    }
  }

  // Multiple series
  const seriesMap = {}
  const xAxisSet = new Set()

  data.forEach(row => {
    const seriesKey = row[series]
    const xValue = row[x]
    const yValue = row[y]

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

export const transformForTable = (data, mapping) => {
  if (!mapping.columns) return data

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

export const transformForMetric = (data, mapping) => {
  if (!data || data.length === 0) return null

  const field = mapping.value
  
  // If it's an aggregation function
  if (field.includes('COUNT') || field.includes('SUM') || field.includes('AVG')) {
    const aggregateField = field.match(/\(([^)]+)\)/)?.[1] || Object.keys(data[0])[0]
    
    if (field.startsWith('COUNT')) {
      return data.length
    } else if (field.startsWith('SUM')) {
      return data.reduce((sum, row) => sum + (Number(row[aggregateField]) || 0), 0)
    } else if (field.startsWith('AVG')) {
      const sum = data.reduce((s, row) => s + (Number(row[aggregateField]) || 0), 0)
      return sum / data.length
    }
  }

  // Direct field value from first row
  return data[0]?.[field]
}

export const formatValue = (value, format) => {
  if (value === null || value === undefined) return '-'

  if (!format) return value

  switch (format.type) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: format.currency || 'USD'
      }).format(value)

    case 'number':
      return new Intl.NumberFormat('en-US', {
        notation: format.notation || 'standard',
        maximumFractionDigits: format.decimals || 0
      }).format(value)

    case 'percent':
      return new Intl.NumberFormat('en-US', {
        style: 'percent',
        maximumFractionDigits: format.decimals || 1
      }).format(value / 100)

    case 'date':
      return new Date(value).toLocaleDateString('en-US')

    default:
      return value
  }
}
