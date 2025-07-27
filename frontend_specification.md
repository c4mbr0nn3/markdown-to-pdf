# Markdown to PDF Frontend - Technical Specification

## 1. Project Overview

### 1.1 Description

A Vue 3-based single-page application that provides a user-friendly interface for the Markdown to PDF API. The frontend allows users to upload markdown files and images via drag-and-drop, configure PDF generation settings, and download the generated PDF documents.

### 1.2 Use Case

This frontend application serves as the user interface for the Markdown to PDF API, enabling users to:

- Upload markdown files and associated images through a drag-and-drop interface
- Configure document title and table of contents settings
- Generate professionally branded PDF documents
- Monitor API status and capabilities

### 1.3 Key Requirements

- **Single Page Application**: Vue 3 with Nuxt UI for modern design
- **File Upload**: Drag-and-drop interface for markdown files and images
- **ZIP Creation**: Client-side ZIP file generation from uploaded files
- **API Integration**: Real-time communication with FastAPI backend
- **Docker Deployment**: Containerized alongside the API service

## 2. Technical Stack

### 2.1 Core Technologies

- **Framework**: Vue 3 (Composition API)
- **UI Library**: Nuxt UI 3 (community version)
- **Build Tool**: Vite
- **Package Manager**: npm
- **Node.js Version**: 18+

### 2.2 Dependencies

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "@nuxt/ui": "^3.0.0",
    "@vueuse/core": "^10.7.0",
    "ky": "^1.2.0",
    "jszip": "^3.10.1",
    "file-saver": "^2.0.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "@antfu/eslint-config": "^2.6.0",
    "eslint": "^8.56.0"
  }
}
```

## 3. Project Structure

```text
client/
├── public/                     # Static assets
│   ├── favicon.ico
│   └── logo.svg
├── src/                        # Source code
│   ├── components/             # Vue components
│   │   ├── FileUpload.vue      # Drag-and-drop file upload
│   │   ├── GenerationForm.vue  # Title and TOC form
│   │   ├── ApiStatus.vue       # API status display
│   │   ├── LoadingSpinner.vue  # Loading indicator
│   │   └── InstructionsPanel.vue # Instructions slideover
│   ├── composables/            # Vue composables
│   │   ├── useApi.js           # API client composable
│   │   ├── useFileUpload.js    # File upload logic
│   │   └── useZipCreation.js   # ZIP file creation
│   ├── utils/                  # Utility functions
│   │   ├── validation.js       # Input validation
│   │   └── constants.js        # Application constants
│   ├── data/                   # Configuration and data files
│   │   └── instructions.json   # User instructions content
│   ├── App.vue                 # Root component
│   └── main.js                 # Application entry point
├── index.html                  # HTML template
├── package.json                # Dependencies and scripts
├── vite.config.js              # Vite configuration
├── eslint.config.js            # ESLint configuration
├── Dockerfile                  # Docker configuration
└── README.md                   # Frontend documentation
```

## 4. Component Specifications

### 4.1 App.vue (Root Component)

**Purpose**: Main application layout and state management

**Features**:

- Overall page layout with Nuxt UI components
- State management for upload progress and API responses
- Error handling and notifications

**Structure**:

```vue
<template>
  <div class="min-h-screen bg-gray-50">
    <UContainer class="py-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Markdown to PDF Converter</h1>
        <p class="text-gray-600 mt-2">Convert your markdown documents to professional PDFs</p>
      </div>

      <!-- API Status -->
      <ApiStatus />

      <!-- Instructions Panel (with integrated button) -->
      <div class="text-center mb-6">
        <InstructionsPanel />
      </div>

      <!-- Main Form -->
      <UCard class="max-w-4xl mx-auto">
        <GenerationForm />
        <FileUpload />
        <div class="mt-6 text-center">
          <UButton @click="generatePdf" :loading="isGenerating" :disabled="!isFormValid">
            Generate PDF
          </UButton>
        </div>
      </UCard>
    </UContainer>
  </div>
