import { ref, computed, readonly } from 'vue'

export function useFileUpload() {
  const files = ref([])
  const isDragOver = ref(false)

  // File type constants
  const MARKDOWN_EXTENSIONS = ['.md', '.markdown']
  const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']
  const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

  const markdownFiles = computed(() => 
    files.value.filter(f => f.type === 'markdown')
  )

  const imageFiles = computed(() => 
    files.value.filter(f => f.type === 'image')
  )

  const isValidFileCount = computed(() => 
    markdownFiles.value.length === 1
  )

  const totalSize = computed(() => 
    files.value.reduce((total, file) => total + file.file.size, 0)
  )

  const isValidTotalSize = computed(() => 
    totalSize.value <= MAX_FILE_SIZE
  )

  const getFileType = (file) => {
    const extension = '.' + file.name.split('.').pop().toLowerCase()
    
    if (MARKDOWN_EXTENSIONS.includes(extension)) {
      return 'markdown'
    } else if (IMAGE_EXTENSIONS.includes(extension)) {
      return 'image'
    }
    return 'unknown'
  }

  const generateFileId = () => {
    return Math.random().toString(36).substr(2, 9)
  }

  const addFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => {
      const fileType = getFileType(file)
      return {
        file,
        id: generateFileId(),
        type: fileType,
        preview: fileType === 'image' ? URL.createObjectURL(file) : null
      }
    }).filter(f => f.type !== 'unknown') // Filter out unsupported files

    // If adding markdown files, ensure we only keep one
    const newMarkdownFiles = newFiles.filter(f => f.type === 'markdown')
    const newImageFiles = newFiles.filter(f => f.type === 'image')

    if (newMarkdownFiles.length > 0) {
      // Remove existing markdown files and add only the first new one
      files.value = files.value.filter(f => f.type !== 'markdown')
      files.value.push(newMarkdownFiles[0])
    }

    // Add all image files
    files.value.push(...newImageFiles)
  }

  const removeFile = (id) => {
    const fileToRemove = files.value.find(f => f.id === id)
    if (fileToRemove && fileToRemove.preview) {
      URL.revokeObjectURL(fileToRemove.preview)
    }
    files.value = files.value.filter(f => f.id !== id)
  }

  const clearFiles = () => {
    // Clean up preview URLs
    files.value.forEach(file => {
      if (file.preview) {
        URL.revokeObjectURL(file.preview)
      }
    })
    files.value = []
  }

  const validateFiles = () => {
    const errors = []
    
    if (markdownFiles.value.length === 0) {
      errors.push('At least one markdown file is required')
    } else if (markdownFiles.value.length > 1) {
      errors.push('Only one markdown file is allowed')
    }

    if (!isValidTotalSize.value) {
      errors.push(`Total file size exceeds ${MAX_FILE_SIZE / (1024 * 1024)}MB limit`)
    }

    return {
      isValid: errors.length === 0 && isValidFileCount.value,
      hasMarkdown: markdownFiles.value.length === 1,
      markdownCount: markdownFiles.value.length,
      errors
    }
  }

  const getFileExtension = (filename) => {
    return filename.split('.').pop().toLowerCase()
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return {
    files: readonly(files),
    isDragOver: readonly(isDragOver),
    markdownFiles,
    imageFiles,
    isValidFileCount,
    totalSize,
    isValidTotalSize,
    addFiles,
    removeFile,
    clearFiles,
    validateFiles,
    getFileExtension,
    formatFileSize,
    setDragOver: (value) => { isDragOver.value = value }
  }
}