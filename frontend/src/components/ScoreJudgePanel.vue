<template>
  <div class="score-judge-panel">
    <!-- 加載狀態 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在載入討論數據...</p>
    </div>

    <!-- 主要內容 -->
    <div v-else class="panel-content">
      <!-- 頁面標題 -->
      <div class="summary-header">
        <div class="header-content">
          <h1>
            <i class="fa-solid fa-chart-line"></i>
            討論結算報告
          </h1>
          <p class="meeting-info">
            討論主題：{{ meetingTitle }} | 
            參與人數：{{ participants.length }} 人 |
            總留言：{{ questions.length }} 條
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline" @click="exportAllTopics">
            <i class="fa-solid fa-download"></i>
            匯出報告
          </button>
          <button class="btn btn-primary" @click="backToHome">
            <i class="fa-solid fa-home"></i>
            返回大廳
          </button>
        </div>
      </div>

      <!-- 討論統計概覽 -->
      <div class="overview-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fa-solid fa-users"></i>
            </div>
            <div class="stat-content">
              <h3>{{ participants.length }}</h3>
              <p>參與人數</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fa-solid fa-comments"></i>
            </div>
            <div class="stat-content">
              <h3>{{ totalComments }}</h3>
              <p>總留言數</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fa-solid fa-thumbs-up"></i>
            </div>
            <div class="stat-content">
              <h3>{{ totalVotes }}</h3>
              <p>總投票數</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fa-solid fa-star"></i>
            </div>
            <div class="stat-content">
              <h3>{{ averageScore }}</h3>
              <p>平均分數</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 參與者評分列表 -->
      <div class="participants-section">
        <h2>
          <i class="fa-solid fa-trophy"></i>
          參與者評分排行榜
        </h2>
        
        <div v-if="rankedParticipants.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fa-regular fa-face-sad-tear"></i>
          </div>
          <h3>尚無參與者數據</h3>
          <p>請確認討論中有參與者發言並返回主持台重新進入</p>
        </div>

        <div v-else class="participants-list">
          <div 
            v-for="(participant, index) in rankedParticipants" 
            :key="participant.nickname"
            :class="['participant-card', getRankClass(index)]"
          >
            <!-- 排名 -->
            <div class="rank-badge">
              <span v-if="index < 3" class="rank-medal">
                <i :class="getRankIcon(index)"></i>
              </span>
              <span v-else class="rank-number">{{ index + 1 }}</span>
            </div>

            <!-- 參與者資訊 -->
            <div class="participant-info">
              <div class="participant-avatar">
                <i class="fa-solid fa-user"></i>
              </div>
              <div class="participant-details">
                <h3>{{ participant.nickname }}</h3>
                <p class="participation-level">{{ getParticipationLevel(participant.score) }}</p>
              </div>
            </div>

            <!-- 評分圓環 -->
            <div class="score-circle">
              <svg class="progress-ring" width="80" height="80">
                <circle
                  class="progress-ring-bg"
                  stroke="#e5e7eb"
                  stroke-width="6"
                  fill="transparent"
                  r="34"
                  cx="40"
                  cy="40"
                />
                <circle
                  class="progress-ring-fill"
                  :stroke="getScoreColor(participant.score)"
                  stroke-width="6"
                  fill="transparent"
                  r="34"
                  cx="40"
                  cy="40"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="circumference - (participant.score / 100) * circumference"
                />
              </svg>
              <div class="score-text">
                <span class="score-number">{{ participant.score }}</span>
                <span class="score-unit">分</span>
              </div>
            </div>

            <!-- 詳細數據 -->
            <div class="participant-stats">
              <div class="stat-item">
                <i class="fa-solid fa-comment"></i>
                <span>{{ participant.commentCount }} 條留言</span>
              </div>
              <div class="stat-item">
                <i class="fa-solid fa-thumbs-up"></i>
                <span>{{ participant.votesReceived }} 票獲得</span>
              </div>
              <div class="stat-item">
                <i class="fa-solid fa-text-height"></i>
                <span>平均 {{ participant.avgLength }} 字</span>
              </div>
              <div class="stat-item">
                <i class="fa-solid fa-fire"></i>
                <span>活躍度 {{ participant.activityRate }}%</span>
              </div>
            </div>

            <!-- 展開詳情按鈕 -->
            <button 
              class="details-toggle"
              @click="toggleDetails(participant.nickname)"
            >
              <i :class="participant.showDetails ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down'"></i>
            </button>

            <!-- 詳細留言 -->
            <div v-if="participant.showDetails" class="participant-comments">
              <h4>主要留言內容</h4>
              <div class="comments-list">
                <div 
                  v-for="comment in participant.comments.slice(0, 3)" 
                  :key="comment.id"
                  class="comment-item"
                >
                  <p>{{ comment.content }}</p>
                  <div class="comment-meta">
                    <span>{{ formatTime(comment.timestamp) }}</span>
                    <span>👍 {{ comment.votes }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增：通知組件 -->
    <NotificationToast
      :notifications="notifications"
      @remove-notification="removeNotification"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '@/utils/api'
import NotificationToast from './NotificationToast.vue'

const router = useRouter()
const route = useRoute()

// 修正：Props 不能在 default 中直接使用 route，改為在組件內部處理
const props = defineProps({
  roomCode: {
    type: String,
    default: ''
  },
  meetingTitle: {
    type: String,
    default: '未命名討論'
  }
})

// 響應式數據 - 修正：在這裡處理 route 參數
const loading = ref(true)
const participants = ref([])
const questions = ref([])
const meetingTitle = ref(props.meetingTitle || route.query.title || '未命名討論')
const roomCode = ref(props.roomCode || route.query.room || '')

// 計算屬性
const totalComments = computed(() => {
  return questions.value.filter(q => !q.isAISummary).length
})

const totalVotes = computed(() => {
  return questions.value.reduce((sum, q) => sum + (q.vote_good || 0) + (q.vote_bad || 0), 0)
})

const averageScore = computed(() => {
  if (participants.value.length === 0) return 0
  const totalScore = participants.value.reduce((sum, p) => sum + p.score, 0)
  return Math.round(totalScore / participants.value.length)
})

const rankedParticipants = computed(() => {
  return [...participants.value].sort((a, b) => b.score - a.score)
})

const circumference = computed(() => 2 * Math.PI * 34)

// 修正：從 HostPanel.vue 複製 exportAllTopics 函數
async function exportAllTopics() {
  if (!roomCode.value) {
    showNotification('找不到討論室代碼', 'error')
    return
  }

  const exportButton = document.querySelector('.btn-outline')
  if (exportButton) {
    exportButton.disabled = true
    exportButton.innerHTML = '<span class="spinner-sm"></span> 匯出中...'
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/export_pdf?room=${roomCode.value}`)
    
    if (!response.ok) {
      throw new Error(`PDF 匯出失敗: ${response.statusText}`)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    
    // 從 Content-Disposition header 獲取檔名
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `MBBuddy-Report-${roomCode.value}.pdf`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1]
      }
    }
    
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()

    showNotification('PDF 匯出成功！', 'success')

  } catch (error) {
    console.error('匯出 PDF 時出錯:', error)
    showNotification(error.message || '匯出失敗，請稍後再試', 'error')
  } finally {
    if (exportButton) {
      exportButton.disabled = false
      exportButton.innerHTML = '<i class="fa-solid fa-download"></i> 匯出報告'
    }
  }
}

// 新增：通知函數（從 HostPanel 複製）
const notifications = ref([])

function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}

function removeNotification(i) {
  notifications.value.splice(i, 1)
}

// 方法
async function fetchMeetingData() {
  if (!roomCode.value) {
    console.error('沒有房間代碼')
    loading.value = false
    return
  }

  try {
    console.log('🔍 開始載入討論數據...')
    
    // 直接獲取留言數據 - 這個端點是有效的
    const questionsResponse = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments`)
    if (questionsResponse.ok) {
      const questionsData = await questionsResponse.json()
      questions.value = questionsData.comments || []
      console.log('📝 載入留言數據:', questions.value.length, '條')
    } else {
      console.error('獲取留言失敗:', questionsResponse.status)
      questions.value = []
    }

    // 從留言中提取唯一的參與者
    const uniqueParticipants = [...new Set(
      questions.value
        .filter(q => q.nickname && !q.isAISummary)
        .map(q => q.nickname)
    )].map(nickname => ({ nickname }))
    
    console.log('👤 從留言提取的參與者:', uniqueParticipants)

    if (uniqueParticipants.length > 0) {
      // 計算每個參與者的分數
      participants.value = uniqueParticipants.map(calculateParticipantScore)
      console.log('🏆 計算完成的參與者評分:', participants.value)
    } else {
      console.warn('⚠️ 沒有找到任何參與者')
      participants.value = []
    }

    // 嘗試從第一個留言獲取討論相關資訊
    if (questions.value.length > 0) {
      const firstComment = questions.value[0]
      if (firstComment.room_title && firstComment.room_title !== meetingTitle.value) {
        meetingTitle.value = firstComment.room_title
        console.log('📝 從留言更新討論標題:', meetingTitle.value)
      }
    }

  } catch (error) {
    console.error('❌ 載入討論數據失敗:', error)
    showNotification('載入討論數據失敗，請稍後再試', 'error')
  } finally {
    loading.value = false
  }
}

