import ky from 'ky'

export function useApi() {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const client = ky.create({ prefixUrl: baseUrl })

  const health = async () => {
    try {
      return await client.get('health').json()
    }
    catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  const info = async () => {
    try {
      return await client.get('api/v1/info').json()
    }
    catch (error) {
      console.error('Failed to get API info:', error)
      throw error
    }
  }

  const status = async () => {
    try {
      return await client.get('api/v1/status').json()
    }
    catch (error) {
      console.error('Failed to get API status:', error)
      throw error
    }
  }

  const convert = async (formData) => {
    try {
      return await client.post('api/v1/convert', {
        body: formData,
        timeout: 120000, // 2 minutes timeout for PDF generation
      }).blob()
    }
    catch (error) {
      console.error('PDF conversion failed:', error)
      throw error
    }
  }

  return {
    health,
    info,
    status,
    convert,
  }
}
