<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand" @click="router.push('/')" aria-label="返回主頁">
          <img src="/icon.png" alt="MBBuddy" class="brand-icon" />
          <!-- <h1>MBBuddy</h1> -->
          <!-- <span>主持人面板</span> -->
        </div>
        <div class="nav-actions">
          <div class="room-info">
            <span class="room-code">討論代碼: <strong>{{ roomCode || '------' }}</strong></span>
            <span class="participant-count">參與人數: <strong>{{ participantsList.length }}</strong></span>
            <span class="room-status" :class="'status-' + roomStatus.toLowerCase()" @click="toggleRoomStatus">
              狀態: <strong>{{ roomStatusText }}</strong>
            </span>
          </div>
          <button class="btn btn-outline" @click="endRoom">結束討論</button>
        </div>
      </div>
    </nav>
    
    <main class="host-content">
      <div class="host-layout">
        <!-- 左側主題列表 -->
        <TopicsSidebar
          :topics="topics"
          :selected-topic-index="selectedTopicIndex"
          :is-collapsed="isSidebarCollapsed"
          @toggle-sidebar="toggleSidebar"
          @select-topic="selectTopic"
          @edit-topic="startEditTopic"
          @add-new-topic="addNewTopic"
          @export-all-topics="exportAllTopics"
          @generate-mind-map="showMindMapModal = true"
        />
        
        <!-- 意見列表區域 -->
        <div class="questions-section">
          <!-- 傳遞 ref 值到 QuestionsList -->
          <QuestionsList
            :questions="questions"
            :current-topic-title="topics[selectedTopicIndex]?.title || '未選擇主題'"
            :sort-by="sortBy"
            :discussion-progress="discussionProgress"
            :discussion-progress-text="discussionProgressText"
            @delete-question="deleteQuestion"
            @summary-ai="summaryAI"
            @clear-all-questions="clearAllQuestions"
            @update-sort-by="sortBy = $event"
          />
        </div>
        
        <!-- 控制面板 -->
        <ControlPanel
          :active-tab="controlTab"
          :room="room"
          :room-link="roomLink"
          :allow-join="allowJoin"
          :settings="settings"
          :timer-running="timerRunning"
          :formatted-remaining-time="formattedRemainingTime"
          :total-questions="questions.length"
          :total-votes="totalVotes"
          :participants-list="participantsList"
          :is-editing-room-info="isEditingRoomInfo"
          :edit-room-title="editRoomTitle"
          :edit-room-summary="editRoomSummary"
          @set-active-tab="controlTab = $event"
          @show-qrcode="showQRCode"
          @copy-room-link="copyRoomLink"
          @update-allow-join="allowJoin = $event"
          @update:edit-room-title="editRoomTitle = $event"
          @update:edit-room-summary="editRoomSummary = $event"
          @start-edit-room-info="startEditRoomInfo"
          @cancel-edit-room-info="cancelEditRoomInfo"
          @update-room-info="updateRoomInfo"
          @toggle-timer="toggleTimer"
          @show-timer-settings="showTimerSettings"
          @terminate-timer="terminateTimer"
          @update-settings="settings = $event"
          @remove-participant="removeParticipant"
        />
      </div>
    </main>

    <!-- 通知訊息 -->
    <NotificationToast
      :notifications="notifications"
      @remove-notification="removeNotification"
    />

    <!-- QR Code 彈窗 -->
    <QRCodeModal
      :is-visible="isQRCodeModalVisible"
      :room-code="roomCode"
      :room-link="roomLink"
      @hide-modal="hideQRCode"
    />

    <!-- 計時器設定彈窗 -->
    <TimerModal
      :is-visible="isTimerSettingsVisible"
      :timer-settings="timerSettings"
      @hide-modal="hideTimerSettings"
      @apply-settings="applyTimerSettings"
    />

    <!-- 主題編輯彈窗 -->
    <TopicEditModal
      :is-visible="editingTopicIndex !== null || isAddingTopic"
      :is-adding-topic="isAddingTopic"
      :editing-topic-name="editingTopicName"
      @cancel-edit="cancelTopicModal"
      @confirm-edit="handleTopicModalConfirm"
    />
    
    <!-- AI心智圖彈窗 -->
    <MindMapModal
      :show="showMindMapModal"
      @close="showMindMapModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'

// 導入子組件
import TopicsSidebar from './TopicsSidebar.vue'
import QuestionsList from './QuestionsList.vue'
import ControlPanel from './ControlPanel.vue'
import NotificationToast from './NotificationToast.vue'
import QRCodeModal from './QRCodeModal.vue'
import TimerModal from './TimerModal.vue'
import TopicEditModal from './TopicEditModal.vue'
import MindMapModal from './MindMapModal.vue'
import { BackgroundStyleTracker } from '@/utils/backgroundStyleTracker'

// 控制面板 tab 狀態
const controlTab = ref('control')
function removeParticipant(index) {
  participantsList.value.splice(index, 1)
  showNotification('已移除成員', 'info')
}

import { API_BASE_URL } from '@/utils/api'

// 狀態
const room = ref(null)
const roomCode = ref('')
const questions = ref([])
const roomStatus = ref('NotFound') // 房間狀態：NotFound, Stop, Discussion
// 房間資訊編輯
const editRoomTitle = ref('')
const editRoomSummary = ref('')
// 主持人欄位已移除
const isEditingRoomInfo = ref(false)
const settings = reactive({ allowQuestions: true, allowVoting: true })
const sortBy = ref('votes')
const notifications = ref([])
const isQRCodeModalVisible = ref(false)
const qrcodeSize = ref(window.innerWidth < 768 ? 320 : 640)
const router = useRouter()

// 允許加入房間開關
const allowJoin = ref(true)

// 計時器相關
const remainingTime = ref(0) // 剩餘時間（以秒為單位）
const initialTime = ref(0) // 初始設定的時間
const seededFromBackend = ref(false) // 是否從後端初始化了計時器設定（首次進入）
const timerRunning = ref(false) // 計時器是否運行中
const timerInterval = ref(null) // 計時器間隔引用
const isTimerSettingsVisible = ref(false) // 計時器設定彈窗是否可見
const timerSettings = reactive({
  hours: 0,
  minutes: 5,
  seconds: 0
})
const autoChangeStatus = ref(true)

