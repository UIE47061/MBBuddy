<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>AI 心智圖</h2>
        <button class="close-btn" @click="close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在生成心智圖...</p>
        </div>
        
        <div v-else-if="error" class="error-container">
          <i class="fa-solid fa-exclamation-triangle"></i>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="generateMindMap">重新生成</button>
        </div>
        
        <div v-else-if="mindMapUrl" class="mindmap-container">
          <div class="mindmap-controls">
            <div class="zoom-controls">
              <button class="zoom-btn" @click="zoomOut" :disabled="zoomLevel <= 0.5">
                <i class="fa-solid fa-magnifying-glass-minus"></i>
              </button>
              <span class="zoom-indicator">{{ Math.round(zoomLevel * 100) }}%</span>
              <button class="zoom-btn" @click="zoomIn" :disabled="zoomLevel >= 2">
                <i class="fa-solid fa-magnifying-glass-plus"></i>
              </button>
              <button class="zoom-btn" @click="resetZoom">
                <i class="fa-solid fa-expand"></i>
              </button>
            </div>
            <div class="scroll-controls">
              <button class="scroll-btn scroll-up" @click="scrollUp">
                <i class="fa-solid fa-chevron-up"></i>
              </button>
              <button class="scroll-btn scroll-left" @click="scrollLeft">
                <i class="fa-solid fa-chevron-left"></i>
              </button>
              <button class="scroll-btn scroll-center" @click="resetScroll" title="重置位置">
                <i class="fa-solid fa-crosshairs"></i>
              </button>
              <button class="scroll-btn scroll-right" @click="scrollRight">
                <i class="fa-solid fa-chevron-right"></i>
              </button>
              <button class="scroll-btn scroll-down" @click="scrollDown">
                <i class="fa-solid fa-chevron-down"></i>
              </button>
            </div>
            <div class="action-controls">
              <button class="btn btn-secondary" @click="generateMindMap">
                <i class="fa-solid fa-arrows-rotate"></i>
                重新生成
              </button>
              <button class="btn btn-primary" @click="downloadMindMap">
                <i class="fa-solid fa-download"></i>
                儲存
              </button>
            </div>
          </div>
          <div ref="mindmapContainer" class="mindmap-viewport">
            <iframe 
              ref="mindmapIframe"
              :src="mindMapUrl" 
              class="mindmap-iframe"
              @load="onIframeLoad"
            ></iframe>
          </div>
        </div>
        
        <div v-else class="initial-container">
          <div class="loading-spinner"></div>
          <p>正在載入心智圖...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { API_BASE_URL } from '@/utils/api';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref('')
const mindMapUrl = ref('')
const zoomLevel = ref(1)
const mindmapContainer = ref(null)
const mindmapIframe = ref(null)
const scrollX = ref(0)
const scrollY = ref(0)

// 當模態視窗顯示時自動生成心智圖
watch(() => props.show, (newShow) => {
  if (newShow && !mindMapUrl.value) {
    generateMindMap()
  }
})

function close() {
  // 重置狀態，下次開啟時重新生成
  mindMapUrl.value = ''
  error.value = ''
  zoomLevel.value = 1
  scrollX.value = 0
  scrollY.value = 0
  emit('close')
}

function onIframeLoad() {
  // iframe 載入完成後重置縮放和滾動
  resetZoom()
  resetScroll()
}

function applyZoom() {
  if (mindmapIframe.value && mindmapIframe.value.contentDocument) {
    const iframeDoc = mindmapIframe.value.contentDocument
    const svgElement = iframeDoc.querySelector('svg')
    if (svgElement) {
      svgElement.style.transform = `scale(${zoomLevel.value}) translate(${scrollX.value}px, ${scrollY.value}px)`
      svgElement.style.transformOrigin = 'center'
    }
  }
}

async function generateMindMap() {
  loading.value = true
  error.value = ''
  mindMapUrl.value = ''
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/mindmap/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const blob = await response.blob()
    mindMapUrl.value = URL.createObjectURL(blob)
    
  } catch (err) {
    console.error('生成心智圖失敗:', err)
    error.value = '生成心智圖失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

function downloadMindMap() {
  if (mindMapUrl.value) {
    const link = document.createElement('a')
    link.href = mindMapUrl.value
    link.download = `AI心智圖_${new Date().toISOString().slice(0, 10)}.svg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

function zoomIn() {
  if (zoomLevel.value < 2) {
    zoomLevel.value = Math.min(2, zoomLevel.value + 0.1)
    applyZoom()
  }
}

function zoomOut() {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value = Math.max(0.5, zoomLevel.value - 0.1)
    applyZoom()
  }
}

function resetZoom() {
  zoomLevel.value = 1
  applyZoom()
}

function resetScroll() {
  scrollX.value = 0
  scrollY.value = 0
  applyZoom()
}

function scrollLeft() {
  scrollX.value += 50
  applyZoom()
}

function scrollRight() {
  scrollX.value -= 50
  applyZoom()
}

function scrollUp() {
  scrollY.value += 50
  applyZoom()
}

function scrollDown() {
  scrollY.value -= 50
  applyZoom()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 1rem;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e9ecef;
  color: #333;
}

.modal-body {
  padding: 2rem;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-container, .initial-container {
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  color: #dc3545;
}

.error-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.mindmap-container {
  width: 100%;
  max-width: 100%;
}

.mindmap-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.zoom-controls, .action-controls, .scroll-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scroll-controls {
  display: grid;
  grid-template-columns: 32px 32px 32px;
  grid-template-rows: 32px 32px 32px;
  gap: 0.25rem;
  width: fit-content;
}

.scroll-up { grid-column: 2; grid-row: 1; }
.scroll-left { grid-column: 1; grid-row: 2; }
.scroll-center { grid-column: 2; grid-row: 2; }
.scroll-right { grid-column: 3; grid-row: 2; }
.scroll-down { grid-column: 2; grid-row: 3; }

.zoom-indicator {
  font-weight: 500;
  color: #666;
  min-width: 50px;
  text-align: center;
  font-size: 0.875rem;
}

.zoom-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  color: #666;
  padding: 0.5rem;
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.zoom-btn:hover:not(:disabled) {
  background: #e9ecef;
  color: #333;
}

.zoom-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.scroll-btn {
  background: #f0f8ff;
  border: 1px solid #b0d4f1;
  color: #0066cc;
  padding: 0.375rem;
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.scroll-btn:hover {
  background: #e1f0ff;
  color: #004499;
}

.mindmap-viewport {
  text-align: center;
  overflow: auto;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: white;
  max-height: 70vh;
}

.mindmap-iframe {
  width: 100%;
  height: 500px;
  border: none;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-size: 0.875rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .mindmap-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .zoom-controls, .action-controls {
    justify-content: center;
  }
  
  .scroll-controls {
    justify-self: center;
  }
}
</style>
