<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useApi } from '@/composables/useApi'
import { DEFAULT_VALUES } from '@/utils/constants'

const api = useApi()
const health = ref(null)
const apiInfo = ref(null)
const systemStatus = ref(null)
const error = ref(null)
const isLoading = ref(true)

let refreshInterval = null

const healthStatus = computed(() => {
  if (isLoading.value) {
    return {
      color: 'neutral',
      variant: 'soft',
      text: 'Checking...',
    }
  }

  if (error.value) {
    return {
      color: 'error',
      variant: 'solid',
      text: 'Offline',
    }
  }

  if (health.value?.status === 'healthy') {
    return {
      color: 'primary',
      variant: 'solid',
      text: 'Online',
    }
  }

  return {
    color: 'warning',
    variant: 'solid',
    text: 'Unknown',
  }
})

async function fetchApiData() {
  try {
    error.value = null

    // Fetch all API data in parallel
    const [healthData, infoData, statusData] = await Promise.all([
      api.health().catch(() => null),
      api.info().catch(() => null),
      api.status().catch(() => null),
    ])

    health.value = healthData
    apiInfo.value = infoData
    systemStatus.value = statusData

    // If none of the requests succeeded, set an error
    if (!healthData && !infoData && !statusData) {
      throw new Error('All API endpoints are unreachable')
    }
  }
  catch (err) {
    console.error('Failed to fetch API data:', err)
    error.value = {
      title: 'API Connection Error',
      message: 'Unable to connect to the API. Please check your connection and try again.',
    }
  }
  finally {
    isLoading.value = false
  }
}

function startRefreshInterval() {
  refreshInterval = setInterval(() => {
    fetchApiData()
  }, DEFAULT_VALUES.API_REFRESH_INTERVAL)
}

function stopRefreshInterval() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

onMounted(() => {
  fetchApiData()
  startRefreshInterval()
})

onUnmounted(() => {
  stopRefreshInterval()
})
</script>

<template>
  <div class="mb-6">
    <UCard>
      <div class="flex items-center justify-between flex-wrap gap-4">
        <!-- API Health Status -->
        <div class="flex items-center space-x-3">
          <UBadge
            :color="healthStatus.color"
            :variant="healthStatus.variant"
            size="lg"
          >
            {{ healthStatus.text }}
          </UBadge>
          <span class="text-sm">API Status</span>
        </div>

        <!-- API Info -->
        <div v-if="apiInfo" class="flex items-center space-x-4 text-sm">
          <span>Max: {{ apiInfo.max_file_size }}</span>
          <span>Images: {{ apiInfo.supported_images.join(', ') }}</span>
          <span>v{{ apiInfo.version }}</span>
        </div>

        <!-- System Status -->
        <div v-if="systemStatus" class="flex items-center space-x-3">
          <UBadge
            :color="systemStatus.environment === 'development' ? 'warning' : 'secondary'"
            variant="soft"
          >
            {{ systemStatus.environment }}
          </UBadge>
          <span class="text-sm">Uptime: {{ systemStatus.uptime }}</span>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="mt-4">
        <UAlert
          color="error"
          variant="soft"
          :title="error.title"
          :description="error.message"
        />
      </div>
    </UCard>
  </div>
</template>
