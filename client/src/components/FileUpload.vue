<script setup>
import { computed, useTemplateRef } from 'vue'
import { useFileUpload } from '@/composables/useFileUpload'

const emit = defineEmits(['filesChange'])

const fileInput = useTemplateRef('file-input')

const {
  files,
  isDragOver,
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
  setDragOver,
} = useFileUpload()

const validationStatus = computed(() => validateFiles())

const dropZoneClasses = computed(() => [
  'border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all duration-200',
])

function openFileDialog() {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

function emitFilesChange() {
  const validation = validateFiles()
  emit('filesChange', {
    files: files.value,
    validation,
    markdownFiles: markdownFiles.value,
    imageFiles: imageFiles.value,
  })
}

function onFileSelect(event) {
  const selectedFiles = event.target.files
  if (selectedFiles && selectedFiles.length > 0) {
    addFiles(selectedFiles)
    emitFilesChange()
  }
  // Reset input value to allow selecting the same files again
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function onDrop(event) {
  setDragOver(false)
  const droppedFiles = event.dataTransfer.files
  if (droppedFiles && droppedFiles.length > 0) {
    addFiles(droppedFiles)
    emitFilesChange()
  }
}

function onDragOver() {
  setDragOver(true)
}

function onDragEnter() {
  setDragOver(true)
}

function onDragLeave(event) {
  // Only set drag over to false if leaving the drop zone entirely
  if (!event.currentTarget.contains(event.relatedTarget)) {
    setDragOver(false)
  }
}

function onRemoveFile(fileId) {
  removeFile(fileId)
  emitFilesChange()
}

function clearAllFiles() {
  clearFiles()
  emitFilesChange()
}

// Initial emit
emitFilesChange()
</script>

<template>
  <div class="space-y-6">
    <!-- Drop Zone -->
    <div
      :class="dropZoneClasses"
      @drop.prevent="onDrop"
      @dragover.prevent="onDragOver"
      @dragenter.prevent="onDragEnter"
      @dragleave.prevent="onDragLeave"
      @click="openFileDialog"
    >
      <input
        ref="file-input"
        type="file"
        multiple
        accept=".md,.markdown,.png,.jpg,.jpeg"
        class="hidden"
        @change="onFileSelect"
      >

      <div class="text-center">
        <div class="mx-auto h-12 w-12 mb-4">
          <svg class="h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <div class="text-lg font-medium mb-2">
          {{ isDragOver ? 'Drop files here' : 'Upload your files' }}
        </div>
        <p class="text-sm mb-4">
          Drag and drop your markdown and image files, or click to browse
        </p>
        <div class="flex justify-center space-x-2">
          <UBadge color="secondary" variant="soft">
            Markdown: .md, .markdown
          </UBadge>
          <UBadge color="primary" variant="soft">
            Images: .png, .jpg, .jpeg
          </UBadge>
        </div>
        <p class="text-xs mt-2">
          Maximum total size: 50MB
        </p>
      </div>
    </div>

    <!-- File Validation Status -->
    <div v-if="files.length > 0" class="rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium">
          Upload Status
        </h4>
        <UButton
          icon="i-lucide-trash-2"
          :disabled="files.length === 0"
          label="Clear All"
          color="error"
          variant="soft"
          size="sm"
          @click="clearAllFiles"
        />
      </div>

      <div class="flex flex-wrap gap-2 mb-3">
        <UBadge
          :color="validationStatus.hasMarkdown && validationStatus.markdownCount === 1 ? 'primary' : 'error'"
          :variant="validationStatus.hasMarkdown && validationStatus.markdownCount === 1 ? 'soft' : 'solid'"
        >
          Markdown: {{ validationStatus.markdownCount }}/1
        </UBadge>
        <UBadge color="secondary" variant="soft">
          Images: {{ imageFiles.length }}
        </UBadge>
        <UBadge
          :color="isValidTotalSize ? 'primary' : 'error'"
          :variant="isValidTotalSize ? 'soft' : 'solid'"
        >
          Size: {{ formatFileSize(totalSize) }}/50MB
        </UBadge>
      </div>

      <div v-if="validationStatus.errors.length > 0" class="space-y-1">
        <UAlert
          v-for="error in validationStatus.errors"
          :key="error"
          color="error"
          variant="soft"
          :description="error"
        />
      </div>
    </div>

    <!-- File List -->
    <div v-if="files.length > 0" class="space-y-3">
      <h4 class="text-sm font-medium">
        Uploaded Files
      </h4>

      <div class="space-y-2">
        <div
          v-for="file in files"
          :key="file.id"
          class="flex items-center justify-between p-3 border border-gray-800 rounded-lg hover:border-gray-600 transition-colors"
        >
          <div class="flex items-center space-x-3 flex-1 min-w-0">
            <!-- File Type Icon -->
            <div class="flex-shrink-0">
              <UBadge
                :color="file.type === 'markdown' ? 'secondary' : 'primary'"
                variant="soft"
                size="sm"
              >
                {{ file.type === 'markdown' ? 'MD' : 'IMG' }}
              </UBadge>
            </div>

            <!-- File Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate">
                {{ file.file.name }}
              </p>
              <div class="flex items-center space-x-2 text-xs">
                <span>{{ formatFileSize(file.file.size) }}</span>
                <span>{{ getFileExtension(file.file.name).toUpperCase() }}</span>
              </div>
            </div>

            <!-- Image Preview -->
            <div v-if="file.type === 'image' && file.preview" class="flex-shrink-0">
              <img
                :src="file.preview"
                :alt="file.file.name"
                class="h-10 w-10 object-cover rounded border border-gray-800"
              >
            </div>
          </div>

          <!-- Remove Button -->
          <UButton
            label="Remove"
            icon="i-lucide-trash-2"
            color="error"
            variant="soft"
            size="sm"
            class="ml-3"
            @click="onRemoveFile(file.id)"
          />
        </div>
      </div>
    </div>

    <!-- Drop Zone Instructions -->
    <div v-if="files.length === 0" class="text-center text-sm">
      <p>No files uploaded yet. Start by adding exactly one markdown file.</p>
    </div>
  </div>
</template>
