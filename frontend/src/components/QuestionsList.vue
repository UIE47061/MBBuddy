<template>
  <div class="questions-list-container">
    <div class="questions-panel">
      <div class="panel-header">
        <!-- 第一行：意見列表標題和操作按鈕 -->
        <div class="header-row">
          <h2>意見列表 - {{ currentTopicTitle }}</h2>
          <div class="panel-controls">
            <select v-model="localSortBy" class="sort-options" @change="updateSortBy">
              <option value="votes">按票數排序</option>
              <option value="time">按時間排序</option>
            </select>
            <button class="btn-qrcode" id="summary-btn" @click="summaryAI" :title="`統整主題「${currentTopicTitle}」的意見`">
              AI統整
            </button>
            <button class="btn-red btn-qrcode" @click="clearAllQuestions" :title="`清空主題「${currentTopicTitle}」的所有評論`">
              <i class="fa-solid fa-trash-can"></i>
              清空評論
            </button>
          </div>
        </div>
        
        <!-- 第二行：討論進度條（並排排版） -->
        <div class="progress-row">
          <div class="progress-inline">
            <span class="progress-label">討論進度</span>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: discussionProgress + '%' }"></div>
            </div>
            <span class="progress-percentage">{{ discussionProgress }}%</span>
          </div>
          <!-- 新增：動態描述文字 -->
          <div class="progress-description">
            {{ discussionProgressText }}
          </div>
        </div>
      </div>
      
      <div class="questions-container">
        <template v-if="sortedQuestions.length === 0">
          <div class="empty-state">
            <div class="empty-icon">
              <i class="fa-regular fa-comment-dots"></i>
            </div>
            <h3>等待參與者提問</h3>
            <p>分享討論室代碼讓參與者加入並開始提問</p>
          </div>
        </template>
        <template v-else>
          <div
            v-for="q in sortedQuestions"
            :key="q.id"
            :class="['question-item', { 'ai-summary-item': q.isAISummary }]"
          >
            <!-- AI 總結樣式 -->
            <template v-if="q.isAISummary">
              <div class="question-header">
                <div class="question-text">
                  <h3><i class="fa-solid fa-robot"></i> AI 討論總結</h3>
                  <div class="ai-content" v-html="q.content.replace(/\\n/g, '<br>')"></div>
                </div>
                <div class="question-actions">
                  <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除此總結">
                    <i class="fa-solid fa-trash-can"></i>
                  </button>
                </div>
              </div>
              <div class="question-meta">
                <div class="question-info">
                  <div class="question-time">{{ formatTime(q.ts) }}</div>
                </div>
              </div>
            </template>

            <!-- 一般留言樣式 -->
            <template v-else>
              <div class="question-header">
                <div class="question-text" v-html="escapeHtml(q.content)"></div>
                <div class="question-actions">
                  <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除意見">
                    <i class="fa-solid fa-trash-can"></i>
                  </button>
                </div>
              </div>
              <div class="question-meta">
                <div class="question-votes">
                  <span class="vote-item"><i class="fa-solid fa-thumbs-up"></i> {{ q.vote_good || 0 }}</span>
                  <span class="vote-item"><i class="fa-solid fa-thumbs-down"></i> {{ q.vote_bad || 0 }}</span>
                </div>
                <div class="question-info">
                  <div class="question-nickname" v-if="q.nickname"><i class="fa-regular fa-user"></i> {{ q.nickname }}</div>
                  <div class="question-time">{{ formatTime(q.ts) }}</div>
                </div>
              </div>
            </template>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  currentTopicTitle: {
    type: String,
    default: '未選擇主題'
  },
  sortBy: {
    type: String,
    default: 'votes'
  },
  discussionProgress: {
    type: Number,
    default: 0
  },
  discussionProgressText: {
    type: String,
    default: '等待討論開始...'
  }
})

const emit = defineEmits(['delete-question', 'summary-ai', 'clear-all-questions', 'update-sort-by'])

const localSortBy = ref(props.sortBy)

// 監聽父組件的 sortBy 變化
watch(() => props.sortBy, (newValue) => {
  localSortBy.value = newValue
})

const sortedQuestions = computed(() => {
  // 1. 先將 AI 總結和一般留言分開
  const aiSummaries = props.questions.filter(q => q.isAISummary)
  const normalQuestions = props.questions.filter(q => !q.isAISummary)

  // 2. 只對一般留言進行排序
  const sortedNormal = [...normalQuestions].sort((a, b) => {
    if (localSortBy.value === 'votes') {
      const aVotes = (a.vote_good || 0) - (a.vote_bad || 0)
      const bVotes = (b.vote_good || 0) - (b.vote_bad || 0)
      if (bVotes !== aVotes) return bVotes - aVotes
    }
    // 時間排序
    return (b.ts || 0) - (a.ts || 0)
  })

  // 3. 最後，將 AI 總結放回陣列的最前面
  return [...aiSummaries, ...sortedNormal]
})

