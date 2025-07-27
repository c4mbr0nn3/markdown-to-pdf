import ui from '@nuxt/ui/vue-plugin'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import home from './pages/home.vue'
import './assets/main.css'

const app = createApp(App)
const routes = [
  { path: '/', component: home },
]
const router = createRouter({
  routes,
  history: createWebHistory(),
})
app.use(router)
app.use(ui)

app.mount('#app')