// 側邊欄與主題相關
const isSidebarCollapsed = ref(false)
const showMindMapModal = ref(false)
const topics = ref([
  { title: '主題 1', content: '', timestamp: new Date().toISOString() }
])
const selectedTopicIndex = ref(0)
const editingTopicIndex = ref(null)
const isAddingTopic = ref(false) // 新增：控制新增主題彈窗
const editingTopicName = ref('')
const originalTopicNameToEdit = ref('') // 新增：儲存原始主題名稱
const editTopicTab = ref('manual')
const customAiPrompt = ref('')
const isGeneratingTopic = ref(false)
const topicSwipeState = ref({}); // { index: { startX, currentX, translateX, isDragging } }

// 取得參與者名單
const participantsList = ref([])

// 統計
const totalVotes = computed(() => questions.value.reduce((sum, q) => sum + (q.vote_good || 0) + (q.vote_bad || 0), 0))

// 分享連結
const roomLink = computed(() => {
  return `${window.location.origin}/participant?room=${roomCode.value || ''}`
})

// 房間狀態顯示文字
const roomStatusText = computed(() => {
  switch(roomStatus.value) {
    case 'NotFound': return '未啟動';
    case 'Stop': return '休息中';
    case 'Discussion': return '討論中';
    case 'End': return '已結束';
    default: return '未知';
  }
})

// 修改：使用 ref 而不是 computed，避免歸零問題
const discussionProgress = ref(0)
const discussionProgressText = ref('等待討論開始...')

// 新增：計算討論進度的函數 - 加入防歸零邏輯
function calculateDiscussionProgress() {
  // 防護：如果數據還在載入中，返回當前進度
  if (!questions.value || !Array.isArray(questions.value)) {
    console.log('🔍 questions 還在載入中，保持當前進度:', discussionProgress.value)
    return discussionProgress.value
  }

  if (questions.value.length === 0) {
    console.log('🔍 沒有留言，進度為 0')
    return 0
  }

  // 過濾掉 AI 總結，只計算真實留言
  const realComments = questions.value.filter(q => q && !q.isAISummary)
  if (realComments.length === 0) {
    console.log('🔍 沒有真實留言，進度為 0')
    return 0
  }

  const participantCount = Math.max(participantsList.value.length, 1)

  // 1. 留言數量評分 (40%)
  const commentsPerParticipant = realComments.length / participantCount
  const commentScore = Math.min(commentsPerParticipant * 3, 40) // 每人5條留言達到滿分

  // 2. 投票活躍度評分 (30%)
  const totalVotesCount = realComments.reduce((sum, q) => 
    sum + (q.vote_good || 0) + (q.vote_bad || 0), 0
  )
  const votesPerComment = realComments.length > 0 ? totalVotesCount / realComments.length : 0
  const voteScore = Math.min(votesPerComment * 6, 30) // 每條留言5票達到滿分

  // 3. 參與者比例評分 (20%)
  const uniqueParticipants = new Set(
    realComments
      .filter(q => q.nickname && q.nickname !== "MBBuddy 小助手")
      .map(q => q.nickname)
  ).size
  const participationRate = uniqueParticipants / participantCount
  const participationScore = participationRate * 20

  // 4. 討論深度評分 (10%)
  const avgLength = realComments.reduce((sum, q) => sum + (q.content?.length || 0), 0) / realComments.length
  const depthScore = Math.min(avgLength / 50, 10) // 平均500字達到滿分

  const totalScore = commentScore + voteScore + participationScore + depthScore

  // debug 資訊
  console.log('🔍 進度計算詳情:', {
    realComments: realComments.length,
    participantCount,
    commentsPerParticipant,
    commentScore,
    totalVotesCount,
    votesPerComment,
    voteScore,
    uniqueParticipants,
    participationRate,
    participationScore,
    avgLength,
    depthScore,
    totalScore: Math.min(Math.round(totalScore), 100)
  })

  return Math.min(Math.round(totalScore), 100)
}

// 新增：更新進度的函數 - 加入防抖動邏輯
function updateDiscussionProgress() {
  try {
    const newProgress = calculateDiscussionProgress()
    const newProgressText = generateProgressText(newProgress)
    
    // 只有當新進度與當前進度差異明顯時才更新
    if (Math.abs(newProgress - discussionProgress.value) >= 1 || newProgress === 0) {
      discussionProgress.value = newProgress
      discussionProgressText.value = newProgressText
      console.log('✅ 進度更新:', newProgress + '%', newProgressText)
    } else {
      console.log('🔍 進度變化不大，不更新:', discussionProgress.value, '->', newProgress)
    }
  } catch (error) {
    console.error('❌ 進度計算錯誤:', error)
  }
}

// 新增：生成進度描述文字的函數
function generateProgressText(progress) {
  const realComments = questions.value.filter(q => q && !q.isAISummary)
  const participantCount = Math.max(participantsList.value.length, 1)
  const activeParticipants = new Set(
    realComments
      .filter(q => q.nickname && q.nickname !== "MBBuddy 小助手")
      .map(q => q.nickname)
  ).size

  if (progress === 0) return '等待討論開始...'
  if (progress < 10) return `討論剛開始 (${activeParticipants}/${participantCount} 人參與，${realComments.length} 條留言)`
  if (progress < 25) return `討論逐漸熱絡 (${realComments.length} 條留言，${totalVotes.value} 次投票)`
  if (progress < 45) return `討論持續活躍中 (${activeParticipants} 人積極參與)`
  if (progress < 65) return `討論非常熱烈 (豐富的互動交流)`
  if (progress < 85) return `討論達到高潮 (${realComments.length} 條深度交流)`
  return `討論圓滿充實 (完美的參與度！)`
}

// 修改：使用防抖動的 watch
let progressUpdateTimer = null
watch([questions, participantsList], () => {
  // 清除之前的計時器
  if (progressUpdateTimer) {
    clearTimeout(progressUpdateTimer)
  }
  
  // 延遲更新，避免頻繁計算
  progressUpdateTimer = setTimeout(() => {
    updateDiscussionProgress()
  }, 100) // 100ms 防抖動
}, { 
  deep: true,
  immediate: false // 不立即執行
})

