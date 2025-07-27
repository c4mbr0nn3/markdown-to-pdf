<script setup>
import { computed } from 'vue'
import { GENERATION_STATES } from '@/utils/constants'

const props = defineProps({
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
})

const emit = defineEmits(['cancel'])

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
</script>

<template>
  <div class="flex flex-col items-center justify-center px-8">
    <!-- Loading Text -->
    <div class="text-center">
      <h3 class="text-lg font-medium mb-2">
        {{ currentStep.title }}
      </h3>
      <p class="text-sm text-gray-400 mb-4">
        {{ currentStep.description }}
      </p>

      <!-- Progress Indicator -->
      <UProgress v-model="progressPercentage" />

      <p class="text-xs text-gray-500 mt-2">
        Step {{ currentStepIndex + 1 }} of {{ steps.length }}
      </p>
    </div>

    <!-- Detailed Status -->
    <div v-if="showDetails" class="mt-6 max-w-md">
      <div class=" p-4">
        <h4 class="text-sm font-medium mb-2">
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
            <span :class="[index <= currentStepIndex ? 'text-green-500' : '']">
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
        @click="emit('cancel')"
      >
        Cancel
      </UButton>
    </div>
  </div>
</template>
