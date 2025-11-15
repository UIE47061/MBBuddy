<template>
  <div v-if="isVisible" class="timer-settings-overlay" @click.self="hideModal">
    <div class="timer-settings-modal">
      <div class="modal-header">
        <h3>設定計時器</h3>
        <button class="btn-close" @click="hideModal">&times;</button>
      </div>
      <div class="modal-body">
        <!-- 時間輸入區域 -->
        <div class="time-input-section">
          <div class="time-input-group">
            <div class="time-input-container">
              <input type="number" v-model="localSettings.hours" min="0" max="23" class="time-input">
              <label class="time-label">時</label>
            </div>
            <div class="time-input-container">
              <input type="number" v-model="localSettings.minutes" min="0" max="59" class="time-input">
              <label class="time-label">分</label>
            </div>
            <div class="time-input-container">
              <input type="number" v-model="localSettings.seconds" min="0" max="59" class="time-input">
              <label class="time-label">秒</label>
            </div>
          </div>
        </div>
        
        <!-- 快捷選項 -->
        <div class="timer-presets">
          <button class="timer-preset-btn" @click="setPresetTime(1)">1 分鐘</button>
          <button class="timer-preset-btn" @click="setPresetTime(5)">5 分鐘</button>
          <button class="timer-preset-btn" @click="setPresetTime(10)">10 分鐘</button>
        </div>
        
        <!-- 設定完成按鈕 -->
        <div class="timer-settings-actions">
          <button class="btn btn-primary" @click="applySettings">
            <i class="fa-solid fa-check"></i> 確定
          </button>
          <button class="btn btn-outline" @click="hideModal">
            <i class="fa-solid fa-xmark"></i> 取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true
  },
  timerSettings: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['hide-modal', 'apply-settings'])

const localSettings = ref({
  hours: 0,
  minutes: 5,
  seconds: 0
})

// 當 props.timerSettings 變化時，更新本地設定
watch(() => props.timerSettings, (newSettings) => {
  Object.assign(localSettings.value, newSettings)
}, { immediate: true, deep: true })

function hideModal() {
  emit('hide-modal')
}

function setPresetTime(minutes) {
  localSettings.value.hours = 0
  localSettings.value.minutes = minutes
  localSettings.value.seconds = 0
}

function applySettings() {
  emit('apply-settings', { ...localSettings.value })
  hideModal()
}
</script>

<style scoped>
.timer-settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.timer-settings-modal {
  background: var(--background);
  border-radius: 1rem;
  width: 90%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0.2rem;
}

.modal-body {
  padding: 1.5rem;
}

.time-input-section {
  margin-bottom: 1.5rem;
}

.time-input-group {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.time-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-input {
  width: 80px;
  height: 80px;
  text-align: center;
  font-size: 2rem;
  border-radius: 12px;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  padding: 0;
  transition: all 0.2s;
}

.time-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.time-label {
  margin-top: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.timer-presets {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.timer-preset-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 8px 16px;
  font-size: 0.9rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.timer-preset-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.timer-settings-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: 1px solid transparent;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
}

@keyframes modalSlideUp {
  from { 
    opacity: 0;
    transform: translateY(30px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}
</style>