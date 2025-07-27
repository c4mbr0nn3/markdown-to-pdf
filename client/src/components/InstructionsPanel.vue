<script>
import { ref } from 'vue'
import instructionsData from '@/data/instructions.json'

export default {
  name: 'InstructionsPanel',
  setup() {
    const instructions = ref(instructionsData)
    const isOpen = ref(false)

    return {
      instructions,
      isOpen,
    }
  },
}
</script>

<template>
  <USlideover
    v-model="isOpen"
    title="How to Use"
    description="Step-by-step guide to convert your markdown documents to PDF"
  >
    <UButton
      label="How to Use"
      color="neutral"
      variant="outline"
      @click="isOpen = true"
    />

    <template #body>
      <div class="p-6">
        <div v-for="section in instructions.sections" :key="section.id" class="mb-6">
          <h3 class="text-lg font-semibold mb-3">
            {{ section.title }}
          </h3>

          <div v-if="section.type === 'steps'">
            <ol class="list-decimal list-inside space-y-2">
              <li v-for="step in section.content" :key="step" class="text-gray-700">
                {{ step }}
              </li>
            </ol>
          </div>

          <div v-else-if="section.type === 'list'">
            <ul class="list-disc list-inside space-y-1">
              <li v-for="item in section.content" :key="item" class="text-gray-700">
                {{ item }}
              </li>
            </ul>
          </div>

          <p v-else class="text-gray-600">
            {{ section.content }}
          </p>
        </div>

        <div class="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 class="font-semibold text-blue-900 mb-2">
            Need More Help?
          </h4>
          <p class="text-blue-700 text-sm">
            If you encounter any issues, check the API status indicator at the top of the page
            or verify your internet connection.
          </p>
        </div>
      </div>
    </template>
  </USlideover>
</template>
