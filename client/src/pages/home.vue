<script setup>
import { saveAs } from 'file-saver'
import { computed, ref } from 'vue'
import ApiStatus from '@/components/ApiStatus.vue'
import FileUpload from '@/components/FileUpload.vue'
import GenerationForm from '@/components/GenerationForm.vue'
import InstructionsPanel from '@/components/InstructionsPanel.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { useApi } from '@/composables/useApi'
import { useZipCreation } from '@/composables/useZipCreation'
import { GENERATION_STATES } from '@/utils/constants'

const api = useApi()
const { createZip } = useZipCreation()

// State
const formData = ref({
  title: '',
  includeToc: true,
  isValid: false,
})

const fileUploadData = ref({
  files: [],
  isValid: false,
})

const isGenerating = ref(false)
const generationState = ref(GENERATION_STATES.IDLE)
const error = ref(null)

// Computed
const canGenerate = computed(() => {
  return formData.value.isValid
    && fileUploadData.value.isValid
    && !isGenerating.value
})

const canCancel = computed(() => {
  return generationState.value === GENERATION_STATES.VALIDATING
    || generationState.value === GENERATION_STATES.CREATING_ZIP
})

function clearError() {
  error.value = null
}

function setError(title, message) {
  error.value = { title, message }
}

// Generation Process
async function generatePdf() {
  if (!canGenerate.value)
    return

  try {
    isGenerating.value = true
    error.value = null

    // Step 1: Validation
    generationState.value = GENERATION_STATES.VALIDATING
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate validation time

    if (!fileUploadData.value.markdownFiles.length) {
      throw new Error('No markdown file found')
    }

    // Step 2: Create ZIP
    generationState.value = GENERATION_STATES.CREATING_ZIP
    const zipBlob = await createZip(
      fileUploadData.value.markdownFiles[0].file,
      fileUploadData.value.imageFiles.map(f => f.file),
    )

    // Step 3: Upload and Convert
    generationState.value = GENERATION_STATES.UPLOADING
    const convertData = {
      title: formData.value.title,
      include_toc: formData.value.includeToc,
    }

    generationState.value = GENERATION_STATES.GENERATING
    const pdfBlob = await api.convert(zipBlob, convertData)

    // Step 4: Download
    generationState.value = GENERATION_STATES.DOWNLOADING
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate download prep

    // Save the PDF
    const filename = `${formData.value.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`
    saveAs(pdfBlob, filename)

    generationState.value = GENERATION_STATES.SUCCESS
  }
  catch (err) {
    console.error('PDF generation failed:', err)
    generationState.value = GENERATION_STATES.ERROR

    let errorMessage = 'An unexpected error occurred during PDF generation.'

    if (err.message.includes('network') || err.message.includes('fetch')) {
      errorMessage = 'Network error: Please check your internet connection and try again.'
    }
    else if (err.message.includes('file') || err.message.includes('format')) {
      errorMessage = 'File error: Please check your files and try again.'
    }
    else if (err.message.includes('server') || err.status >= 500) {
      errorMessage = 'Server error: The service is temporarily unavailable. Please try again later.'
    }
    else if (err.status === 400) {
      errorMessage = 'Invalid request: Please check your input and try again.'
    }

    setError('PDF Generation Failed', errorMessage)
  }
  finally {
    setTimeout(() => {
      isGenerating.value = false
      generationState.value = GENERATION_STATES.IDLE
    }, 1000)
  }
}

function cancelGeneration() {
  if (canCancel.value) {
    isGenerating.value = false
    generationState.value = GENERATION_STATES.IDLE
    setError('Generation Cancelled', 'PDF generation was cancelled by user.')
  }
}
</script>

<template>
  <div class="min-h-screen">
    <!-- Header -->
    <header>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold ">
              Markdown to PDF Converter
            </h1>
            <p class="mt-1 text-sm text-gray-400">
              Convert your markdown documents to professional PDFs
            </p>
          </div>
          <InstructionsPanel />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- API Status -->
      <!-- <ApiStatus /> -->

      <!-- Loading Overlay -->
      <div v-if="isGenerating" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg max-w-md w-full mx-4">
          <LoadingSpinner
            :state="generationState"
            :show-details="true"
            :show-cancel="canCancel"
            @cancel="cancelGeneration"
          />
        </div>
      </div>

      <!-- Main Form -->
      <div v-if="!isGenerating" class="space-y-8">
        <!-- Generation Form -->
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">
              Document Settings
            </h2>
          </template>

          <GenerationForm v-model="formData" />
        </UCard>

        <!-- File Upload -->
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">
              File Upload
            </h2>
          </template>

          <FileUpload v-model="fileUploadData" />
        </UCard>

        <!-- Generation Button -->
        <div class="flex justify-center">
          <UButton
            :disabled="!canGenerate"
            :loading="isGenerating"
            size="xl"
            color="blue"
            @click="generatePdf"
          >
            <template #leading>
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </template>
            Generate PDF
          </UButton>
        </div>

        <!-- Generation Summary -->
        <!-- <div v-if="formData.title || fileUploadData.files.length > 0" class="rounded-lg p-4">
          <h3 class="text-sm font-medium mb-2">
            Generation Summary
          </h3>
          <div class="text-sm space-y-1">
            <p v-if="formData.title">
              <strong>Title:</strong> {{ formData.title }}
            </p>
            <p>
              <strong>Table of Contents:</strong> {{ formData.includeToc ? 'Enabled' : 'Disabled' }}
            </p>
            <p v-if="fileUploadData.markdownFiles.length > 0">
              <strong>Markdown File:</strong> {{ fileUploadData.markdownFiles[0].file.name }}
            </p>
            <p v-if="fileUploadData.imageFiles.length > 0">
              <strong>Images:</strong> {{ fileUploadData.imageFiles.length }} file(s)
            </p>
            <p>
              <strong>Total Size:</strong> {{ formatFileSize(getTotalSize()) }}
            </p>
          </div>
        </div> -->
      </div>

      <!-- Error Display -->
      <div v-if="error" class="mt-6">
        <UAlert
          color="red"
          variant="solid"
          :title="error.title"
          :description="error.message"
        >
          <template #actions>
            <UButton color="white" variant="solid" size="xs" @click="clearError">
              Dismiss
            </UButton>
          </template>
        </UAlert>
      </div>
    </main>

    <!-- Footer -->
    <footer class="mt-12 border-t border-gray-600 ">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center text-sm text-gray-600">
          <p>Markdown to PDF Converter • Professional document generation</p>
        </div>
      </div>
    </footer>
  </div>
</template>
