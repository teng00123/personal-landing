import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as Icons from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router/index.js'
import './assets/global.css'

const app = createApp(App)

// 全局注册 Element Plus 图标
for (const [name, comp] of Object.entries(Icons)) {
  app.component(name, comp)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