function updateSortBy() {
  emit('update-sort-by', localSortBy.value)
}

function deleteQuestion(id) {
  emit('delete-question', id)
}

function summaryAI() {
  emit('summary-ai')
}

function clearAllQuestions() {
  emit('clear-all-questions')
}

function formatTime(dateString) {
  const date = new Date(dateString * 1000)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '剛剛'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分鐘前`
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  // 處理換行符號，將 \n 轉換為 <br>
  return div.innerHTML.replace(/\\n/g, '<br>')
}
</script>

<style scoped>
.questions-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
}

.questions-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 1.3rem;
  border-bottom: 1px solid var(--border);
  background: var(--background);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex-shrink: 0;
}

/* 第一行：標題和控制按鈕 */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-row h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.panel-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

/* 第二行：進度條 */
.progress-row {
  width: 100%;
}

.progress-inline {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.progress-label {
  font-size: 1rem;
  font-weight: 600;
  /* 修改：使用主題變數，自動適應深淺色模式 */
  color: var(--text-primary); /* 這會在淺色模式下是黑色，深色模式下是白色 */
  white-space: nowrap;
  min-width: fit-content;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  min-width: 100px;
  /* 新增：容器陰影 */
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  /* 修改：改為藍色漸層 */
  background: linear-gradient(90deg, 
    #3b82f6 0%,      /* 藍色 */
    #1d4ed8 50%,     /* 深藍色 */
    #2563eb 100%     /* 中藍色 */
  );
  border-radius: 4px;
  transition: width 0.8s ease-in-out;
  position: relative;
  /* 新增：藍色的光澤效果 */
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

/* 修改：白色跑條效果 */
.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* 修改：白色跑條 */
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(255, 255, 255, 0.6) 30%, 
    rgba(255, 255, 255, 0.8) 50%, 
    rgba(255, 255, 255, 0.6) 70%, 
    transparent 100%
  );
  animation: shimmer 2s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { 
    transform: translateX(-100%); 
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% { 
    transform: translateX(100%); 
    opacity: 0;
  }
}

.progress-percentage {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--primary-color); /* 保持藍色主題 */
  white-space: nowrap;
  min-width: fit-content;
}

.progress-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-align: center;
  margin-top: 0.5rem;
  font-style: italic;
}

.sort-options {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
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

.btn-red {
  background: #ef4444;
}

.btn-red:hover {
  background: #dc2626;
}

.questions-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 300px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.question-item {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
}

.ai-summary-item {
  background: var(--ai-summary-background);
  border: 1px solid var(--ai-summary-border-color);
  border-left: 5px solid var(--ai-summary-accent-border-color);
  box-shadow: 0 4px 12px var(--ai-summary-shadow-color);
  animation: fadeInHighlight 0.5s ease;
}

.ai-summary-item h3 {
  color: var(--ai-summary-header-color);
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 1.15em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-summary-item .ai-content {
  color: var(--ai-summary-content-color);
  line-height: 1.6;
  font-size: 0.95em;
  word-break: break-word;
  white-space: pre-wrap;
}

@keyframes fadeInHighlight {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.question-text {
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
  margin-right: 1rem;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
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

.question-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 12px;
  gap: 16px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.question-votes {
  display: flex;
  gap: 12px;
  align-items: center;
  gap: 0.25rem;
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.vote-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.question-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.question-nickname {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 500;
}

.question-nickname i {
  font-size: 0.875rem;
  color: var(--primary-color);
}

/* 響應式調整 */
@media (max-width: 1024px) {
  .questions-container { 
    min-height: 400px; 
  }
}

@media (max-width: 768px) {
  .panel-header {
    gap: 0.75rem;
  }
  
  .header-row {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  
  .panel-controls { 
    flex-direction: column; 
    gap: 0.5rem; 
    width: 100%;
  }

  .progress-inline {
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
  }
  
  .progress-label {
    font-size: 0.9rem;
  }
  
  .progress-percentage {
    font-size: 1rem;
  }
  
  .progress-bar {
    min-width: 80px;
  }
  
  .progress-description {
    font-size: 0.8rem;
  }
  
  .question-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .question-info {
    align-items: flex-start;
    width: 100%;
  }
  
  .questions-container {
    min-height: 300px;
  }
}

/* 超小螢幕調整 */
@media (max-width: 480px) {
  .progress-inline {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .progress-bar {
    width: 100%;
    min-width: unset;
  }
  
  .questions-container {
    min-height: 250px;
  }
}
</style>