</template>
```

### 4.2 FileUpload.vue

**Purpose**: Drag-and-drop file upload interface

**Features**:

- Drag-and-drop zone for files
- File type validation (markdown and images)
- File preview and removal
- Visual feedback for drag states
- File size validation

**Accepted Files**:

- Markdown: `.md`, `.markdown` (exactly one file required)
- Images: `.png`, `.jpg`, `.jpeg` (multiple allowed)
- Maximum file size: 50MB total

**Validation Requirements**:

- Exactly one markdown file must be uploaded
- Generate button is disabled if no markdown file or more than one markdown file is present
- Real-time validation feedback to user

### 4.3 GenerationForm.vue

**Purpose**: PDF generation configuration form

**Features**:

- Title input field (required)
- Include TOC checkbox (default: true)
- Form validation
- Integration with Nuxt UI form components

**Validation Rules**:

- Title: Required, 1-200 characters, no special characters
- TOC: Boolean value
- Form is valid only when title is provided and exactly one markdown file is uploaded
- Generate button is disabled when form validation fails

### 4.4 ApiStatus.vue

**Purpose**: Display API status and information

**Features**:

- Real-time API health status
- API capabilities display (from `/api/v1/info`)
- System uptime and environment info (from `/api/v1/status`)
- Auto-refresh every 30 seconds
- Visual status indicators

**Status Display**:

- API Health: Green (healthy) / Red (unhealthy)
- Supported formats and file size limits
- System uptime and version info

### 4.5 LoadingSpinner.vue

**Purpose**: Loading indicator during PDF generation

**Features**:

- Animated spinner with Nuxt UI styling
- Progress messages
- Cancellation option (if needed)

### 4.6 InstructionsPanel.vue

**Purpose**: Instructions slideover panel using USlideover component

**Features**:

- USlideover component from Nuxt UI
- Loads instructions from external JSON file
- Step-by-step usage guide
- File format requirements
- Examples and tips
- Close button and overlay dismiss

**Structure**:

```vue
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
          <h3 class="text-lg font-semibold mb-3">{{ section.title }}</h3>
          <div v-if="section.type === 'steps'">
            <ol class="list-decimal list-inside space-y-2">
              <li v-for="step in section.content" :key="step">{{ step }}</li>
            </ol>
          </div>
          <div v-else-if="section.type === 'list'">
            <ul class="list-disc list-inside space-y-1">
              <li v-for="item in section.content" :key="item">{{ item }}</li>
            </ul>
          </div>
          <p v-else class="text-gray-600">{{ section.content }}</p>
        </div>
      </div>
    </template>
  </USlideover>
</template>
```

## 5. Composables Specifications

### 5.1 useApi.js

**Purpose**: API client and communication logic

**Features**:

```javascript
const useApi = () => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const client = ky.create({ prefixUrl: baseUrl })

  const health = async () => {
    return await client.get('health').json()
  }

  const info = async () => {
    return await client.get('api/v1/info').json()
  }

  const status = async () => {
    return await client.get('api/v1/status').json()
  }

  const convert = async (formData) => {
    return await client.post('api/v1/convert', { body: formData }).blob()
  }

  return {
    health,
    info,
    status,
    convert
  }
}
```

### 5.2 useFileUpload.js

**Purpose**: File upload state and validation logic

**Features**:

```javascript
import { ref, computed, readonly } from 'vue'

const useFileUpload = () => {
  const files = ref([])
  const isDragOver = ref(false)

  const markdownFiles = computed(() =>
    files.value.filter(f => f.type === 'markdown')
  )

  const imageFiles = computed(() =>
    files.value.filter(f => f.type === 'image')
  )

  const isValidFileCount = computed(() =>
    markdownFiles.value.length === 1
  )

  const addFiles = (fileList) => {
    // Add files with validation
    // Only allow one markdown file
  }

  const removeFile = (id) => {
    files.value = files.value.filter(f => f.id !== id)
  }

  const validateFiles = () => {
    return {
      isValid: isValidFileCount.value,
      hasMarkdown: markdownFiles.value.length === 1,
      markdownCount: markdownFiles.value.length
    }
  }

  return {
    files: readonly(files),
    isDragOver: readonly(isDragOver),
    markdownFiles,
    imageFiles,
    isValidFileCount,
    addFiles,
    removeFile,
    validateFiles
  }
}
```

### 5.3 useZipCreation.js

**Purpose**: Client-side ZIP file creation

**Features**:

```javascript
import JSZip from 'jszip'

