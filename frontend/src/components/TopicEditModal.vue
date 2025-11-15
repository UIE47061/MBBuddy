<template>
  <div v-if="isVisible" class="topic-edit-overlay">
    <div class="topic-edit-container">
      <h3>{{ isAddingTopic ? '新增主題' : '編輯主題' }}</h3>
      
      <!-- 頁籤導覽 -->
      <div class="edit-topic-tabs">
        <button :class="{ active: activeTab === 'manual' }" @click="activeTab = 'manual'">
          <i class="fa-solid fa-keyboard"></i> 自行輸入
        </button>
        <button :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'">
          <i class="fa-solid fa-lightbulb"></i> AI 發想
        </button>
      </div>

      <!-- 頁籤內容 -->
      <div class="edit-topic-content">
        <!-- 手動輸入 -->
        <div v-if="activeTab === 'manual'">
          <input 
            ref="topicEditInput"
            v-model="topicName" 
            @keyup.enter="confirmEdit" 
            @keyup.esc="cancelEdit"
            class="topic-edit-input"
            :placeholder="isAddingTopic ? '輸入主題名稱' : '修改主題名稱'"
          />
        </div>
        <!-- AI 發想 -->
        <div v-if="activeTab === 'ai'">
          <div class="ai-brainstorm-section">
            <label class="ai-brainstorm-label">請描述您希望 AI 發想的主題方向</label>
            <textarea
              v-model="aiPrompt"
              class="ai-prompt-input"
              placeholder="例如：「一個關於提升團隊協作效率的創新方法」"
              rows="3"
            ></textarea>
          </div>
        </div>
      </div>

      <div class="topic-edit-actions">
        <button 
          class="btn btn-primary" 
          @click="confirmEdit" 
          :disabled="(activeTab === 'manual' && !topicName.trim()) || (activeTab === 'ai' && !aiPrompt.trim())"
        >
          <i :class="activeTab === 'ai' ? 'fa-solid fa-lightbulb' : 'fa-solid fa-check'"></i>
          {{ activeTab === 'ai' ? '產生' : (isAddingTopic ? '新增' : '儲存') }}
        </button>
        <button class="btn btn-outline" @click="cancelEdit">
          <i class="fa-solid fa-xmark"></i>
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true
  },
  isAddingTopic: {
    type: Boolean,
    default: false
  },
  editingTopicName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['cancel-edit', 'confirm-edit'])

const activeTab = ref('manual')
const topicName = ref('')
const aiPrompt = ref('')
const topicEditInput = ref(null)

// 當 props 變化時更新本地狀態
watch(() => props.editingTopicName, (newName) => {
  topicName.value = newName
}, { immediate: true })

// 當模態框顯示時聚焦輸入框
watch(() => props.isVisible, async (isVisible) => {
  if (isVisible) {
    activeTab.value = 'manual'
    await nextTick()
    topicEditInput.value?.focus()
  }
})

function cancelEdit() {
  // 重置狀態
  topicName.value = ''
  aiPrompt.value = ''
  activeTab.value = 'manual'
  emit('cancel-edit')
}

function confirmEdit() {
  const data = {
    tab: activeTab.value,
    topicName: topicName.value.trim(),
    aiPrompt: aiPrompt.value.trim(),
    isAddingTopic: props.isAddingTopic
  }
  
  emit('confirm-edit', data)
  
  // 重置狀態
  topicName.value = ''
  aiPrompt.value = ''
  activeTab.value = 'manual'
}
</script>

<style scoped>
.topic-edit-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 0 16px;
  backdrop-filter: blur(4px);
}

.topic-edit-container {
  background: var(--background);
  border-radius: 1rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideIn 0.3s ease;
}

.topic-edit-container h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-weight: 600;
}

.edit-topic-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
}

.edit-topic-tabs button {
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-secondary);
  position: relative;
  top: 1px;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.edit-topic-tabs button.active {
  color: var(--primary-color);
  font-weight: 600;
  border-bottom-color: var(--primary-color);
}

.edit-topic-content {
  min-height: 120px;
  margin-bottom: 1.5rem;
}

.topic-edit-input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  font-size: 1rem;
  transition: all 0.2s;
}

.topic-edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.ai-brainstorm-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  background-color: var(--surface);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
}

.ai-brainstorm-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.ai-prompt-input {
  flex-grow: 1;
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  font-size: 1rem;
  margin-bottom: 0.5rem;
  transition: all 0.2s;
  resize: vertical;
}

.ai-prompt-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.topic-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
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

@keyframes modalSlideIn {
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