<template>
  <div class="control-panel">
    <div class="panel-header">
      <h2>控制區</h2>
      <div class="panel-tabs">
        <button :class="{ active: activeTab === 'control' }" @click="setActiveTab('control')" title="討論控制">
          <i class="fa-solid fa-gear"></i>
        </button>
        <button :class="{ active: activeTab === 'info' }" @click="setActiveTab('info')" title="討論資訊">
          <i class="fa-solid fa-link"></i>
        </button>
        <button :class="{ active: activeTab === 'members' }" @click="setActiveTab('members')" title="成員名單">
          <i class="fa-solid fa-users"></i>
        </button>
      </div>
    </div>

    <!-- 討論資訊頁籤 -->
    <template v-if="activeTab === 'info'">
      <div class="control-section">
        <div class="share-item">
          <div class="share-title-row">
            <h3>討論連結</h3>
            <button class="btn-qrcode" @click="showQRCode">
              開啟 QR Code
            </button>
          </div>
          <div class="code-display">
            <span>{{ roomLink }}</span>
            <button class="btn-icon" @click="copyRoomLink" title="複製連結">
              <i class="fa-regular fa-clipboard"></i>
            </button>
          </div>
          <div class="setting-item" style="margin-top: 1rem;">
            <label class="switch">
              <input type="checkbox" :checked="localAllowJoin" @change="updateAllowJoin" />
              <span class="slider"></span>
            </label>
            <span>允許加入</span>
          </div>
          
          <!-- 房間資訊設定 -->
          <div class="room-info-settings" style="margin-top: 1.5rem;">
            <h3>房間資訊</h3>
            
            <!-- 顯示模式 -->
            <div v-if="!isEditingRoomInfo" class="room-info-display">
              <div class="room-info-item">
                <label>房間名稱</label>
                <div class="room-info-value">{{ room?.title || '載入中...' }}</div>
              </div>
              <div class="room-info-item">
                <label>摘要資訊</label>
                <div class="room-info-value" style="white-space: pre-wrap;">{{ room?.topic_summary || '（尚未填寫）' }}</div>
              </div>
              <div class="room-info-actions">
                <button class="btn btn-outline btn-sm" @click="startEditRoomInfo">
                  <i class="fa-solid fa-pen-to-square"></i>
                  編輯
                </button>
              </div>
            </div>
            
            <!-- 編輯模式 -->
            <div v-else class="room-info-form">
              <div class="form-group">
                <label for="edit-room-title">房間名稱</label>
                <div class="input-with-btn">
                  <input 
                    id="edit-room-title"
                    type="text" 
                    :value="editRoomTitle" 
                    @input="$emit('update:edit-room-title', $event.target.value)"
                    :placeholder="room?.title || '討論室名稱'"
                    maxlength="50"
                    class="form-input"
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="edit-room-summary">摘要資訊</label>
                <textarea
                  id="edit-room-summary"
                  :value="editRoomSummary"
                  @input="$emit('update:edit-room-summary', $event.target.value)"
                  placeholder="輸入此討論的摘要資訊..."
                  rows="4"
                  class="form-input"
                ></textarea>
              </div>
              <div class="form-actions">
                <button 
                  class="btn btn-primary btn-sm" 
                  @click="updateRoomInfo"
                  :disabled="!editRoomTitle.trim()"
                >
                  <i class="fa-solid fa-check"></i>
                  儲存變更
                </button>
                <button 
                  class="btn btn-outline btn-sm" 
                  @click="cancelEditRoomInfo"
                >
                  <i class="fa-solid fa-xmark"></i>
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 討論控制頁籤 -->
    <template v-else-if="activeTab === 'control'">
      <div class="control-section">
        <div class="timer-header-row">
          <h3>計時器</h3>
          <div class="timer-header-actions">
            <div class="timer-controls">
              <button class="btn-timer" :class="{ 'timer-active': timerRunning }" @click="toggleTimer">
                <i :class="timerRunning ? 'fa-solid fa-pause' : 'fa-solid fa-play'"></i>
              </button>
              <button class="btn-timer" @click="showTimerSettings">
                <i class="fa-solid fa-gear"></i>
              </button>
              <button class="btn-timer btn-terminate" @click="terminateTimer">
                <i class="fa-solid fa-stop"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="timer-display">
          <div class="timer-top">
            <div class="timer-time">{{ formattedRemainingTime }}</div>
          </div>
        </div>
      </div>
      <div class="control-section">
        <h3>問答設定</h3>
        <div class="setting-item">
          <label class="switch">
            <input type="checkbox" :checked="localSettings.allowQuestions" @change="updateSettings" name="allowQuestions">
            <span class="slider"></span>
          </label>
          <span>允許新意見</span>
        </div>
        <div class="setting-item">
          <label class="switch">
            <input type="checkbox" :checked="localSettings.allowVoting" @change="updateSettings" name="allowVoting">
            <span class="slider"></span>
          </label>
          <span>允許投票</span>
        </div>
      </div>
      <div class="control-section">
        <h3>統計資訊</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ totalQuestions }}</div>
            <div class="stat-label">總意見數</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalVotes }}</div>
            <div class="stat-label">總投票數</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ participantsList.length }}</div>
            <div class="stat-label">活躍參與者</div>
          </div>
        </div>
      </div>
    </template>

    <!-- 成員名單頁籤 -->
    <template v-else-if="activeTab === 'members'">
      <div class="control-section">
        <h3>目前參與者</h3>
        <ul class="participant-list">
          <li v-for="(p, index) in participantsList" :key="index">
            <i class="fa-regular fa-user"></i> {{ p.nickname }}
            <button class="btn-icon" @click="removeParticipant(index)" title="移除成員">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'control'
  },
  room: {
    type: Object,
    default: null
  },
  roomLink: {
    type: String,
    required: true
  },
  allowJoin: {
    type: Boolean,
    required: true
  },
  settings: {
    type: Object,
    required: true
  },
  timerRunning: {
    type: Boolean,
    required: true
  },
  formattedRemainingTime: {
    type: String,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  },
  totalVotes: {
    type: Number,
    required: true
  },
  participantsList: {
    type: Array,
    required: true
  },
  isEditingRoomInfo: {
    type: Boolean,
    default: false
  },
  editRoomTitle: {
    type: String,
    default: ''
  },
  editRoomSummary: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'set-active-tab',
  'show-qrcode',
  'copy-room-link',
  'update-allow-join',
  'update:edit-room-title',
  'update:edit-room-summary',
  'start-edit-room-info',
  'cancel-edit-room-info',
  'update-room-info',
  'toggle-timer',
  'show-timer-settings',
  'terminate-timer',
  'update-settings',
  'remove-participant'
])