const useZipCreation = () => {
  const createZip = async (files) => {
    const zip = new JSZip()

    // Add the single markdown file (validated to be exactly one)
    const markdownFiles = files.filter(f => f.type === 'markdown')
    if (markdownFiles.length === 1) {
      zip.file(markdownFiles[0].file.name, markdownFiles[0].file)
    }

    // Add images to images/ folder
    const imageFiles = files.filter(f => f.type === 'image')
    for (const file of imageFiles) {
      zip.file(`images/${file.file.name}`, file.file)
    }

    return await zip.generateAsync({ type: 'blob' })
  }

  return { createZip }
}
```

## 6. Instructions Configuration

### 6.1 instructions.json

**Purpose**: External configuration file containing user instructions content

**Structure**:

```json
{
  "title": "How to Use the Markdown to PDF Converter",
  "sections": [
    {
      "id": "getting-started",
      "title": "Getting Started",
      "type": "steps",
      "content": [
        "Enter a title for your document in the Title field (required)",
        "Choose whether to include a Table of Contents (enabled by default)",
        "Upload your files using the drag-and-drop area or click to browse",
        "Click 'Generate PDF' once all requirements are met"
      ]
    },
    {
      "id": "file-requirements",
      "title": "File Requirements",
      "type": "list",
      "content": [
        "Exactly one markdown file (.md or .markdown) - required",
        "Multiple image files (.png, .jpg, .jpeg) - optional",
        "Total file size must not exceed 50MB",
        "Images should be referenced in markdown using relative paths"
      ]
    },
    {
      "id": "markdown-tips",
      "title": "Markdown Tips",
      "type": "list",
      "content": [
        "Use standard CommonMark syntax for best results",
        "Reference images like: ![Alt text](images/chart.png)",
        "Use headers (# ## ###) for automatic table of contents",
        "Tables, code blocks, and lists are fully supported"
      ]
    },
    {
      "id": "zip-structure",
      "title": "File Organization",
      "type": "text",
      "content": "When you upload files, they will be automatically organized into a ZIP structure with your markdown file at the root and images in an 'images' folder. Make sure your markdown references images using paths like 'images/filename.png'."
    },
    {
      "id": "troubleshooting",
      "title": "Troubleshooting",
      "type": "list",
      "content": [
        "Generate button disabled: Check that you have exactly one markdown file and a title",
        "Images not showing: Verify image paths in markdown match uploaded filenames",
        "File too large: Reduce image sizes or remove unnecessary files",
        "API error: Check your internet connection and try again"
      ]
    },
    {
      "id": "tips",
      "title": "Pro Tips",
      "type": "list",
      "content": [
        "Keep image file names simple (no spaces or special characters)",
        "Use descriptive titles for better PDF organization",
        "Table of contents is generated from your markdown headers",
        "The PDF will include professional company branding automatically"
      ]
    }
  ]
}
```

### 6.2 Loading Instructions in Component

```javascript
// In InstructionsPanel.vue
import { ref, computed } from 'vue'
import instructionsData from '@/data/instructions.json'

export default {
  setup() {
    const instructions = ref(instructionsData)
    const isOpen = ref(false)

    return {
      instructions,
      isOpen
    }
  }
}
```

## 7. Data Structures (JavaScript Objects)

### 7.1 API Response Formats

Expected response structures from the API:

```javascript
// Health Response
{
  status: 'healthy',
  timestamp: '2024-01-15T10:30:00Z',
  version: '1.0.0'
}

// API Info Response
{
  name: 'Markdown to PDF Converter API',
  version: '1.0.0',
  supported_formats: ['zip'],
  max_file_size: '50MB',
  supported_images: ['png', 'jpg', 'jpeg']
}

// API Status Response
{
  status: 'operational',
  uptime: '2h 30m 15s',
  version: '1.0.0',
  environment: 'production'
}
```

### 7.2 Application Data Structures

```javascript
// Uploaded File Object
{
  file: File,           // Browser File object
  id: 'uuid-string',    // Unique identifier
  type: 'markdown',     // 'markdown' or 'image'
  preview: 'data:...'   // Optional preview URL
}

// Validation Result
{
  isValid: true,
  hasMarkdown: true,
  markdownCount: 1,
  errors: []
}

