<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand" @click="goHome" aria-label="返回主頁">
          <img src="/icon.png" alt="MBBuddy" class="brand-icon" />
          <!-- <h1>MBBuddy</h1> -->
          <span>參與者</span>
        </div>
        <div class="nav-actions">
          <span class="room-info room-code">代碼: <strong>{{ roomCode || '------' }}</strong></span>
          <div class="user-nickname" @click="openEditNicknameModal" title="點擊修改暱稱">
            <i class="fa-solid fa-user"></i>
            <span>{{ currentNickname || '載入中...' }}</span>
            <i class="fa-solid fa-pen edit-icon"></i>
          </div>
          <div class="status-indicator" :class="'status-' + roomStatus.toLowerCase()">
            <i class="status-icon" :class="statusIcon"></i>
            {{ roomStatusText }}
          </div>
          <div class="timer-display" v-if="remainingTime > 0 && roomStatus === 'Discussion'">
            <span class="timer">{{ formattedRemainingTime }}</span>
          </div>
          <button v-if="roomStatus === 'NotFound' || roomStatus === 'End'" class="btn btn-outline btn-home" @click="goHome">
            <i class="fa-solid fa-home"></i> 返回主頁
          </button>
        </div>
      </div>
    </nav>

    <main class="participant-content">
      <div class="participant-layout">
        <!-- 主題與意見區 -->
        <div class="topic-questions-container">
          <div class="topic-section">
            <div class="topic-header">
              <i class="fa-solid fa-lightbulb"></i>
              <h3>當前主題</h3>
            </div>
            <div class="current-topic">{{ currentTopic }}</div>
          </div>
          <div class="question-submit-section">
            <form @submit.prevent="submitNewQuestion">
              <textarea v-model="newQuestion" placeholder="請輸入您的意見..." :disabled="roomStatus !== 'Discussion'" rows="3"></textarea>
              <button type="submit" class="btn btn-primary" :disabled="!newQuestion.trim() || roomStatus !== 'Discussion'">
                <i class="fa-solid fa-paper-plane"></i> 提交意見
              </button>
            </form>
          </div>
        </div>
        
        <!-- 意見列表面板 -->
        <div class="questions-panel">
          <div class="info-title"><i class="fa-solid fa-comments"></i> 意見列表</div>
          <div v-if="questions.length === 0" class="empty-state">
            <div class="empty-icon"><i class="fa-regular fa-comment-dots"></i></div>
            <div class="empty-text">目前還沒有意見。</div>
          </div>
          <div v-else class="question-list">
            <div v-for="q in questions.slice().reverse()" :key="q.id" class="question-item" :class="{ 'ai-summary-message': q.isAISummary }">
              <div class="question-header">
                <div class="question-meta">
                  <div class="meta-item" v-if="q.nickname"><i class="meta-icon fa-regular fa-user"></i><span>{{ q.nickname }}</span></div>
                  <div class="meta-item"><i class="meta-icon fa-regular fa-clock"></i><span>{{ formatTime(q.ts) }}</span></div>
                </div>
                <div class="question-left">
                  <div v-if="q.answered" class="answered-tag"><i class="fa-solid fa-check"></i> 已回答</div>
                  <div class="question-votes">
                    <button class="vote-button vote-good" @click="voteQuestion(q.id, 'good')" :disabled="q.answered || roomStatus !== 'Discussion'" :class="{'voted': votedQuestions.good.has(q.id)}">
                      <i class="vote-icon fa-solid fa-thumbs-up"></i><span class="vote-count">{{ q.vote_good || 0 }}</span>
                    </button>
                    <button class="vote-button vote-bad" @click="voteQuestion(q.id, 'bad')" :disabled="q.answered || roomStatus !== 'Discussion'" :class="{'voted': votedQuestions.bad.has(q.id)}">
                      <i class="vote-icon fa-solid fa-thumbs-down"></i><span class="vote-count">{{ q.vote_bad || 0 }}</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="question-content">{{ q.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 通知訊息 -->
    <TransitionGroup name="fade">
      <div v-for="msg in notifications" :key="msg.id" :class="['notification', `notification-${msg.type}`]" style="position: fixed; top: 20px; right: 20px; z-index: 2000; margin-bottom: 12px;">
        <span>{{ msg.text }}</span>
        <button @click="removeNotification(msg.id)">&times;</button>
      </div>
    </TransitionGroup>

    <!-- 暱稱 Modals -->
    <NicknameModals 
      v-model:show-name-modal="showNameModal"
      v-model:show-edit-modal="showNicknameEditModal"
      :initial-nickname="currentNickname"
      @nickname-confirmed="handleNicknameConfirmed"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoom } from '../composables/useRoom.js';
import NicknameModals from './NicknameModals.vue';

const newQuestion = ref('');
const showNameModal = ref(false);
const showNicknameEditModal = ref(false);

const {
  roomCode, questions, notifications, roomStatus, currentTopic, remainingTime,
  votedQuestions, currentNickname, roomStatusText, formattedRemainingTime, statusIcon,
  removeNotification, submitQuestion, voteQuestion, updateUserNickname, goHome,
  initializeUser, registerHeartbeat, fetchUserVotes
} = useRoom();

const submitNewQuestion = async () => {
  await submitQuestion(newQuestion.value);
  newQuestion.value = '';
};

const handleNicknameConfirmed = async (nickname) => {
  const isInitialSetup = !currentNickname.value;
  // 修正：在初次設定時，應先加入房間，而不是直接更新暱稱
  await updateUserNickname(nickname, isInitialSetup);
  
  if (isInitialSetup) {
    await registerHeartbeat();
    await fetchUserVotes();
  }

  showNameModal.value = false;
  showNicknameEditModal.value = false;
};

const openEditNicknameModal = () => {
  if (currentNickname.value) {
    showNicknameEditModal.value = true;
  }
};

const formatTime = (ts) => {
  const d = new Date(ts * 1000);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

onMounted(() => {
  const hasNickname = initializeUser();
  if (hasNickname) {
    registerHeartbeat();
    fetchUserVotes();
  } else {
    // 等待 useRoom 中的 fetchRoomState 完成後再決定是否顯示 modal
    setTimeout(() => {
      if (roomStatus.value !== 'NotFound' && roomStatus.value !== 'End') {
        showNameModal.value = true;
      }
    }, 500); // 延遲一點以確保狀態已更新
  }
});
</script>

<style scoped>
@import url('../assets/styles.css');
/* 這裡保留您原有的所有 CSS 樣式 */
.ai-summary-message {
  background-color: #2c4268;
  border-left: 5px solid #4285f4;
  padding: 15px;
  margin: 10px 0;
  border-radius: 8px;
  font-style: italic;
}
.navbar {
  background: var(--background);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
}
.participant-content {
  padding: 1.5rem 1rem;
}
.participant-layout {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}
.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
.topic-questions-container {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 0;
  color: var(--text-primary);
  overflow: hidden;
  transition: all 0.3s ease;
}
.room-info {
  color: #b6c6e6;
  font-size: 1.08em;
}
.room-info strong {
  color: var(--primary-color);
}
.topic-questions-container:hover {
  box-shadow: var(--shadow-lg);
}
.topic-section {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  padding: 24px 28px;
  position: relative;
  overflow: hidden;
}
.topic-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}
.topic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}
.topic-header i {
  font-size: 1.3rem;
  color: #fbbf24;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}
.topic-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
.current-topic {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 18px 22px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 1.1rem;
  line-height: 1.6;
  color: #ffffff;
  position: relative;
  z-index: 1;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
.question-submit-section {
  padding: 24px 28px;
  background: var(--background);
}
.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}
.question-header i {
  font-size: 1.1rem;
  color: var(--primary-color);
}
.question-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.question-submit-section form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.question-submit-section textarea {
  border-radius: 0.75rem;
  padding: 12px 16px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}
.question-submit-section textarea:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  background: var(--background);
}
.question-submit-section textarea::placeholder {
  color: var(--text-secondary);
}
.question-submit-section .btn.btn-primary {
  background: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: 0.75rem;
  padding: 12px 18px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  box-shadow: var(--shadow);
}
.question-submit-section .btn.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}
.question-submit-section .btn.btn-primary:disabled {
  background: var(--secondary-color);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}