// 上方狀態顯示切換
function toggleRoomStatus() {
  if (roomStatus.value === 'Discussion') {
    setRoomStatus('Stop')
  } else if (roomStatus.value === 'Stop') {
    setRoomStatus('Discussion')
  }
}

async function fetchParticipants() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/participants?room=${roomCode.value}`)
    const data = await res.json()
    participantsList.value = data.participants || []
  } catch (err) {
    console.error('取得參與者失敗', err)
  }
}

// 意見排序
const sortedQuestions = computed(() => {
  // 1. 先將 AI 總結和一般留言分開
  const aiSummaries = questions.value.filter(q => q.isAISummary);
  const normalQuestions = questions.value.filter(q => !q.isAISummary);

  // 2. 只對一般留言進行排序
  const sortedNormal = [...normalQuestions].sort((a, b) => {
    if (sortBy.value === 'votes') {
      const aVotes = (a.vote_good || 0) - (a.vote_bad || 0);
      const bVotes = (b.vote_good || 0) - (b.vote_bad || 0);
      if (bVotes !== aVotes) return bVotes - aVotes;
    }
    // 時間排序
    return (b.ts || 0) - (a.ts || 0);
  });

  // 3. 最後，將 AI 總結放回陣列的最前面
  return [...aiSummaries, ...sortedNormal];
});

// 修改：在資料載入完成後初始化進度
async function fetchQuestions() {
  try {
    // 修復：使用正確的 RESTful API 端點
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments`);
    if (response.ok) {
      const data = await response.json();
      questions.value = data.comments || [];
      
      // 資料載入完成後，立即更新一次進度
      nextTick(() => {
        updateDiscussionProgress()
      })
    } else if (response.status === 404) {
      // 如果房間不存在，清空問題列表
      questions.value = [];
      console.warn('房間不存在或沒有評論');
    } else {
      console.error('獲取評論失敗:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('載入意見時出錯:', error);
  }
}

// 取得 Room 資訊
async function loadRoom() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('room')
  if (!code) {
    // 處理沒有 room code 的情況
    return
  }
  roomCode.value = code

  // --- 檢查是否為新建立的房間 ---
  const isNewRoom = urlParams.get('new') === 'true'

  try {
    const resp = await fetch(`${API_BASE_URL}/api/rooms`)
    if (!resp.ok) throw new Error('無法獲取房間列表')
    const data = await resp.json()
    const roomData = data.rooms.find(r => r.code === code)

    if (roomData) {
      room.value = roomData
      // 從 roomData 更新 topics
      const roomTopicsResp = await fetch(`${API_BASE_URL}/api/room_topics?room=${code}`)
      const roomTopicsData = await roomTopicsResp.json()
      if (roomTopicsData.topics) {
        topics.value = roomTopicsData.topics.map(t => ({ title: t, content: '', timestamp: new Date().toISOString() }))
        if (topics.value.length > 0) {
          selectedTopicIndex.value = 0
        }
      }

      // 如果是新房間，觸發 AI 生成主題
      if (isNewRoom && room.value) {
        generateAndDisplayTopics()
      }
    } else {
      // 房間不存在的處理
      showNotification('找不到指定的討論室', 'error')
      router.push('/')
    }
  } catch (error) {
    console.error('載入房間資訊時發生錯誤:', error)
    showNotification('載入房間資訊失敗', 'error')
  }
}

// --- AI 生成並逐一顯示主題 ---
async function generateAndDisplayTopics() {
  // 1. 先清空現有主題並顯示載入狀態
  const originalTitle = room.value?.title || '新討論'
  topics.value = [{ title: 'AI 主題生成中...', content: '', timestamp: '' }]
  selectedTopicIndex.value = 0

  try {
    // 2. 呼叫 AI 生成主題
    const topicResp = await fetch(`${API_BASE_URL}/ai/generate_topics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        meeting_title: originalTitle,
        topic_count: room.value?.topic_count || 3,
      })
    })
    if (!topicResp.ok) throw new Error("AI 主題生成失敗")
    const topicData = await topicResp.json()
    const generatedTopics = topicData.topics || []

    if (generatedTopics.length === 0) {
      throw new Error("AI 未能生成任何主題，將使用預設主題")
    }

    // 3. 呼叫新 API 將主題添加到房間
    await fetch(`${API_BASE_URL}/api/room/add_topics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room: roomCode.value, topics: generatedTopics }),
    });


    // 4. 逐一顯示主題
    topics.value = [] // 清空 loading 狀態
    for (let i = 0; i < generatedTopics.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 300)) // 延遲效果
      topics.value.push({
        title: generatedTopics[i],
        content: '',
        timestamp: new Date().toISOString()
      })
    }
    
    // 預設選中第一個主題並切換
    if (topics.value.length > 0) {
      selectedTopicIndex.value = 0
      await switchTopic(topics.value[0].title)
    }

    // 5. 清理臨時主題（載入狀態和錯誤訊息）
    try {
      const cleanResp = await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
      if (cleanResp.ok) {
        const cleanData = await cleanResp.json()
        if (cleanData.success && cleanData.cleaned_topics.length > 0) {
          console.log(`已清理臨時主題: ${cleanData.cleaned_topics.join(', ')}`)
        }
      }
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
      // 清理失敗不影響主流程
    }

  } catch (err) {
    showNotification(err.message, 'error')
    // 如果失敗，還原為預設主題
    topics.value = [{ title: '預設主題', content: '', timestamp: new Date().toISOString() }]
    selectedTopicIndex.value = 0
    
    // 即使生成失敗，也嘗試清理可能存在的臨時主題
    try {
      await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
    }
  }
}


// 寫回 localStorage
function saveRoom() {
  try {
    // 檢查 room.value 和 roomCode.value 是否存在
    if (!room.value || !roomCode.value) {
      console.warn('房間資料或房間代碼不存在，跳過保存')
      return
    }
    
    const roomsData = localStorage.getItem('Sync_AI_rooms')
    const rooms = new Map(roomsData ? JSON.parse(roomsData) : [])
    room.value.questions = questions.value
    room.value.updatedAt = new Date().toISOString()
    room.value.settings = { ...settings }
    room.value.topics = topics.value  // 將主題保存到房間數據中
    rooms.set(roomCode.value, room.value)
    localStorage.setItem('Sync_AI_rooms', JSON.stringify(Array.from(rooms.entries())))
  } catch (e) {
    console.error('保存房間資料失敗:', e)
  }
}

