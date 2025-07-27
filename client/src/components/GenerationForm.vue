<script>
import { computed, ref, watch } from 'vue'
import { DEFAULT_VALUES } from '@/utils/constants'
import { debounce, validateTitle } from '@/utils/validation'

export default {
  name: 'GenerationForm',
  emits: ['formChange'],
  setup(props, { emit }) {
    const title = ref(DEFAULT_VALUES.TITLE)
    const includeToc = ref(DEFAULT_VALUES.INCLUDE_TOC)

    const titleValidation = computed(() => {
      return validateTitle(title.value)
    })

    const isFormValid = computed(() => {
      return titleValidation.value.isValid && title.value.trim().length > 0
    })

    // Debounced title change handler
    const debouncedEmit = debounce(() => {
      emit('formChange', {
        title: titleValidation.value.sanitized,
        includeToc: includeToc.value,
        isValid: isFormValid.value,
      })
    }, DEFAULT_VALUES.DEBOUNCE_DELAY)

    const onTitleChange = () => {
      debouncedEmit()
    }

    // Watch for TOC changes
    watch(includeToc, () => {
      emit('formChange', {
        title: titleValidation.value.sanitized,
        includeToc: includeToc.value,
        isValid: isFormValid.value,
      })
    })

    // Initial emit
    emit('formChange', {
      title: titleValidation.value.sanitized,
      includeToc: includeToc.value,
      isValid: isFormValid.value,
    })

    return {
      title,
      includeToc,
      titleValidation,
      isFormValid,
      onTitleChange,
    }
  },
}
</script>

<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Title Input -->
      <div>
        <label class="block text-sm font-medium mb-2">
          Document Title *
        </label>
        <UInput
          v-model="title"
          placeholder="Enter document title"
          :error="titleValidation.errors.length > 0"
          size="lg"
          @input="onTitleChange"
        />
        <div v-if="titleValidation.errors.length > 0" class="mt-1">
          <p
            v-for="error in titleValidation.errors"
            :key="error"
            class="text-sm text-red-600"
          >
            {{ error }}
          </p>
        </div>
        <p class="mt-1 text-sm ">
          {{ title.length }}/200 characters
        </p>
      </div>

      <!-- Include TOC Checkbox -->
      <div>
        <label class="block text-sm font-medium mb-2">
          Table of Contents
        </label>
        <div class="flex items-center space-x-3">
          <UCheckbox
            v-model="includeToc"
            name="includeToc"
            size="lg"
          />
          <span class="text-sm">
            Include table of contents in the PDF
          </span>
        </div>
        <p class="mt-1 text-sm">
          Automatically generated from markdown headers
        </p>
      </div>
    </div>

    <!-- Form Summary -->
    <div class="rounded-lg p-4">
      <h4 class="text-sm font-medium mb-2">
        Form Status
      </h4>
      <div class="flex items-center space-x-4">
        <UBadge>
          Title: {{ titleValidation.isValid ? 'Valid' : 'Invalid' }}
        </UBadge>
        <UBadge>
          TOC: {{ includeToc ? 'Enabled' : 'Disabled' }}
        </UBadge>
      </div>
    </div>
  </div>
</template>
