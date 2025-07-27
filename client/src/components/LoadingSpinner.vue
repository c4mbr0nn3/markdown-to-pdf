<script>
import { computed } from 'vue'
import { GENERATION_STATES } from '@/utils/constants'

export default {
  name: 'LoadingSpinner',
  props: {
    state: {
      type: String,
      default: GENERATION_STATES.VALIDATING,
      validator: value => Object.values(GENERATION_STATES).includes(value),
    },
    showDetails: {
      type: Boolean,
      default: false,
    },
    showCancel: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['cancel'],
  setup(props) {
    const steps = [
      {
        id: GENERATION_STATES.VALIDATING,
        title: 'Validating Files',
        description: 'Checking file formats and content validity...',
      },
      {
        id: GENERATION_STATES.CREATING_ZIP,
        title: 'Creating Archive',
        description: 'Packaging your files for upload...',
      },
      {
        id: GENERATION_STATES.UPLOADING,
        title: 'Uploading Files',
        description: 'Sending your content to the server...',
      },
      {
        id: GENERATION_STATES.GENERATING,
        title: 'Generating PDF',
        description: 'Converting markdown to PDF with styling...',
      },
      {
        id: GENERATION_STATES.DOWNLOADING,
        title: 'Preparing Download',
        description: 'Finalizing your PDF document...',
      },
    ]

    const currentStepIndex = computed(() => {
      return steps.findIndex(step => step.id === props.state)
    })

    const currentStep = computed(() => {
      const index = currentStepIndex.value
      return index >= 0 ? steps[index] : steps[0]
    })

    const progressPercentage = computed(() => {
      const index = currentStepIndex.value
      return index >= 0 ? ((index + 1) / steps.length) * 100 : 0
    })

    return {
      steps,
      currentStepIndex,
      currentStep,
      progressPercentage,
    }
  },
}
</script>

<template>
  <div class="flex flex-col items-center justify-center p-8">
    <!-- Spinner Animation -->
    <div class="relative">
      <div class="h-12 w-12 rounded-full border-4 border-gray-200 animate-spin border-t-blue-600" />
    </div>

    <!-- Loading Text -->
    <div class="mt-4 text-center">
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        {{ currentStep.title }}
      </h3>
      <p class="text-sm text-gray-600 mb-4">
        {{ currentStep.description }}
      </p>

      <!-- Progress Indicator -->
      <div class="w-64 bg-gray-200 rounded-full h-2">
        <div
          class="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-in-out"
          :style="{ width: `${progressPercentage}%` }"
        />
      </div>

      <p class="text-xs text-gray-500 mt-2">
        Step {{ currentStepIndex + 1 }} of {{ steps.length }}
      </p>
    </div>

    <!-- Detailed Status -->
    <div v-if="showDetails" class="mt-6 max-w-md">
      <div class="bg-gray-50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-900 mb-2">
          Process Details
        </h4>
        <div class="space-y-2">
          <div
            v-for="(step, index) in steps"
            :key="step.id"
            class="flex items-center space-x-2 text-sm"
          >
            <div
              class="w-2 h-2 rounded-full" :class="[
                index < currentStepIndex ? 'bg-green-500'
                : index === currentStepIndex ? 'bg-blue-500'
                  : 'bg-gray-300',
              ]"
            />
            <span
              :class="[
                index <= currentStepIndex ? 'text-gray-900' : 'text-gray-500',
              ]"
            >
              {{ step.title }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Button -->
    <div v-if="showCancel" class="mt-6">
      <UButton
        color="red"
        variant="outline"
        size="sm"
        @click="$emit('cancel')"
      >
        Cancel
      </UButton>
    </div>
  </div>
</template>
