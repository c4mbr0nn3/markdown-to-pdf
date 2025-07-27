<script setup>
import { computed, watch } from 'vue'

const model = defineModel({ required: true })

// const MARKDOWN_EXTENSIONS = ['.md', '.markdown']
// const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

const markdownCount = computed(() => model.value.files.filter(file => file.type === 'text/markdown').length)
const imageCount = computed(() => model.value.files.filter(file => file.type.startsWith('image/')).length)
const totalSize = computed(() => model.value.files.reduce((sum, file) => sum + file.size, 0))
const isValidTotalSize = computed(() => totalSize.value <= MAX_FILE_SIZE)

const fileSizeFormatted = computed(() => {
  const bytes = totalSize.value
  if (bytes === 0)
    return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
})

const validationErrors = computed(() => {
  const errors = []
  if (markdownCount.value > 1) {
    errors.push('Only one markdown file is allowed.')
  }
  if (markdownCount.value === 0 && model.value.files.length > 0) {
    errors.push('At least one markdown file is required.')
  }
  if (!isValidTotalSize.value) {
    errors.push(`Total file size exceeds ${MAX_FILE_SIZE / (1024 * 1024)} MB.`)
  }
  return errors
})

watch(
  () => model.value.files,
  () => {
    model.value.isValid = model.value.files.length > 0 && validationErrors.value.length === 0
  },
  { immediate: true, deep: true },
)

function clearAllFiles() {
  model.value.files = []
}
</script>

<template>
  <div class="space-y-6">
    <!-- Drop Zone -->
    <UFileUpload
      v-model="model.files"
      layout="list"
      multiple
      label="Drop your files here"
      description="You can drop images and a markdown file here."
      accept="image/jpeg,image/jpg,image/png,text/markdown"
      class="w-full min-h-48"
    />

    <!-- File Validation Status -->
    <div v-if="model.files.length > 0" class="rounded-lg py-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium">
          Upload Status
        </h4>
        <UButton
          icon="i-lucide-trash-2"
          label="Clear All"
          color="error"
          variant="soft"
          size="sm"
          @click="clearAllFiles"
        />
      </div>
      <div class="flex flex-wrap gap-2 mb-3">
        <UBadge
          :color="markdownCount === 1 ? 'primary' : 'error'"
          :variant="markdownCount === 1 ? 'soft' : 'solid'"
        >
          Markdown: {{ markdownCount }}/1
        </UBadge>
        <UBadge color="secondary" variant="soft">
          Images: {{ imageCount }}
        </UBadge>
        <UBadge
          :color="isValidTotalSize ? 'primary' : 'error'"
          :variant="isValidTotalSize ? 'soft' : 'solid'"
        >
          Size: {{ fileSizeFormatted }}/50MB
        </UBadge>
      </div>

      <div v-if="validationErrors.length > 0" class="space-y-1">
        <UAlert
          v-for="error in validationErrors"
          :key="error"
          color="error"
          variant="soft"
          :description="error"
        />
      </div>
    </div>

    <!-- Drop Zone Instructions -->
    <div v-if="model.files.length === 0" class="text-center text-sm">
      <p>No files uploaded yet. Start by adding exactly one markdown file.</p>
    </div>
  </div>
</template>
