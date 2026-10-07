import { createApp } from 'vue'
import './globals.css'
import ModelView from './model_view.vue'

const app = createApp(ModelView)

// Expose on window for MCP server to inject results
window.mcpApp = app

app.mount('#app')
