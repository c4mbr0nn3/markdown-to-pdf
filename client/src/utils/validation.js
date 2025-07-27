export function validateTitle(title) {
  const errors = []
  
  if (!title || !title.trim()) {
    errors.push('Title is required')
  } else {
    const trimmedTitle = title.trim()
    
    if (trimmedTitle.length < 1) {
      errors.push('Title cannot be empty')
    } else if (trimmedTitle.length > 200) {
      errors.push('Title cannot exceed 200 characters')
    }
    
    // Check for invalid characters
    const invalidChars = /[<>:"/\\|?*]/
    if (invalidChars.test(trimmedTitle)) {
      errors.push('Title contains invalid characters: < > : " / \\ | ? *')
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    sanitized: title ? title.trim() : ''
  }
}

export function validateFileType(file) {
  const allowedTypes = {
    markdown: ['.md', '.markdown'],
    image: ['.png', '.jpg', '.jpeg']
  }
  
  const fileName = file.name.toLowerCase()
  const extension = '.' + fileName.split('.').pop()
  
  for (const [type, extensions] of Object.entries(allowedTypes)) {
    if (extensions.includes(extension)) {
      return { isValid: true, type, extension }
    }
  }
  
  return { 
    isValid: false, 
    type: 'unknown', 
    extension,
    error: `Unsupported file type. Allowed: ${Object.values(allowedTypes).flat().join(', ')}`
  }
}

export function validateFileSize(file, maxSize = 50 * 1024 * 1024) {
  return {
    isValid: file.size <= maxSize,
    size: file.size,
    maxSize,
    error: file.size > maxSize ? `File size ${formatFileSize(file.size)} exceeds maximum ${formatFileSize(maxSize)}` : null
  }
}

export function validateTotalSize(files, maxSize = 50 * 1024 * 1024) {
  const totalSize = files.reduce((sum, file) => sum + file.size, 0)
  
  return {
    isValid: totalSize <= maxSize,
    totalSize,
    maxSize,
    error: totalSize > maxSize ? `Total size ${formatFileSize(totalSize)} exceeds maximum ${formatFileSize(maxSize)}` : null
  }
}

export function sanitizeFilename(filename) {
  // Remove path separators and dangerous characters
  const safeChars = /[^a-zA-Z0-9-_\.]/g
  let sanitized = filename.replace(safeChars, '_')
  
  // Ensure it doesn't start with a dot or hyphen
  if (/^[.-]/.test(sanitized)) {
    sanitized = 'file_' + sanitized
  }
  
  // Ensure it's not empty
  if (!sanitized || sanitized === '_') {
    sanitized = 'document.pdf'
  }
  
  // Limit length
  if (sanitized.length > 100) {
    const parts = sanitized.split('.')
    if (parts.length > 1) {
      const ext = parts.pop()
      const name = parts.join('.')
      sanitized = name.substring(0, 100 - ext.length - 1) + '.' + ext
    } else {
      sanitized = sanitized.substring(0, 100)
    }
  }
  
  return sanitized
}

export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}