// 意見操作
async function deleteQuestion(id) {
  if (!roomCode.value || !id) return
  if (!confirm('確定要刪除這個意見嗎？')) return

  try {
    // 使用新的 RESTful API
    const resp = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    })

    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`)
    }
    const data = await resp.json()
    if (data.success) {
      // 重新抓取列表以確保票數與內容同步
      await fetchQuestions()
      showNotification('已刪除意見', 'success')
    } else {
      showNotification(data.detail || '刪除失敗', 'error')
    }
  } catch (e) {
    console.error('刪除意見失敗:', e)
    showNotification('刪除失敗，請稍後再試', 'error')
  }
}

/*
 * 呼叫後端 API 以生成討論總結，並將結果顯示在指定的文字區塊中。
 */
async function summaryAI() {
  const summaryButton = document.getElementById('summary-btn');
  // 取得目前主題
  const currentTopic = topics.value[selectedTopicIndex.value]?.title
  
  // --- 1. 進入載入狀態 (提供使用者回饋) ---
  if (summaryButton) {
    summaryButton.disabled = true;
    summaryButton.textContent = 'AI 統整中...';
  }

  try {
    // --- 2. 呼叫後端的 summary API ---
    const response = await fetch(`${API_BASE_URL}/ai/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // 將參數轉換為 JSON 字串作為請求的 body
      body: JSON.stringify({
        room: roomCode.value,
        topic: currentTopic
      }),
    });

    // --- 3. 處理 API 回應 ---
    if (!response.ok) {
      // 如果伺服器回傳錯誤狀態 (例如 404, 500)
      throw new Error(`API 請求失敗，狀態碼：${response.status}`);
    }

    // 解析回傳的 JSON 資料
    const data = await response.json();

    // --- 4.將總結結果貼回留言區 ---
    if (data.summary) {
      // 使用新的 RESTful API
      await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          content: data.summary,
          nickname: "MBBuddy 小助手",
          isAISummary: true
        })
      });
      await fetchQuestions(); // 新增留言後刷新
    } else {
      throw new Error("API 回應中未包含 summary 欄位。");
    }

  } catch (error) {
    // --- 5. 處理所有可能發生的錯誤 ---
    console.error('生成 AI 總結時發生錯誤:', error);
    alert('無法生成討論總結，請檢查網路連線或稍後再試。');

  } finally {
    // --- 6. 無論成功或失敗，都恢復按鈕狀態 ---
    if (summaryButton) {
      summaryButton.disabled = false;
      summaryButton.textContent = 'AI統整';
    }
  }
}

async function clearAllQuestions() {
  if (confirm('確定要清空所有意見嗎？此操作無法復原。')) {
    // 獲取當前主題名稱
    const currentTopic = topics.value[selectedTopicIndex.value]?.title
    
    if (!currentTopic) {
      showNotification('未選擇主題，無法清空意見', 'error')
      return
    }
    
    try {
      // 修復：獲取當前主題的所有評論，然後逐一刪除
      const commentsResponse = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments`);
      if (!commentsResponse.ok) {
        throw new Error(`無法獲取評論列表: ${commentsResponse.status}`);
      }
      
      const commentsData = await commentsResponse.json();
      const commentsToDelete = commentsData.comments || [];
      
      if (commentsToDelete.length === 0) {
        showNotification('當前主題沒有評論需要清空', 'info');
        return;
      }
      
      // 逐一刪除評論
      let deletedCount = 0;
      let votesDeletedCount = 0;
      
      for (const comment of commentsToDelete) {
        try {
          const deleteResponse = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments/${comment.id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
          });
          
          if (deleteResponse.ok) {
            deletedCount++;
            // 每個評論的投票也會被一起刪除
            votesDeletedCount += (comment.vote_good || 0) + (comment.vote_bad || 0);
          }
        } catch (deleteError) {
          console.error('刪除單個評論失敗:', deleteError);
        }
      }
      
      // 清空本地意見列表
      questions.value = []
      if (room.value) {
        room.value.questions = []
        saveRoom()
      }
      
      // 顯示清空結果
      const message = `已清空主題「${currentTopic}」的所有內容：刪除了 ${deletedCount} 個評論和約 ${votesDeletedCount} 個投票記錄`;
      showNotification(message, 'success');
      
      // 重新獲取意見列表以確保同步
      await fetchQuestions();
      
    } catch (error) {
      console.error('清空意見失敗:', error)
      showNotification('清空意見失敗，請稍後再試', 'error')
    }
  }
}

// 清理臨時主題的手動功能
async function cleanTempTopics() {
  if (!roomCode.value) {
    showNotification('找不到討論室代碼', 'error')
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room: roomCode.value })
    })

    if (!response.ok) {
      throw new Error(`清理請求失敗: ${response.status}`)
    }

    const data = await response.json()
    
    if (data.success) {
      if (data.cleaned_topics.length > 0) {
        showNotification(`已清理 ${data.cleaned_topics.length} 個臨時主題`, 'success')
        console.log('清理的主題:', data.cleaned_topics)
        // 重新載入主題列表
        await loadRoom()
      } else {
        showNotification('沒有找到需要清理的臨時主題', 'info')
      }
    } else {
      showNotification(data.detail || '清理失敗', 'error')
    }
  } catch (error) {
    console.error('清理臨時主題失敗:', error)
    showNotification('清理臨時主題失敗，請稍後再試', 'error')
  }
}

function goToSummary() {
  router.push({
    path: '/meeting-summary',
    query: {
      room: roomCode.value,
      title: room.value?.title || '未命名討論'
    }
  })
}

// 討論控制
async function endRoom() {
  if (confirm('確定要結束討論嗎？這將關閉房間並跳轉到結算頁面。')) {
    try {
      // 停止計時器 (如果有運行的話)
      if (timerRunning.value) {
        await stopTimer()
      }
      
      // 更新API狀態為 End
      await setRoomStatus('End')
      
      // 更新本地房間狀態（如果存在）
      if (room.value) {
        room.value.isActive = false
        room.value.endedAt = new Date().toISOString()
        saveRoom()
      }
      
      // 🎯 背景風格追蹤 - 改為 async
      try {
        const meetingData = {
          participants: participantsList.value,
          questions: questions.value,
          roomCode: roomCode.value,
          title: room.value?.title
        }
        await BackgroundStyleTracker.trackMeeting(meetingData) // 加 await
      } catch (styleError) {
        console.warn('風格追蹤失敗，但討論正常結束:', styleError)
      }
      
      // 顯示結束通知
      showNotification('討論已結束，正在跳轉到結算頁面...', 'success')
      
      // 直接跳轉到結算頁面
      setTimeout(() => {
        router.push({
          path: '/meeting-summary',
          query: {
            room: roomCode.value,
            title: room.value?.title || '未命名討論'
          }
        })
      }, 1000)
      
    } catch (error) {
      console.error('結束討論失敗:', error)
      showNotification('結束討論失敗，請稍後再試', 'error')
    }
  }
}

// 通知
function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}
function removeNotification(i) {
  notifications.value.splice(i, 1)
}

// 共享剪貼簿
const copyRoomCode = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomCode.value)
      showNotification('代碼已複製', 'success')
    } else {
      // Fallback: 建立暫時 input 執行複製
      const tmpInput = document.createElement('input')
      tmpInput.value = roomCode.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('代碼已複製', 'success')
    }
  } catch (e) {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

const copyRoomLink = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomLink.value)
      showNotification('連結已複製', 'success')
    } else {
      // Fallback: 建立暫時 input 執行複製
      const tmpInput = document.createElement('input')
      tmpInput.value = roomLink.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('連結已複製', 'success')
    }
  } catch (e) {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

// 工具
function formatTime(dateString) {
  const date = new Date(dateString*1000)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '剛剛'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分鐘前`
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}
function escapeHtml(text) {
  // Vue 自動 escape，不過保留此函式相容
  const div = document.createElement('div')
  div.textContent = text
  // 處理換行符號，將 \n 轉換為 <br>
  return div.innerHTML.replace(/\n/g, '<br>')
}

// QR Code 彈窗控制
function showQRCode() {
  isQRCodeModalVisible.value = true
}

function hideQRCode() {
  isQRCodeModalVisible.value = false
}

// 監聽設定變化並同步到後端
watch(settings, async (newSettings) => {
  if (!roomCode.value) return;
  try {
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || '更新設定失敗');
    }
    showNotification('問答設定已更新', 'success');
  } catch (error) {
    console.error('更新問答設定失敗:', error);
    showNotification(error.message, 'error');
    // 可選擇性地將設定還原
  }
}, { deep: true });

