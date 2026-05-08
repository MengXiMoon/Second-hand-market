export const formatDateTime = (dateTime) => {
  if (!dateTime) return ''

  const date = new Date(dateTime)

  if (isNaN(date.getTime())) {
    return dateTime
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

export const formatDate = (dateTime) => {
  if (!dateTime) return ''

  const date = new Date(dateTime)

  if (isNaN(date.getTime())) {
    return dateTime
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

/**
 * Format cents to yuan display string (e.g., 10000 → "100.00").
 */
export const formatMoney = (cents) => {
  if (cents == null) return '0.00'
  return (cents / 100).toFixed(2)
}

/**
 * Convert yuan (float/string) to cents (integer).
 */
export const toCents = (yuan) => {
  return Math.round(Number(yuan) * 100)
}