// 修正：改善參與者評分計算
function calculateParticipantScore(participant) {
  const userComments = questions.value.filter(q => 
    q.nickname === participant.nickname && !q.isAISummary
  )
  
  console.log(`🔍 計算 ${participant.nickname} 的評分:`)
  console.log(`  - 總留言數: ${questions.value.length}`)
  console.log(`  - 該用戶留言數: ${userComments.length}`)
  console.log(`  - 留言內容預覽:`, userComments.slice(0, 3).map(c => c.content?.substring(0, 30) + '...'))

  if (userComments.length === 0) {
    return {
      nickname: participant.nickname,
      score: 0,
      commentCount: 0,
      votesReceived: 0,
      avgLength: 0,
      activityRate: 0,
      comments: [],
      showDetails: false
    }
  }
  
  // 基礎數據計算
  const commentCount = userComments.length
  const totalVotesReceived = userComments.reduce((sum, c) => sum + (c.vote_good || 0) + (c.vote_bad || 0), 0)
  const totalLength = userComments.reduce((sum, c) => sum + (c.content?.length || 0), 0)
  const avgLength = Math.round(totalLength / commentCount)
  
  // 評分計算 (滿分100分)
  const commentScore = Math.min(commentCount * 15, 40) // 留言數量分 (40%)
  const qualityScore = Math.min(avgLength / 10, 25) // 留言品質分 (25%)
  const interactionScore = Math.min(totalVotesReceived * 5, 20) // 互動得分 (20%)
  const contributionScore = Math.min(commentCount * 3 + totalVotesReceived * 2, 15) // 貢獻度 (15%)
  
  const totalScore = Math.round(commentScore + qualityScore + interactionScore + contributionScore)
  const activityRate = Math.min(Math.round((commentCount / Math.max(totalComments.value, 1)) * 100), 100)
  
  const result = {
    nickname: participant.nickname,
    score: Math.min(totalScore, 100),
    commentCount,
    votesReceived: totalVotesReceived,
    avgLength,
    activityRate,
    comments: userComments.map(c => ({
      id: c.id,
      content: c.content,
      timestamp: c.ts,
      votes: (c.vote_good || 0) + (c.vote_bad || 0)
    })),
    showDetails: false
  }

  console.log(`✅ ${participant.nickname} 評分結果:`)
  console.log(`  - 總分: ${result.score}`)
  console.log(`  - 留言數: ${result.commentCount}`)
  console.log(`  - 獲得投票: ${result.votesReceived}`)
  console.log(`  - 平均字數: ${result.avgLength}`)
  
  return result
}