// 監聽 allowJoin 狀態變化，自動呼叫 setRoomAllowJoin
watch(allowJoin, (val) => {
  setRoomAllowJoin(val)
})

// 房間資訊更新函數
function startEditRoomInfo() {
  // 初始化編輯表單
  editRoomTitle.value = room.value?.title || ''
  editRoomSummary.value = room.value?.topic_summary || ''
  isEditingRoomInfo.value = true
}

function cancelEditRoomInfo() {
  // 清空編輯表單並返回顯示模式
  editRoomTitle.value = ''
  editRoomSummary.value = ''
  isEditingRoomInfo.value = false
}

async function updateRoomInfo() {
  if (!editRoomTitle.value.trim()) {
    showNotification('房間名稱不能為空', 'error')
    return
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_update_info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        new_title: editRoomTitle.value.trim(),
        new_summary: editRoomSummary.value
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      // 更新本地的房間資料
      if (room.value) {
        room.value.title = data.new_title
        room.value.topic_summary = data.topic_summary || ''
      }
      
      // 退出編輯模式
      isEditingRoomInfo.value = false
      editRoomTitle.value = ''
      editRoomSummary.value = ''
      
      showNotification('房間資訊更新成功', 'success')
    } else {
      showNotification(data.error || '更新房間資訊失敗', 'error')
    }
  } catch (err) {
    console.error('更新房間資訊時發生錯誤:', err)
    showNotification('更新房間資訊時發生錯誤', 'error')
  }
}

function resetRoomInfoForm() {
  editRoomTitle.value = room.value?.title || ''
  editRoomSummary.value = room.value?.topic_summary || ''
}

// 側邊欄相關函數
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value.toString())
}

async function selectTopic(index) {
  selectedTopicIndex.value = index
  const currentTopic = topics.value[index].title
  try {
    const success = await switchTopic(currentTopic)
    if (success) {
      await fetchQuestions()
    }
  } catch (error) {
    console.error('切換主題時更新資料失敗:', error)
  }
}

function startEditTopic(index) {
  isAddingTopic.value = false;
  editingTopicIndex.value = index
  editingTopicName.value = topics.value[index].title
  originalTopicNameToEdit.value = topics.value[index].title
  editTopicTab.value = 'manual'
  nextTick(() => {
    document.querySelector('.topic-edit-input')?.focus();
  });
}

