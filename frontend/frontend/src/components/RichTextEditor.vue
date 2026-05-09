<template>
  <div class="rich-text-editor">
    <div class="custom-controls" v-if="showCustomControls">
      <button type="button" class="btn-control" @click="handleUndo" title="Undo (Ctrl+Z)">
        <i class="fas fa-undo"></i> ↶
      </button>
      <button type="button" class="btn-control" @click="handleRedo" title="Redo (Ctrl+Y)">
        <i class="fas fa-redo"></i> ↷
      </button>
    </div>
    <QuillEditor 
      ref="editor"
      v-model:content="content" 
      contentType="html" 
      theme="snow" 
      :toolbar="toolbarOptions"
      :placeholder="placeholder"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  showCustomControls: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const content = ref(props.modelValue)
const editor = ref(null)

const handleUndo = () => {
  editor.value?.getQuill()?.history?.undo()
}

const handleRedo = () => {
  editor.value?.getQuill()?.history?.redo()
}

// Sync internal content with prop
watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
  }
})

// Emit changes
watch(content, (newValue) => {
  emit('update:modelValue', newValue)
})

// Academic Toolbar Configuration
const toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
  [{ 'header': [1, 2, 3, false] }],
  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  ['clean']                                         // remove formatting button
]
</script>

<style scoped>
.rich-text-editor {
  background: white;
  border-radius: var(--border-radius);
  position: relative;
}

.custom-controls {
  position: absolute;
  top: 5px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 5px;
}

.btn-control {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 14px;
  color: #333;
  background: white;
}

.btn-control:hover {
  background: #f0f0f0;
}

:deep(.ql-toolbar) {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  border-color: var(--color-border);
  font-family: var(--font-family-base);
}

:deep(.ql-container) {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
  border-color: var(--color-border);
  font-family: var(--font-family-base);
  min-height: 150px;
}

:deep(.ql-editor) {
  min-height: 150px;
  font-size: 14px;
  line-height: 1.6;
}
</style>