// Generation State
{
  isGenerating: false,
  progress: 50,         // Optional progress percentage
  message: 'Processing...' // Optional status message
}
```

## 8. Configuration Files

### 8.1 vite.config.js

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

### 8.2 eslint.config.js

```javascript
import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
  typescript: false,
  formatters: true,
  rules: {
    'no-console': 'warn',
    'vue/max-attributes-per-line': 'off'
  }
})
```

## 9. User Interface Design

### 9.1 Layout Structure

- **Header**: Application title and description
- **API Status Bar**: Real-time status indicators
- **Main Form Card**: Centered card with form and upload area
- **Form Section**: Title input and TOC checkbox
- **Upload Section**: Drag-and-drop zone with file preview
- **Action Section**: Generate button with loading state

### 9.2 Nuxt UI Components Used

- `UContainer`: Page layout container
- `UCard`: Main form container
- `UInput`: Title text field
- `UCheckbox`: Include TOC option
- `UButton`: Generate PDF button
- `UBadge`: Status indicators
- `UAlert`: Error and success messages
- `UProgress`: Loading progress bar
- `UTable`: File list display
- `USlideover`: Instructions panel

### 9.3 Color Scheme

- Primary: Nuxt UI default blue
- Success: Green for healthy status
- Warning: Yellow for warnings
- Error: Red for errors and failures
- Background: Light gray for page background

## 10. File Upload Workflow

### 10.1 Upload Process

1. User drags files or clicks to select
2. Client validates file types and sizes
3. Files are added to upload list with preview
4. User can remove individual files
5. Markdown files and images are organized
6. ZIP creation happens on form submission

### 10.2 Validation Rules

- **File Types**: Only .md, .markdown, .png, .jpg, .jpeg
- **File Size**: Total size must not exceed 50MB
- **File Count**: Exactly one markdown file required, multiple images allowed
- **File Names**: Safe filename validation
- **Form Validation**: Generate button disabled until all requirements met

### 10.3 ZIP Structure Creation

```text
generated.zip
├── document.md (the single uploaded markdown file)
└── images/
    ├── image1.png
    ├── image2.jpg
    └── chart.jpeg
```

## 11. Error Handling

### 11.1 Client-Side Errors

- File validation errors
- Network connectivity issues
- ZIP creation failures
- Form validation errors

### 11.2 API Errors

- HTTP status code handling
- API error response parsing
- User-friendly error messages
- Retry mechanisms for transient errors

### 11.3 Error Display

- Toast notifications for quick feedback
- Inline validation messages
- Error state in upload components
- Detailed error information in development

## 12. Docker Configuration

### 12.1 Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 12.2 nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://api:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://api:8000/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## 13. Docker Compose Configuration

### 13.1 docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: markdown-pdf-api
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - API_ENV=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      - COMPANY_NAME=Your Company Name
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  frontend:
    build: ./client
    container_name: markdown-pdf-frontend
    ports:
      - "80:80"
    depends_on:
      - api
    environment:
      - VITE_API_URL=http://localhost:8000
    restart: unless-stopped

networks:
  default:
    name: markdown-pdf-network
```

## 14. Environment Variables

### 14.1 Development (.env.development)

```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Markdown to PDF Converter
VITE_MAX_FILE_SIZE=52428800
```

### 14.2 Production (.env.production)

```env
VITE_API_URL=http://api:8000
VITE_APP_TITLE=Markdown to PDF Converter
VITE_MAX_FILE_SIZE=52428800
```

## 15. Development Workflow

### 15.1 Setup Commands

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### 15.2 Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --fix"
  }
}
```

## 16. Performance Considerations

### 16.1 Optimization Strategies

- Lazy loading for components
- Image preview optimization
- Debounced API status checks
- Efficient ZIP file creation
- Minimal bundle size with tree shaking

### 16.2 File Size Limits

- Client-side validation before upload
- Progressive file loading for large uploads
- Memory-efficient ZIP creation
- Cleanup of temporary objects

## 17. Security Considerations

### 17.1 Input Validation

- File type validation using MIME types
- Filename sanitization
- File size restrictions
- Content validation for markdown files

### 17.2 API Communication

- CORS handling
- Request/response validation
- Error message sanitization
- No sensitive data in client-side code

## 18. Deployment Instructions

### 18.1 Development Deployment

```bash
# Start both services
docker-compose up --build

# Access application
# Frontend: http://localhost
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 18.2 Production Deployment

```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 19. Future Enhancements

### 19.1 Potential Features

- Multiple markdown file support with merge options
- Real-time markdown preview
- Template selection for different PDF styles
- Batch processing for multiple documents
- Download history and management
- User preferences and settings

### 19.2 Technical Improvements

- Progressive Web App (PWA) capabilities
- Offline functionality
- Advanced file validation
- Real-time collaboration features
- Integration with cloud storage services

This specification provides a complete blueprint for implementing a modern, user-friendly frontend for the Markdown to PDF API using Vue 3, Nuxt UI, and containerized deployment.