function getRankClass(index) {
  if (index === 0) return 'rank-first'
  if (index === 1) return 'rank-second'
  if (index === 2) return 'rank-third'
  return 'rank-normal'
}

function getRankIcon(index) {
  const icons = [
    'fa-solid fa-crown', // 第一名
    'fa-solid fa-medal',  // 第二名
    'fa-solid fa-award'   // 第三名
  ]
  return icons[index]
}

function getScoreColor(score) {
  if (score >= 80) return '#22c55e' // 綠色
  if (score >= 60) return '#eab308' // 黃色
  if (score >= 40) return '#f97316' // 橙色
  return '#ef4444' // 紅色
}

function getParticipationLevel(score) {
  if (score >= 90) return '卓越參與者'
  if (score >= 80) return '活躍參與者'
  if (score >= 60) return '積極參與者'
  if (score >= 40) return '一般參與者'
  return '待加強參與'
}

function toggleDetails(nickname) {
  const participant = participants.value.find(p => p.nickname === nickname)
  if (participant) {
    participant.showDetails = !participant.showDetails
  }
}

function formatTime(timestamp) {
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

function backToHome() {
  router.push('/')
}

// 初始化
onMounted(async () => {
  console.log('🚀 ScoreJudgePanel 初始化')
  console.log('📋 房間代碼:', roomCode.value)
  console.log('📝 討論標題:', meetingTitle.value)
  
  await fetchMeetingData()
})
</script>

<style scoped>
.score-judge-panel {
  min-height: 100vh;
  background: var(--background);
  padding: 2rem 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.panel-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* 按鈕樣式 - 與 HostPanel 完全一致 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  border: 1px solid transparent;
  text-decoration: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
  border-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-outline {
  background-color: transparent;
  color: var(--primary-color);
  border-color: var(--border);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.btn-secondary {
  background-color: var(--surface);
  color: var(--text-primary);
  border-color: var(--border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--background);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  border-color: #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
  border-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-success {
  background-color: #22c55e;
  color: white;
  border-color: #22c55e;
}

.btn-success:hover:not(:disabled) {
  background-color: #16a34a;
  border-color: #16a34a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.btn-large {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

/* 按鈕圖標樣式 */
.btn i {
  font-size: 0.875rem;
  flex-shrink: 0;
}

.btn-large i {
  font-size: 1rem;
}

.btn-small i {
  font-size: 0.75rem;
}

/* 頁面標題 */
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--surface);
  border-radius: 1rem;
  border: 1px solid var(--border);
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-content h1 i {
  color: var(--primary-color);
}

.meeting-info {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* 統計概覽 */
.overview-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.stat-content p {
  color: var(--text-secondary);
  margin: 0;
}

/* 參與者區塊 */
.participants-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.participants-section h2 i {
  color: var(--primary-color);
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

.participants-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.participant-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  position: relative;
}

.rank-first {
  border-color: #ffd700;
  background: linear-gradient(135deg, var(--surface) 0%, rgba(255, 215, 0, 0.1) 100%);
}

.rank-second {
  border-color: #c0c0c0;
  background: linear-gradient(135deg, var(--surface) 0%, rgba(192, 192, 192, 0.1) 100%);
}

.rank-third {
  border-color: #cd7f32;
  background: linear-gradient(135deg, var(--surface) 0%, rgba(205, 127, 50, 0.1) 100%);
}

.rank-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
}

.rank-medal {
  font-size: 2rem;
}

.rank-first .rank-medal i {
  color: #ffd700;
}

.rank-second .rank-medal i {
  color: #c0c0c0;
}

.rank-third .rank-medal i {
  color: #cd7f32;
}

.rank-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.participant-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.participant-avatar {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.participant-details h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.participation-level {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

/* 評分圓環 */
.score-circle {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-fill {
  transition: stroke-dashoffset 1s ease-in-out;
  stroke-linecap: round;
}

.score-text {
  position: absolute;
  text-align: center;
}

.score-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.score-unit {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 參與者統計 */
.participant-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  min-width: 200px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-item i {
  color: var(--primary-color);
  width: 16px;
}

.details-toggle {
  background: none;
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.details-toggle:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* 詳細留言 */
.participant-comments {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 1rem 1rem;
  padding: 1.5rem;
  z-index: 10;
}

.participant-comments h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.comment-item {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1rem;
}

.comment-item p {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .summary-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
    width: 100%;
  }
  
  .btn {
    flex: 1;
    justify-content: center;
    min-width: 140px;
  }
  
  .participant-card {
    flex-direction: column;
    text-align: center;
  }
  
  .participant-stats {
    grid-template-columns: 1fr;
  }
  
  .participant-comments {
    position: relative;
    top: auto;
    margin-top: 1rem;
    border-top: 1px solid var(--border);
    border-radius: 1rem;
  }
}
</style>