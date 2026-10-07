<template>
  <div>
    <h2 class="text-xl font-bold mb-3 text-blue-600">Available Models</h2>
    
    <!-- Model List Grid -->
    <div class="model-grid" v-if="models.length === 0">
      <div class="loading">Loading models...</div>
    </div>

    <div 
      class="model-card" 
      v-for="model in models" 
      :key="model.name"
      @click="invokeModel(model)"
    >
      <h3 class="model-name">{{ model.name }}</h3>
      
      <!-- Status badge -->
      <span 
        class="model-status" 
        :class="model.status === 'loaded' ? 'status-loaded' : 'status-loading'"
      >
        {{ model.status }}
      </span>

      <p class="text-sm text-gray-600 mt-1">{{ model.description || model.name }}</p>
      
      <!-- Result display -->
      <div class="result-box" v-if="model.output">
        <strong>{{ model.name }}:</strong>
        <pre>{{ model.output }}</pre>
      </div>
    </div>

    <div class="loading text-center mt-6" v-if="models.length === 0">
      Loading available models...
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// Store models keyed by model_name
const models = reactive({})

// Available models for Fal AI API (based on your project)
const AVAILABLE_MODELS = [
  {
    name: "fal-mc",
    version: "0.2.1",
    source: "https://huggingface.co/fal/Airavata-40b-fp8/resolve/main/model.json"
  },
  {
    name: "fal-audio-gen-musical-memex",
    version: "1.0.0",
    source: "fal_audio_gen_musical_memex"
  }
]

// Initialize models
for (const m of AVAILABLE_MODELS) {
  models[m.name] = {
    name: m.name,
    description: m.source?.includes('huggingface') ? `Model from HuggingFace` : m.source || '',
    status: 'loaded', // Models available for use
    output: null
  }
}

// Invoke model via MCP or Fal Client endpoint
async function invokeModel(model) {
  models[model.name].output = ''
  models[model.name].status = 'running'
  
  try {
    // Call MCP tool to invoke model
    const name = model.name.replace(/-/g, '_')
    const result = await window.mcpApp.invokeTool(name) || 'Model invocation command not available in this session. MCP server may not support direct tool calls from browser yet.'
    
    models[model.name].output = JSON.stringify(result, null, 2)
    console.log(`${name} invoked`, result)
  } catch (error) {
    console.error(`Failed to invoke ${model.name}:`, error)
  }
  
  models[model.name].status = 'loaded'
}

</script>

<style scoped>
/* Sayhello-style card layout */
div { color: #065f46; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

</style>
