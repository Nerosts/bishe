import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

axios.interceptors.request.use(
  (config) => {
    const userId = localStorage.getItem('user_id')
    const role = localStorage.getItem('role')

    if (userId) {
      config.headers['X-User-Id'] = userId
    }

    if (role) {
      config.headers['X-User-Role'] = role
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

createApp(App).use(router).mount('#app')