// 本地狀態
const localAllowJoin = ref(props.allowJoin)
const localSettings = reactive({ ...props.settings })

// 監聽 props 變化並更新本地狀態
watch(() => props.allowJoin, (newValue) => {
  localAllowJoin.value = newValue
})

watch(() => props.settings, (newSettings) => {
  Object.assign(localSettings, newSettings)
}, { deep: true })

function setActiveTab(tab) {
  emit('set-active-tab', tab)
}

function showQRCode() {
  emit('show-qrcode')
}

function copyRoomLink() {
  emit('copy-room-link')
}

function updateAllowJoin(event) {
  localAllowJoin.value = event.target.checked
  emit('update-allow-join', localAllowJoin.value)
}

function startEditRoomInfo() {
  emit('start-edit-room-info')
}

function cancelEditRoomInfo() {
  emit('cancel-edit-room-info')
}

function updateRoomInfo() {
  emit('update-room-info')
}

function toggleTimer() {
  emit('toggle-timer')
}

function showTimerSettings() {
  emit('show-timer-settings')
}

function terminateTimer() {
  emit('terminate-timer')
}

function updateSettings(event) {
  const fieldName = event.target.name
  localSettings[fieldName] = event.target.checked
  emit('update-settings', { ...localSettings })
}

function removeParticipant(index) {
  emit('remove-participant', index)
}
</script>

