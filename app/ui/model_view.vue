<template>
  <div class="model-result">
    <h3>{{ modelId }}</h3>
    <pre class="output">{{ output }}</pre>
    <template v-if="latency">
      <p><strong>Latency:</strong> {{ latency }} ms</p>
    </template>
  </div>
</template>

<script setup>
defineProps({
  modelId: { type: String, required: true },
  output: { type: String, required: true },
  latency: { type: Number },
});
</script>

<style scoped>
.model-result {
  border: 1px solid #ddd;
  padding: 1rem;
  margin: 1rem 0;
}
.output {
  white-space: pre-wrap;
  overflow-y: auto;
  max-height: 400px;
}
</style>
