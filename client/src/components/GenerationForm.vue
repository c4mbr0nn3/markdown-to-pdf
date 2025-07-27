<script setup>
import { computed, watch } from 'vue'
import { validateTitle } from '@/utils/validation'

const model = defineModel({ required: true })

const titleError = computed(() => {
  return validateTitle(model.value.title)
})

const isValid = computed(() => {
  return model.value.title && titleError.value === null
})

watch(() => isValid.value, (newIsValid) => {
  model.value.isValid = newIsValid
})
</script>

<template>
  <div class="space-y-6">
    <div class="grid grid-cols-2 gap-6">
      <!-- Title Input -->
      <div class="block text-sm font-medium mb-2">
        <UFormField
          label="Document Title"
          required
          :error="titleError"
        >
          <UInput
            v-model="model.title"
            placeholder="Enter document title"
          />
        </UFormField>
      </div>

      <UFormField label="Table of Contents">
        <UCheckbox
          v-model="model.includeToc"
          label="Generate Table of Contents"
          description="Automatically generated from markdown headers"
        />
      </UFormField>

      <!-- Form Summary -->
      <div class="rounded-lg p-4">
        <h4 class="text-sm font-medium mb-2">
          Form Status
        </h4>
        <div class="flex items-center space-x-4">
          <UBadge
            :color="isValid ? 'primary' : 'error'"
            :variant="isValid ? 'soft' : 'solid'"
          >
            Title: {{ isValid ? 'Valid' : 'Invalid' }}
          </UBadge>
          <UBadge
            :color="model.includeToc ? 'primary' : 'warning'"
            variant="soft"
          >
            TOC: {{ model.includeToc ? 'Enabled' : 'Disabled' }}
          </UBadge>
        </div>
      </div>
    </div>
  </div>
</template>
