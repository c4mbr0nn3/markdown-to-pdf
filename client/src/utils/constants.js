export const FILE_TYPES = {
  MARKDOWN: 'markdown',
  IMAGE: 'image',
  UNKNOWN: 'unknown',
}

export const FILE_EXTENSIONS = {
  MARKDOWN: ['.md', '.markdown'],
  IMAGE: ['.png', '.jpg', '.jpeg'],
}

export const FILE_LIMITS = {
  MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
  MAX_TOTAL_SIZE: 50 * 1024 * 1024, // 50MB
  MAX_TITLE_LENGTH: 200,
  MIN_TITLE_LENGTH: 1,
}

export const API_ENDPOINTS = {
  HEALTH: 'health',
  INFO: 'api/v1/info',
  STATUS: 'api/v1/status',
  CONVERT: 'api/v1/convert',
}

export const ERROR_CODES = {
  INVALID_FILE_FORMAT: 'INVALID_FILE_FORMAT',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  NO_MARKDOWN_FOUND: 'NO_MARKDOWN_FOUND',
  INVALID_MARKDOWN: 'INVALID_MARKDOWN',
  IMAGE_NOT_FOUND: 'IMAGE_NOT_FOUND',
  PDF_GENERATION_FAILED: 'PDF_GENERATION_FAILED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
}

export const DRAG_STATES = {
  IDLE: 'idle',
  DRAGOVER: 'dragover',
  DROPPING: 'dropping',
}

export const GENERATION_STATES = {
  IDLE: 'idle',
  VALIDATING: 'validating',
  CREATING_ZIP: 'creating_zip',
  UPLOADING: 'uploading',
  GENERATING: 'generating',
  DOWNLOADING: 'downloading',
  SUCCESS: 'success',
  ERROR: 'error',
}

export const SUPPORTED_MIME_TYPES = {
  'text/markdown': FILE_TYPES.MARKDOWN,
  'text/plain': FILE_TYPES.MARKDOWN, // Some systems report .md as text/plain
  'image/png': FILE_TYPES.IMAGE,
  'image/jpeg': FILE_TYPES.IMAGE,
  'image/jpg': FILE_TYPES.IMAGE,
}

export const DEFAULT_VALUES = {
  TITLE: '',
  INCLUDE_TOC: true,
  API_REFRESH_INTERVAL: 30000, // 30 seconds
  DEBOUNCE_DELAY: 300, // 300ms
}
