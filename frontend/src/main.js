import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initAuth } from './composables/useAuth'
import '@material-symbols/font-400/outlined.css'
import './style.css'

initAuth().then(() => {
  createApp(App).use(router).mount('#app')
})
