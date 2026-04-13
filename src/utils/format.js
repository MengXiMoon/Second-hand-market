export const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  
  let date
  if (typeof dateTime === 'string' && dateTime.includes('T')) {
    date = new Date(dateTime)
  } else {
    date = new Date(dateTime)
  }
  
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
  
  let date
  if (typeof dateTime === 'string' && dateTime.includes('T')) {
    date = new Date(dateTime)
  } else {
    date = new Date(dateTime)
  }
  
  if (isNaN(date.getTime())) {
    return dateTime
  }
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}
