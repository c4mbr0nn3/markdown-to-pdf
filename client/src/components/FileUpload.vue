<script>
import { computed, ref } from 'vue'
import { useFileUpload } from '@/composables/useFileUpload'

export default {
  name: 'FileUpload',
  emits: ['files-change'],
  setup(props, { emit }) {
    const fileInput = ref(null)

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
      {
        'border-blue-400 bg-blue-50': isDragOver.value,
        'border-gray-300 hover:border-gray-400': !isDragOver.value,
        'bg-gray-50': !isDragOver.value,
      },
    ])

    const openFileDialog = () => {
      if (fileInput.value) {
        fileInput.value.click()
      }
    }

    const onFileSelect = (event) => {
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

    const onDrop = (event) => {
      setDragOver(false)
      const droppedFiles = event.dataTransfer.files
      if (droppedFiles && droppedFiles.length > 0) {
        addFiles(droppedFiles)
        emitFilesChange()
      }
    }

    const onDragOver = () => {
      setDragOver(true)
    }

    const onDragEnter = () => {
      setDragOver(true)
    }

    const onDragLeave = (event) => {
      // Only set drag over to false if leaving the drop zone entirely
      if (!event.currentTarget.contains(event.relatedTarget)) {
        setDragOver(false)
      }
    }

    const onRemoveFile = (fileId) => {
      removeFile(fileId)
      emitFilesChange()
    }

    const clearAllFiles = () => {
      clearFiles()
      emitFilesChange()
    }

    const emitFilesChange = () => {
      const validation = validateFiles()
      emit('files-change', {
        files: files.value,
        validation,
        markdownFiles: markdownFiles.value,
        imageFiles: imageFiles.value,
      })
    }

    // Initial emit
    emitFilesChange()

    return {
      fileInput,
      files,
      isDragOver,
      markdownFiles,
      imageFiles,
      isValidFileCount,
      totalSize,
      isValidTotalSize,
      validationStatus,
      dropZoneClasses,
      openFileDialog,
      onFileSelect,
      onDrop,
      onDragOver,
      onDragEnter,
      onDragLeave,
      removeFile: onRemoveFile,
      clearAllFiles,
      getFileExtension,
      formatFileSize,
    }
  },
}
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
        ref="fileInput"
        type="file"
        multiple
        accept=".md,.markdown,.png,.jpg,.jpeg"
        class="hidden"
        @change="onFileSelect"
      >

      <div class="text-center">
        <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
          <svg class="h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <div class="text-lg font-medium text-gray-900 mb-2">
          {{ isDragOver ? 'Drop files here' : 'Upload your files' }}
        </div>
        <p class="text-sm text-gray-600 mb-4">
          Drag and drop your markdown and image files, or click to browse
        </p>
        <div class="flex justify-center space-x-2">
          <UBadge color="blue" variant="soft">
            Markdown: .md, .markdown
          </UBadge>
          <UBadge color="green" variant="soft">
            Images: .png, .jpg, .jpeg
          </UBadge>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          Maximum total size: 50MB
        </p>
      </div>
    </div>

    <!-- File Validation Status -->
    <div v-if="files.length > 0" class="bg-gray-50 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-gray-900">
          Upload Status
        </h4>
        <UButton
          color="red"
          variant="soft"
          size="xs"
          @click="clearAllFiles"
        >
          Clear All
        </UButton>
      </div>

      <div class="flex flex-wrap gap-2 mb-3">
        <UBadge
          :color="validationStatus.hasMarkdown && validationStatus.markdownCount === 1 ? 'green' : 'red'"
          :variant="validationStatus.hasMarkdown && validationStatus.markdownCount === 1 ? 'soft' : 'solid'"
        >
          Markdown: {{ validationStatus.markdownCount }}/1
        </UBadge>
        <UBadge color="blue" variant="soft">
          Images: {{ imageFiles.length }}
        </UBadge>
        <UBadge
          :color="isValidTotalSize ? 'green' : 'red'"
          :variant="isValidTotalSize ? 'soft' : 'solid'"
        >
          Size: {{ formatFileSize(totalSize) }}/50MB
        </UBadge>
      </div>

      <div v-if="validationStatus.errors.length > 0" class="space-y-1">
        <UAlert
          v-for="error in validationStatus.errors"
          :key="error"
          color="red"
          variant="soft"
          :description="error"
        />
      </div>
    </div>

    <!-- File List -->
    <div v-if="files.length > 0" class="space-y-3">
      <h4 class="text-sm font-medium text-gray-900">
        Uploaded Files
      </h4>

      <div class="space-y-2">
        <div
          v-for="file in files"
          :key="file.id"
          class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
        >
          <div class="flex items-center space-x-3 flex-1 min-w-0">
            <!-- File Type Icon -->
            <div class="flex-shrink-0">
              <UBadge
                :color="file.type === 'markdown' ? 'blue' : 'green'"
                variant="soft"
                size="xs"
              >
                {{ file.type === 'markdown' ? 'MD' : 'IMG' }}
              </UBadge>
            </div>

            <!-- File Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ file.file.name }}
              </p>
              <div class="flex items-center space-x-2 text-xs text-gray-500">
                <span>{{ formatFileSize(file.file.size) }}</span>
                <span>{{ getFileExtension(file.file.name).toUpperCase() }}</span>
              </div>
            </div>

            <!-- Image Preview -->
            <div v-if="file.type === 'image' && file.preview" class="flex-shrink-0">
              <img
                :src="file.preview"
                :alt="file.file.name"
                class="h-10 w-10 object-cover rounded border border-gray-200"
              >
            </div>
          </div>

          <!-- Remove Button -->
          <UButton
            color="red"
            variant="soft"
            size="xs"
            @click="removeFile(file.id)"
          >
            Remove
          </UButton>
        </div>
      </div>
    </div>

    <!-- Drop Zone Instructions -->
    <div v-if="files.length === 0" class="text-center text-sm text-gray-500">
      <p>No files uploaded yet. Start by adding exactly one markdown file.</p>
    </div>
  </div>
</template>
