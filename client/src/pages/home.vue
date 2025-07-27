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

    if (!fileUploadData.value.files.length) {
      throw new Error('No file found')
    }

    // Step 2: Create ZIP
    generationState.value = GENERATION_STATES.CREATING_ZIP
    const markdownFiles = fileUploadData.value.files.filter(f => f.type === 'text/markdown')

    const imageFiles = fileUploadData.value.files.filter(f => f.type.startsWith('image/'))
    const zipBlob = await createZip({
      markdownFiles,
      imageFiles,
    })
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
      <ApiStatus />

      <!-- Loading Overlay -->
      <UModal v-model:open="isGenerating">
        <template #content>
          <UCard>
            <LoadingSpinner
              :state="generationState"
              :show-details="true"
              :show-cancel="canCancel"
              class="mx-auto"
              @cancel="cancelGeneration"
            />
          </UCard>
        </template>
      </UModal>

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
            color="info"
            label="Generate PDF"
            icon="i-lucide-cloud-cog"
            @click="generatePdf"
          />
        </div>
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
          <p>Markdown to PDF Converter - Professional document generation</p>
        </div>
      </div>
    </footer>
  </div>
</template>