async function saveTopicEdit() {
  if (editingTopicIndex.value === null) return;

  const oldTopicName = originalTopicNameToEdit.value
  const newTopicName = editingTopicName.value.trim()
  
  if (!newTopicName || oldTopicName === newTopicName) {
    cancelTopicModal();
    return
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/topics/rename`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_topic: oldTopicName, new_topic: newTopicName })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      topics.value[editingTopicIndex.value].title = newTopicName
      if (result.is_current_topic) {
        await fetchQuestions()
      }
      showNotification(`主題已重新命名為「${newTopicName}」`, 'success')
    } else {
      showNotification(result.detail || '重新命名主題失敗', 'error')
    }
  } catch (error) {
    console.error('重新命名主題失敗:', error)
    showNotification(error.message || '重新命名主題失敗，請稍後再試', 'error')
  } finally {
    cancelTopicModal();
  }
}

function cancelTopicModal() {
  editingTopicIndex.value = null
  isAddingTopic.value = false;
  editingTopicName.value = ''
  customAiPrompt.value = ''
  originalTopicNameToEdit.value = ''
  editTopicTab.value = 'manual'
}

async function handleTopicModalConfirm(data) {
  if (data.isAddingTopic) {
    if (data.tab === 'manual') {
      await createNewTopicManual(data.topicName);
    } else {
      await createNewTopicWithAI(data.aiPrompt);
    }
  } else {
    if (data.tab === 'manual') {
      editingTopicName.value = data.topicName
      await saveTopicEdit();
    } else {
      customAiPrompt.value = data.aiPrompt
      await generateAndReplaceTopic();
    }
  }
}

async function generateAndReplaceTopic() {
  if (!customAiPrompt.value.trim()) {
    showNotification('請輸入 AI 發想的提示', 'warn')
    return
  }

  const topicIndex = editingTopicIndex.value
  const originalTopic = originalTopicNameToEdit.value
  const prompt = customAiPrompt.value

  cancelTopicModal()
  if (topicIndex !== null) {
    topics.value[topicIndex].title = 'AI 產生中...'
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ai/generate_single_topic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room: roomCode.value, custom_prompt: prompt }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`)
    }

    const result = await response.json()
    if (!result.topic) throw new Error('AI 未能生成主題')
    
    const newTopicName = result.topic

    const renameResponse = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/topics/rename`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_topic: originalTopic, new_topic: newTopicName }),
    })

    if (!renameResponse.ok) {
      const errorData = await renameResponse.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! Status: ${renameResponse.status}`)
    }

    const renameResult = await renameResponse.json()
    if (renameResult.success) {
      topics.value[topicIndex].title = newTopicName
      showNotification(`AI 已生成新主題：「${newTopicName}」`, 'success')
    } else {
      throw new Error(renameResult.detail || '重命名主題失敗')
    }

    // 清理臨時主題
    try {
      const cleanResp = await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
      if (cleanResp.ok) {
        const cleanData = await cleanResp.json()
        if (cleanData.success && cleanData.cleaned_topics.length > 0) {
          console.log(`已清理臨時主題: ${cleanData.cleaned_topics.join(', ')}`)
        }
      }
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
    }

  } catch (error) {
    console.error('AI 主題生成與替換失敗:', error)
    showNotification(error.message || 'AI 主題生成與替換失敗，請稍後再試', 'error')
    if (topicIndex !== null) {
      topics.value[topicIndex].title = originalTopic
    }
    
    // 即使生成失敗，也嘗試清理可能存在的臨時主題
    try {
      await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
    }
  }
}

function addNewTopic() {
  isAddingTopic.value = true;
  editingTopicIndex.value = null;
  editingTopicName.value = '';
  customAiPrompt.value = '';
  editTopicTab.value = 'manual';
  nextTick(() => {
    document.querySelector('.topic-edit-input')?.focus();
  });
}

async function createNewTopicManual(topicName) {
  const newTopicName = topicName.trim();
  if (!newTopicName) {
    showNotification('主題名稱不能為空', 'warn');
    return;
  }
  if (topics.value.some(t => t.title === newTopicName)) {
    showNotification('該主題名稱已存在', 'error');
    return;
  }

  topics.value.push({
    title: newTopicName,
    content: '',
    timestamp: new Date().toISOString()
  });

  try {
    const newIndex = topics.value.length - 1;
    await selectTopic(newIndex);
  } catch (error) {
    console.error("切換到新主題時出錯:", error);
  }
}

async function createNewTopicWithAI(aiPrompt) {
  if (!aiPrompt.trim()) {
    showNotification('請輸入 AI 發想的提示', 'warn');
    return;
  }
  const prompt = aiPrompt;

  const placeholderIndex = topics.value.length;
  topics.value.push({
    title: 'AI 產生中...',
    content: '',
    timestamp: new Date().toISOString(),
  });

  try {
    const response = await fetch(`${API_BASE_URL}/ai/generate_single_topic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room: roomCode.value, custom_prompt: prompt }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }
    const result = await response.json();
    if (!result.topic) throw new Error('AI 未能生成主題');
    
    const newTopicName = result.topic;
    topics.value[placeholderIndex].title = newTopicName;
    await selectTopic(placeholderIndex);
    showNotification(`AI 已生成新主題：「${newTopicName}」`, 'success');

    // 清理臨時主題
    try {
      const cleanResp = await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
      if (cleanResp.ok) {
        const cleanData = await cleanResp.json()
        if (cleanData.success && cleanData.cleaned_topics.length > 0) {
          console.log(`已清理臨時主題: ${cleanData.cleaned_topics.join(', ')}`)
        }
      }
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
    }

  } catch (error) {
    console.error('AI 新增主題失敗:', error);
    showNotification(error.message, 'error');
    topics.value.splice(placeholderIndex, 1);
    
    // 即使生成失敗，也嘗試清理可能存在的臨時主題
    try {
      await fetch(`${API_BASE_URL}/ai/clean_temp_topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room: roomCode.value })
      })
    } catch (cleanErr) {
      console.warn('清理臨時主題失敗:', cleanErr)
    }
  }
}

async function exportAllTopics() {
  if (!roomCode.value) {
    showNotification('找不到討論室代碼', 'error')
    return
  }

  const exportButton = document.querySelector('.btn-export-all')
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
      exportButton.innerHTML = '<i class="fas fa-file-export"></i> 匯出全部'
    }
  }
}

function loadTopics() {
  try {
    const savedTopics = localStorage.getItem(`topics_${roomCode.value}`)
    if (savedTopics) {
      topics.value = JSON.parse(savedTopics)
    }
    
    // 讀取側邊欄折疊狀態
    const savedCollapsed = localStorage.getItem('sidebarCollapsed')
    if (savedCollapsed !== null) {
      isSidebarCollapsed.value = savedCollapsed === 'true'
    }
  } catch (e) {
    console.error('讀取主題失敗:', e)
  }
}

function saveTopics() {
  try {
    localStorage.setItem(`topics_${roomCode.value}`, JSON.stringify(topics.value))
  } catch (e) {
    console.error('儲存主題失敗:', e)
  }
}

// 監聽主題變化
watch(topics, saveTopics, { deep: true })

// 輪詢
// 計時器函數
function showTimerSettings() {
  // 載入保存的設置（如果有）
  const savedSettings = localStorage.getItem(`timer_settings_${roomCode.value}`)
  if (savedSettings) {
    Object.assign(timerSettings, JSON.parse(savedSettings))
  }
  isTimerSettingsVisible.value = true
}

function hideTimerSettings() {
  isTimerSettingsVisible.value = false
}