.btn.btn-secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.btn.btn-secondary:hover {
  background: linear-gradient(135deg, #7c8fa5, #5a6575);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}
.btn-home {
  display: flex;
  align-items: center;
  gap: 6px;
}
.questions-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 24px 28px;
  color: var(--text-primary);
  min-width: 0;
  overflow-y: auto;
  transition: all 0.3s ease;
}
.questions-panel:hover {
  box-shadow: var(--shadow-lg);
}
.questions-panel .info-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding-bottom: 12px;
}
.questions-panel .info-title i {
  color: var(--primary-color);
  font-size: 1.3rem;
}
.question-list {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}
.question-item {
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 16px 18px;
  background: var(--background);
  transition: all 0.2s ease;
}
.question-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.question-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.question-votes {
  display: flex;
  align-items: center;
  gap: 8px;
}
.vote-button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.vote-button:hover:not(:disabled) {
  background: var(--background);
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.vote-button.vote-good.voted {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}
.vote-button.vote-bad.voted {
  background: rgba(220, 38, 38, 0.1);
  color: var(--danger-color);
  border-color: var(--danger-color);
}
.vote-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.vote-icon {
  font-size: 1em;
}
.vote-count {
  font-weight: 500;
}
.answered-tag {
  background: rgba(5, 150, 105, 0.1);
  color: var(--success-color);
  font-size: 0.875rem;
  border-radius: 0.375rem;
  padding: 4px 8px;
  margin-right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(5, 150, 105, 0.2);
}
.question-content {
  margin: 12px 0;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
  color: var(--text-primary);
  font-size: 1rem;
}
.question-meta {
  font-size: 0.875rem;
  color: var(--text-secondary);
  display: flex;
  gap: 16px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.meta-icon {
  color: var(--text-secondary);
}
.empty-state {
  text-align: center;
  color: var(--text-secondary);
  margin: 50px 0;
  padding: 30px;
  background: var(--surface);
  border-radius: 1rem;
  border: 1px dashed var(--border);
}
.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  color: var(--text-secondary);
}
.empty-text {
  font-size: 1.1em;
  max-width: 320px;
  margin: 0 auto;
  line-height: 1.6;
  color: var(--text-secondary);
}
.btn-home {
  display: flex;
  align-items: center;
  gap: 6px;
}
@media (max-width: 768px) {
  .nav-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  .question-list {
    grid-template-columns: 1fr;
  }
  .status-indicator {
    font-size: 0.9rem;
    padding: 4px 8px;
  }
  .timer {
    font-size: 1.1rem;
  }
  .topic-questions-container {
    border-radius: 12px;
  }
  .topic-section {
    padding: 20px 20px;
  }
  .question-submit-section {
    padding: 20px 20px;
  }
  .topic-header h3 {
    font-size: 1.2rem;
  }
  .current-topic {
    padding: 16px 18px;
    font-size: 1.1rem;
  }
  .questions-panel {
    padding: 20px 20px;
  }
}
@media (min-width: 1024px) {
  .participant-layout {
    grid-template-columns: 1fr 1.35fr;
    align-items: start;
  }
  .topic-questions-container {
    margin-bottom: 0;
  }
  .questions-panel {
    grid-column: auto;
  }
}
@media (max-width: 480px) {
  .participant-content {
    padding: 16px 12px;
  }
  .nav-container {
    padding: 0 12px;
    flex-direction: column;
    height: auto;
    padding: 10px;
  }
  .nav-brand {
    margin-bottom: 10px;
    flex-wrap: nowrap;
  }
  .nav-actions {
    width: 100%;
    justify-content: space-between;
  }
  .topic-section {
    padding: 18px 16px;
  }
  .question-submit-section {
    padding: 18px 16px;
  }
  .topic-header h3 {
    font-size: 1.1rem;
  }
  .current-topic {
    padding: 14px 16px;
    font-size: 1rem;
  }
  .questions-panel {
    padding: 18px 16px;
  }
  .question-item {
    padding: 16px 18px;
  }
  .vote-button {
    padding: 5px 10px;
    font-size: 0.85rem;
  }
}
.user-nickname {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  position: relative;
  max-width: 200px;
}
.user-nickname:hover {
  background: var(--background);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}
.user-nickname span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  flex: 1;
}
.user-nickname .edit-icon {
  opacity: 0.6;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}
.user-nickname:hover .edit-icon {
  opacity: 1;
  color: var(--primary-color);
}
</style>
