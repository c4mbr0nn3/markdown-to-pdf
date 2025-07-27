import { createApp } from 'vue'
import App from './App.vue'

// Import Nuxt UI styles
import '@nuxt/ui/dist/runtime/ui.css'

// Create and mount the Vue application
const app = createApp(App)

// Mount the app
app.mount('#app')