async function applyTimerSettings(newSettings) {
  // 更新設定
  Object.assign(timerSettings, newSettings)
  
  // 計算總秒數
  const totalSeconds = 
    (timerSettings.hours * 3600) + 
    (timerSettings.minutes * 60) + 
    timerSettings.seconds
  
  // 保存設置
  localStorage.setItem(`timer_settings_${roomCode.value}`, JSON.stringify(timerSettings))
  
  // 設置計時器
  remainingTime.value = totalSeconds
  initialTime.value = totalSeconds
  
  // 如果時間已設置，與API同步並自動開始計時
  if (totalSeconds > 0) {
    setRoomState()
    startTimer() // 自動開始計時
  }
}

async function startTimer() {
  if (remainingTime.value <= 0) return
  
  timerRunning.value = true
  
  // 清除可能存在的舊計時器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  
  // 更新房間狀態為討論中
  await setRoomStatus('Discussion')
  
  // 記錄計時器開始時間
  const startTime = Date.now()
  const initialSeconds = remainingTime.value
  
  // 設置新計時器，使用基於時間差的方式計算，而不是簡單地減1
  timerInterval.value = setInterval(async () => {
    const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000)
    const newRemaining = initialSeconds - elapsedSeconds

    if (newRemaining > 0) {
      remainingTime.value = newRemaining
    } else {
      remainingTime.value = 0
      // 記錄時間到之前的狀態
      const currentStatus = roomStatus.value
      stopTimer()
      if (autoChangeStatus.value) {
        // 根據時間到之前的狀態進行切換
        if (currentStatus === 'Discussion') {
          await setRoomStatus('Stop')
        } else if (currentStatus === 'Stop') {
          await setRoomStatus('Discussion')
        }
        showNotification('計時器時間到！已自動切換狀態', 'info')
      } else {
        showNotification('時間到（未切換狀態）', 'info')
      }
    }
  }, 500) // 更頻繁檢查但只在必要時更新視圖
}

async function stopTimer() {
  timerRunning.value = false
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  
  // 更新房間狀態為暫停
  try {
    await setRoomStatus('Stop')
  } catch (error) {
    console.error('停止計時器時更新狀態失敗:', error)
  }
}

async function toggleTimer() {
  if (remainingTime.value <= 0) {
    // 如果沒有設置時間，開啟設置面板
    showTimerSettings()
    return
  }
  
  if (timerRunning.value) {
    await stopTimer()
    // stopTimer 已經會設置房間狀態為休息中
  } else {
    await startTimer()
    // startTimer 已經會設置房間狀態為討論中
    // 同步當前主題和計時狀態到參與者面板
    await setRoomState()
  }
}

async function terminateTimer() {
  // 停止計時器 (內部已經會設置狀態為 Stop)
  await stopTimer()
  // 將剩餘時間設為0（時間到）
  remainingTime.value = 0
  // 顯示時間到的通知
  showNotification('計時已終止！', 'info')
}

// 格式化剩餘時間為 HH:MM:SS 格式
const formattedRemainingTime = computed(() => {
  if (remainingTime.value <= 0) return '00:00:00'
  
  const hours = Math.floor(remainingTime.value / 3600)
  const minutes = Math.floor((remainingTime.value % 3600) / 60)
  const seconds = remainingTime.value % 60
  
  return [hours, minutes, seconds]
    .map(v => v.toString().padStart(2, '0'))
    .join(':')
})

// 從本地存儲中載入計時器設置
function loadTimerSettings() {
  try {
    // 檢查是否為新建的房間
    const urlParams = new URLSearchParams(window.location.search)
    const isNewRoom = urlParams.get('new') === 'true'
    
    if (isNewRoom && room.value && room.value.countdown > 0) {
      // 新房間：使用後端提供的倒數時間
      const backendCountdown = room.value.countdown
      
      timerSettings.hours = Math.floor(backendCountdown / 3600)
      timerSettings.minutes = Math.floor((backendCountdown % 3600) / 60)
      timerSettings.seconds = backendCountdown % 60
      
      initialTime.value = backendCountdown
      remainingTime.value = backendCountdown
      seededFromBackend.value = true // 標記為從後端初始化
      
      // 保存到 localStorage 以便後續使用
      localStorage.setItem(`timer_settings_${roomCode.value}`, JSON.stringify(timerSettings))
      
      console.log(`新房間自動設定計時器: ${timerSettings.hours}:${timerSettings.minutes}:${timerSettings.seconds}`)
      return
    }
    
    // 現有房間：載入本地設置
    const savedSettings = localStorage.getItem(`timer_settings_${roomCode.value}`)
    if (savedSettings) {
      Object.assign(timerSettings, JSON.parse(savedSettings))
      
      // 計算總秒數
      initialTime.value = 
        (timerSettings.hours * 3600) + 
        (timerSettings.minutes * 60) + 
        timerSettings.seconds
      
      remainingTime.value = initialTime.value
    } else {
      // 預設值為 5 分鐘
      timerSettings.hours = 0
      timerSettings.minutes = 5
      timerSettings.seconds = 0
      
      initialTime.value = 300 // 5 分鐘
      remainingTime.value = 300
    }
    
    // 載入運行狀態
    const savedRunning = localStorage.getItem(`timer_running_${roomCode.value}`)
    if (savedRunning === 'true') {
      // 如果之前是在運行中，自動啟動
      const savedRemainingTime = localStorage.getItem(`timer_remaining_${roomCode.value}`)
      if (savedRemainingTime) {
        remainingTime.value = parseInt(savedRemainingTime, 10) || initialTime.value
        if (remainingTime.value > 0) {
          startTimer()
        }
      }
    }
  } catch (e) {
    console.error('載入計時器設置失敗:', e)
  }
}

// 保存計時器狀態
function saveTimerState() {
  try {
    localStorage.setItem(`timer_running_${roomCode.value}`, timerRunning.value)
    localStorage.setItem(`timer_remaining_${roomCode.value}`, remainingTime.value)
  } catch (e) {
    console.error('保存計時器狀態失敗:', e)
  }
}

// 監聽計時器狀態變化
watch([timerRunning, remainingTime], saveTimerState)

