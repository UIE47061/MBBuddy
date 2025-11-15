import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { API_BASE_URL } from '@/utils/api';

export function useRoom() {
  const route = useRoute();
  const router = useRouter();

  // --- State ---
  const roomCode = ref(route.query.room || '');
  const questions = ref([]);
  const notifications = ref([]);
  const roomStatus = ref('NotFound');
  const currentTopic = ref('');
  const remainingTime = ref(0);
  const votedQuestions = ref({ good: new Set(), bad: new Set() });
  const currentNickname = ref('');
  const deviceId = ref('');

  // --- Private Vars ---
  let statePoller, localTimerPoller, heartbeatPoller;
  const getRoomNicknameKey = () => `nickname_${roomCode.value}`;

  // --- Computed ---
  const roomStatusText = computed(() => ({ 'NotFound': '未啟動', 'Stop': '休息中', 'Discussion': '討論中', 'End': '已結束' }[roomStatus.value] || '未知'));
  const formattedRemainingTime = computed(() => {
    if (remainingTime.value <= 0) return '00:00:00';
    const h = Math.floor(remainingTime.value / 3600).toString().padStart(2, '0');
    const m = Math.floor((remainingTime.value % 3600) / 60).toString().padStart(2, '0');
    const s = (remainingTime.value % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  });
  const statusIcon = computed(() => ({ 'Discussion': 'fa-solid fa-comments', 'Stop': 'fa-solid fa-pause', 'End': 'fa-solid fa-flag-checkered', 'NotFound': 'fa-solid fa-circle-exclamation' }[roomStatus.value] || 'fa-solid fa-question'));

  // --- Methods ---
  const showNotification = (text, type = 'info') => {
    const id = Date.now() + Math.random();
    notifications.value.push({ id, text, type });
    setTimeout(() => removeNotification(id), 3000);
  };

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) notifications.value.splice(index, 1);
  };

  const clearAllPolling = () => {
    clearInterval(statePoller);
    clearInterval(localTimerPoller);
    clearInterval(heartbeatPoller);
  };

  const goHome = () => {
    clearAllPolling();
    router.push('/');
  };

  const fetchRoomState = async () => {
    if (!roomCode.value) return 'NotFound';
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/state`);
      if (response.status === 404) throw new Error('NotFound');
      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
      const data = await response.json();
      roomStatus.value = data.status;
      currentTopic.value = data.topic || '等待主持人設定主題';
      questions.value = data.comments || [];
      remainingTime.value = (data.status === 'End' || data.status === 'Stop') ? 0 : (data.countdown || 0);
      return data.status;
    } catch (error) {
      roomStatus.value = 'NotFound';
      clearAllPolling();
      showNotification('討論不存在或已結束', 'error');
      setTimeout(goHome, 3000);
      return 'NotFound';
    }
  };

  const submitQuestion = async (content) => {
    if (!content.trim() || !roomCode.value) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, nickname: currentNickname.value, isAISummary: false })
      });
      if (!response.ok) throw new Error('提交失敗');
      await fetchRoomState();
      showNotification('意見已提交', 'success');
    } catch (error) {
      showNotification(error.message, 'error');
    }
  };

  const voteQuestion = async (questionId, voteType) => {
    const isVoted = votedQuestions.value[voteType].has(questionId);
    const method = isVoted ? 'DELETE' : 'POST';
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/comments/${questionId}/vote`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: deviceId.value, vote_type: voteType })
      });
      if (!response.ok) throw new Error('投票失敗');
      await fetchUserVotes();
      await fetchRoomState();
      showNotification('投票操作成功', 'success');
    } catch (error) {
      showNotification(error.message, 'error');
    }
  };

  const fetchUserVotes = async () => {
    if (!deviceId.value || !roomCode.value) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/votes?device_id=${deviceId.value}`);
      if (!response.ok) return;
      const data = await response.json();
      votedQuestions.value.good = new Set(data.voted_good || []);
      votedQuestions.value.bad = new Set(data.voted_bad || []);
    } catch (error) {
      console.error('獲取投票記錄失敗:', error);
    }
  };

  const sendHeartbeat = async () => {
    if (!roomCode.value || !deviceId.value) return;
    try {
      await fetch(`${API_BASE_URL}/api/participants/heartbeat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room: roomCode.value, device_id: deviceId.value })
      });
    } catch (error) {
      console.error('心跳發送錯誤:', error);
    }
  };

  const registerHeartbeat = async () => {
    if (!currentNickname.value || !roomCode.value || !deviceId.value) return;
    try {
      await fetch(`${API_BASE_URL}/api/participants/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room: roomCode.value, device_id: deviceId.value, nickname: currentNickname.value })
      });
      clearInterval(heartbeatPoller);
      heartbeatPoller = setInterval(sendHeartbeat, 5000); // 5秒一次心跳
    } catch (error) {
      console.error('加入房間或註冊心跳時出錯:', error);
    }
  };

  const initializeUser = () => {
    let savedDeviceId = localStorage.getItem('device_id');
    if (!savedDeviceId) {
      savedDeviceId = `device_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      localStorage.setItem('device_id', savedDeviceId);
    }
    deviceId.value = savedDeviceId;

    const savedNickname = localStorage.getItem(getRoomNicknameKey());
    if (savedNickname) {
      currentNickname.value = savedNickname;
      return true;
    }
    return false;
  };

  const updateUserNickname = async (newNickname, isInitialSetup = false) => {
    const oldNickname = currentNickname.value;
    if (!newNickname.trim()) return;

    // --- 修正後的邏輯 ---
    if (isInitialSetup) {
      // 情況 1：初次設定暱稱
      // 只更新前端的狀態，後續由 registerHeartbeat 負責與後端同步
      currentNickname.value = newNickname;
      localStorage.setItem(getRoomNicknameKey(), newNickname);
      showNotification(`暱稱設定為「${newNickname}」`, 'success');
      // 不發送 PUT 請求，直接返回
      return; 
    }

    // 情況 2：後續修改暱稱 (舊邏輯)
    if (newNickname === oldNickname) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomCode.value}/participants/${deviceId.value}/nickname`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_nickname: newNickname, old_nickname: oldNickname })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `伺服器錯誤: ${response.status}` }));
        throw new Error(errorData.detail || '更新暱稱失敗');
      }
      
      localStorage.setItem(getRoomNicknameKey(), newNickname);
      currentNickname.value = newNickname;
      showNotification(`暱稱已更新為「${newNickname}」`, 'success');
      await fetchRoomState();
    } catch (error) {
      showNotification(error.message, 'error');
    }
  };

  const startPolling = () => {
    statePoller = setInterval(fetchRoomState, 3000);
    localTimerPoller = setInterval(() => {
      if (remainingTime.value > 0 && roomStatus.value === 'Discussion') {
        remainingTime.value--;
      }
    }, 1000);
  };

  onMounted(async () => {
    if (!roomCode.value) {
      goHome();
      return;
    }
    await fetchRoomState();
    startPolling();
  });

  onBeforeUnmount(clearAllPolling);

  return {
    roomCode, questions, notifications, roomStatus, currentTopic, remainingTime,
    votedQuestions, currentNickname, roomStatusText, formattedRemainingTime, statusIcon,
    showNotification, removeNotification, submitQuestion, voteQuestion, initializeUser,
    updateUserNickname, goHome, fetchRoomState, fetchUserVotes, registerHeartbeat
  };
}