<style scoped>
.control-panel {
  display: flex;
  flex-direction: column;
  max-height: 100vh;
  overflow-y: auto;
  min-width: 280px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  overflow: hidden;
}

.panel-header {
  padding: 1.3rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--background);
}

.panel-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.panel-tabs {
  display: flex;
  gap: 10px;
}

.panel-tabs button {
  background: transparent;
  border: none;
  padding: 6px 12px;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-tabs button.active {
  color: var(--primary-color);
  border-color: var(--primary-color);
  font-weight: 600;
}

.control-section {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.control-section:last-child {
  border-bottom: none;
}

.control-section h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.share-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  gap: 12px;
}

.share-title-row h3 {
  margin: 0 0 0 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.code-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 1rem;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.code-display span {
  flex: 1;
  font-family: 'Space Mono', monospace;
  font-size: 0.9rem;
  color: var(--text-primary);
  word-break: break-all;
}

.btn-qrcode {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.btn-qrcode:hover {
  background: var(--primary-hover);
  color: white;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary);
  border-radius: 0.25rem;
  transition: color 0.2s;
}

.btn-icon:hover {
  background: var(--surface);
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border);
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-color);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.room-info-settings h3 {
  margin: 1rem 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.room-info-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.room-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.room-info-item label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.room-info-value {
  padding: 0.5rem 0.75rem;
  background-color: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem;
  min-height: 20px;
}

.room-info-actions {
  margin-top: 0.5rem;
}

.room-info-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.room-info-form .form-group {
  margin-bottom: 0;
}

.room-info-form .form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1.5px solid var(--border);
  border-radius: 6px;
  background-color: var(--surface);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.2s ease;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-input:disabled {
  background-color: var(--background);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.form-actions .btn {
  flex: 1;
}

.timer-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  gap: 1.5rem;
}

.timer-header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.timer-display {
  background: var(--background);
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border);
}

.timer-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 12px;
}

.timer-time {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.timer-controls {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-timer {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.btn-timer:hover {
  background: var(--border);
  color: var(--primary-color);
}

/* 開始按鈕顯示綠色 */
.btn-timer:not(.timer-active) i.fa-play {
  color: #16a34a;
}

.btn-timer:not(.timer-active):hover i.fa-play {
  color: white;
}

.btn-timer:not(.timer-active):hover {
  background-color: #16a34a;
  border-color: #16a34a;
}

/* 設定按鈕顯示紫色 */
.btn-timer i.fa-gear {
  color: #8b5cf6;
}

.btn-timer:hover i.fa-gear {
  color: white;
}

.btn-timer:has(i.fa-gear):hover {
  background-color: #8b5cf6;
  border-color: #8b5cf6;
}

/* 暫停按鈕顯示黃色 */
.btn-timer.timer-active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

/* 終止按鈕顯示紅色 */
.btn-timer.btn-terminate {
  color: #dc2626;
}

.btn-timer.btn-terminate:hover {
  background: #dc2626;
  color: white;
  border-color: #dc2626;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item { 
  text-align: center; 
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.participant-list {
  list-style: none;
  padding: 0;
  margin-top: 0.75rem;
}

.participant-list li {
  margin-bottom: 0.5rem;
  font-size: 1rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
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
  border: 1px solid transparent;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-outline {
  background: transparent;
  border-color: var(--border);
  color: var(--text-secondary);
}

.btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
}

/* 響應式調整 */
@media (max-width: 1024px) {
  .control-panel { 
    order: -1; 
  }
}

@media (max-width: 768px) {
  .stats-grid { 
    grid-template-columns: 1fr; 
  }
}
</style>