// 房間狀態相關API函數
async function fetchRoomStatus() {
  try {
    // 如果計時器正在運行，不需要頻繁查詢房間狀態
    if (timerRunning.value && roomStatus.value === 'Discussion') {
      return roomStatus.value
    }
    
    const response = await fetch(`${API_BASE_URL}/api/room_status?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    const data = await response.json()
    const status = data.status
    // 只在狀態變化時更新
    if (roomStatus.value !== status) {
      roomStatus.value = status
      console.log(`房間狀態已更新：${status}`) // 便於調試
    }
    
    return status
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
    roomStatus.value = 'NotFound'
    return 'NotFound'
  }
}

async function setRoomStatus(status) {
  try {
    // 如果狀態沒有變化，不做任何事情
    if (roomStatus.value === status) {
      return
    }
    
    const response = await fetch(`${API_BASE_URL}/api/room_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        status: status
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    roomStatus.value = status
    showNotification(`房間狀態已更新為：${roomStatusText.value}`, 'success')
  } catch (error) {
    console.error('設置房間狀態失敗:', error)
    showNotification('設置房間狀態失敗', 'error')
  }
}

// 新增的切換主題API函數
async function switchTopic(topicName) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/topic`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: topicName
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    if (data.success) {
      showNotification(`已切換到主題：${topicName}`, 'success')
      // 更新房間狀態
      roomStatus.value = data.status
      return true
    } else {
      throw new Error(data.detail || '切換主題失敗')
    }
  } catch (error) {
    console.error('切換主題失敗:', error)
    showNotification(error.message || '切換主題失敗', 'error')
    return false
  }
}

// 主題和計時相關的API函數
async function setRoomState() {
  if (!topics.value[selectedTopicIndex.value]) {
    return
  }
  
  const currentTopic = topics.value[selectedTopicIndex.value].title
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_state`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        topic: currentTopic,
        countdown: initialTime.value,
        time_start: Date.now() / 1000
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    showNotification('主題和計時器已同步到參與者面板', 'success')
  } catch (error) {
    console.error('設置房間狀態失敗:', error)
    showNotification('設置房間狀態失敗', 'error')
  }
}

let roomPoller
let dataPoller
let participantsPoller
onMounted(async () => {
  await loadRoom()  // 等待房間載入完成
  loadTopics()
  loadTimerSettings() // 載入計時器設置（新房間會從後端載入倒數時間）
  
  // 檢查是否為新房間且需要自動開始計時
  const urlParams = new URLSearchParams(window.location.search)
  const isNewRoom = urlParams.get('new') === 'true'
  
  try {
    const savedRunning = localStorage.getItem(`timer_running_${roomCode.value}`)
    
    // 新房間自動開始計時邏輯
    if (isNewRoom && seededFromBackend.value && remainingTime.value > 0 && !timerRunning.value) {
      console.log('新房間自動開始計時')
      await setRoomState() // 會同時將狀態設為 Discussion
      await startTimer()
    }
    // 現有房間恢復計時邏輯
    else if (!isNewRoom && savedRunning === 'true' && remainingTime.value > 0 && !timerRunning.value) {
      console.log('恢復現有房間的計時狀態')
      await setRoomState() // 會同時將狀態設為 Discussion
      await startTimer()
    }
  } catch (e) { 
    console.error('自動啟動計時器失敗:', e)
  }
    
  // 窗口監聽器已移至子組件中
  
  // 首次檢查房間狀態，如果房間不存在則返回主頁
  const initialStatus = await fetchRoomStatus()
  if (initialStatus === 'NotFound') {
    showNotification('房間不存在，即將返回主頁', 'error')
    setTimeout(() => {
      router.push('/')
    }, 2000)
    return
  }
  
  // 延遲啟動意見輪詢，確保 loadRoom() 先完成
  setTimeout(() => {
    fetchQuestions() // 首次獲取
    dataPoller = setInterval(fetchQuestions, 5000)
  }, 100)

  fetchParticipants()
  participantsPoller = setInterval(fetchParticipants, 5000)
})

onBeforeUnmount(() => {
  // 組件卸載時清理
  clearInterval(dataPoller)
  clearInterval(roomPoller)
  clearInterval(participantsPoller)
  
  // 停止計時器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  
  // 清理進度更新計時器
  if (progressUpdateTimer) {
    clearTimeout(progressUpdateTimer)
  }
})

// --- 以下為原有函數，請根據需要保留或修改 ---
</script>

<style scoped>
@import url('../assets/styles.css');

/* 主要佈局結構 */
.host-content {
    max-width: 1500px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
    min-height: calc(100vh - 140px); /* 確保最小高度 */
}

.host-layout {
  display: grid;
  grid-template-columns: auto 1fr 350px;
  gap: 1.5rem;
  min-height: calc(100vh - 70px - 6rem - 1px); /* 改為最小高度而不是固定高度 */
  height: auto; /* 允許內容撐開高度 */
}

/* 導覽列樣式 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.room-info {
  display: flex;
  gap: 1rem;
  font-size: 0.92rem;
  align-items: center;
}

.room-code, .participant-count {
  color: var(--text-secondary);
}

.room-code strong, .participant-count strong {
  color: var(--primary-color);
}

/* 房間狀態樣式 */
.room-status {
  margin-left: 1rem;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.9rem;
  background-color: #f0f0f0;
  cursor: pointer;
}

.status-notfound {
  background-color: #e5e5e5;
  color: #666666;
}

.status-stop {
  background-color: #fef3c7;
  color: #b45309;
}

.status-discussion {
  background-color: #dcfce7;
  color: #166534;
}

.status-end {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
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

.btn-outline {
  background: transparent;
  border-color: var(--border);
  color: var(--text-secondary);
}

.btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
}

/* 意見列表區域 - 重要修正 */
.questions-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 500px; /* 設定最小高度 */
  max-height: calc(100vh - 110px - 24px*2); /* 設定最大高度 */
  height: auto; /* 允許內容撐開 */
  overflow: visible; /* 確保內容不被切掉 */
}

/* 響應式調整 */
@media (max-width: 1024px) {
  .host-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    height: auto; /* 確保自適應高度 */
    min-height: auto; /* 移除最小高度限制 */
  }
  
  .questions-section {
    min-height: 400px; /* 在小螢幕上調整最小高度 */
  }
}

@media (max-width: 768px) {
  .room-info {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .nav-actions {
    flex-direction: column;
    gap: 0.5rem;
  }

  .progress-header {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .questions-section {
    min-height: 300px; /* 手機上進一步調整 */
  }
}
</style>