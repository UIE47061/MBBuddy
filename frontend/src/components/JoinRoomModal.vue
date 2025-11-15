<template>
  <div class="modal" :class="{ active: visible }" @click.self="close">
    <div class="modal-content modal-large">
      <div class="modal-header">
        <h3>加入討論室</h3>
        <button class="modal-close" @click="close">&times;</button>
      </div>
      <div class="room-list-container">
        <div class="filter-section">
          <label>篩選討論室狀態：</label>
          <div class="filter-buttons">
            <button v-for="filter in filters" :key="filter.value" type="button"
              :class="['filter-btn', { active: selectedFilter === filter.value }]" @click="selectedFilter = filter.value">
              {{ filter.text }}
            </button>
          </div>
        </div>
        <div class="room-list">
          <div class="room-list-header">
            <span>討論室標題</span>
            <span>狀態</span>
            <span>參與人數</span>
            <span>建立時間</span>
          </div>
          <div v-for="room in filteredRooms" :key="room.code" class="room-item-container">
            <div class="room-item" :class="{ 'selected': selectedRoom?.code === room.code }" @click="selectRoom(room)">
              <span class="room-title">{{ room.title }}</span>
              <span :class="['room-status', `status-${room.status}`]">{{ getStatusText(room.status) }}</span>
              <span class="room-participants">{{ room.participants }}</span>
              <span class="room-time">{{ formatTime(room.created_at) }}</span>
            </div>
            <div v-if="selectedRoom?.code === room.code" class="room-join-form">
              <div class="join-form-content">
                <h4><i class="fas fa-sign-in-alt"></i> 加入討論室：{{ selectedRoom.title }}</h4>
                <form @submit.prevent="joinSelectedRoom" class="inline-join-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label for="roomCode">請輸入討論室代碼確認加入</label>
                      <input type="text" id="roomCode" v-model="joinCode" required placeholder="輸入 6 位數代碼"
                        maxlength="6" class="join-input" />
                    </div>
                    <div class="form-actions">
                      <button type="button" class="btn btn-outline btn-sm" @click="selectedRoom = null">
                        <i class="fas fa-times"></i> 取消
                      </button>
                      <button type="submit" class="btn btn-primary btn-sm">
                        <i class="fas fa-sign-in-alt"></i> 確認加入
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
          <div v-if="filteredRooms.length === 0" class="no-rooms">
            沒有找到符合條件的討論室
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  visible: Boolean
});

const emit = defineEmits(['close', 'show-notification', 'join-success']);
const router = useRouter();

// --- API 位址 ---
import { API_BASE_URL } from '@/utils/api';
const API_BASE = API_BASE_URL;

const rooms = ref([]);
const selectedFilter = ref('all');
const selectedRoom = ref(null);
const joinCode = ref('');

const filters = [
  { text: '全部', value: 'all' },
  { text: '休息中', value: 'Stop' },
  { text: '討論中', value: 'Discussion' },
  { text: '已結束', value: 'End' },
];

const filteredRooms = computed(() => {
  if (selectedFilter.value === 'all') return rooms.value;
  return rooms.value.filter(room => room.status === selectedFilter.value);
});

watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadRooms();
  } else {
    // 關閉時重置狀態
    selectedRoom.value = null;
    joinCode.value = '';
  }
});

function close() {
  emit('close');
}

async function loadRooms() {
  try {
    const resp = await fetch(`${API_BASE}/api/rooms`);
    if (!resp.ok) throw new Error('無法載入討論室列表');
    rooms.value = (await resp.json()).rooms || [];
  } catch (err) {
    emit('show-notification', { text: '載入討論室列表失敗', type: 'error' });
  }
}

function selectRoom(room) {
  if (selectedRoom.value?.code === room.code) {
    selectedRoom.value = null;
    joinCode.value = '';
  } else {
    selectedRoom.value = room;
    joinCode.value = '';
    setTimeout(() => document.getElementById('roomCode')?.focus(), 100);
  }
}

async function joinSelectedRoom() {
  const code = joinCode.value.trim().toUpperCase();
  if (code !== selectedRoom.value.code) {
    emit('show-notification', { text: '輸入的代碼與選擇的討論室不符', type: 'error' });
    return;
  }
  if (!code || code.length !== 6) {
    emit('show-notification', { text: '請輸入有效的 6 位數討論室代碼', type: 'error' });
    return;
  }
  try {
    const resp = await fetch(`${API_BASE}/api/room_status?room=${code}`);
    const data = await resp.json();
    if (data.status === "NotFound") {
      emit('show-notification', { text: '找不到該討論室', type: 'error' });
      return;
    }
    if (data.status === "End") {
      emit('show-notification', { text: '該討論室已結束', type: 'error' });
      return;
    }
    emit('join-success', code);
    close();
  } catch (e) {
    emit('show-notification', { text: '加入討論室失敗', type: 'error' });
  }
}

function formatTime(timeString) {
  const date = new Date(timeString * 1000);
  return date.toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function getStatusText(status) {
  const statusMap = { 'Stop': '休息中', 'Discussion': '討論中', 'End': '已結束' };
  return statusMap[status] || status;
}
</script>

<style scoped>
/* 從 Home.vue 複製過來的 Modal 和 Room List 相關樣式 */
@import url('../assets/styles.css');
/* ... 將 Home.vue 中所有與 .modal-large, .room-list-container, .filter-section, .room-list, .room-item 等相關的樣式複製到這裡 ... */
/* 為了簡潔，此處省略，但您需要將原檔案中的對應 CSS 規則貼過來 */
.modal-content.modal-large { max-width: 900px !important; max-height: 85vh; overflow-y: auto; border-radius: 16px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15); border: none; }
.room-list-container { margin: 0 20px 20px 20px; padding: 0 10px; }
.filter-section { margin-bottom: 25px; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; }
.filter-section label { display: block; margin-bottom: 15px; font-weight: 600; color: #495057; text-align: center; font-size: 16px; }
.filter-buttons { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
.filter-btn { padding: 12px 20px; border: 2px solid #dee2e6; background: white; color: #6c757d; border-radius: 25px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.filter-btn:hover { border-color: #007bff; color: #007bff; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,123,255,0.2); }
.filter-btn.active { background: linear-gradient(135deg, #007bff, #0056b3); border-color: #007bff; color: white; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,123,255,0.3); }
.room-list { border: 1px solid #dee2e6; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07); background: white; margin: 0 10px; }
.room-item-container { border-bottom: 1px solid #f1f3f4; }
.room-item-container:last-child { border-bottom: none; }
.room-list-header { display: grid; grid-template-columns: 2.5fr 1.5fr 1fr 1.5fr; gap: 20px; padding: 20px 25px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); font-weight: 700; color: #495057; border-bottom: 2px solid #dee2e6; text-align: center; }
.room-list-header span:first-child { text-align: left; }
.room-item { display: grid; grid-template-columns: 2.5fr 1.5fr 1fr 1.5fr; gap: 20px; padding: 20px 25px; cursor: pointer; transition: all 0.3s ease; align-items: center; }
.room-item:hover { background: linear-gradient(135deg, #f8f9fa, #ffffff); transform: translateX(5px); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
.room-item.selected { background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-left: 4px solid #2196f3; }
.room-join-form { background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-top: 1px solid #dee2e6; animation: slideDown 0.3s ease; }
@keyframes slideDown { from { max-height: 0; opacity: 0; } to { max-height: 200px; opacity: 1; } }
.join-form-content { padding: 20px 25px; }
.join-form-content h4 { margin-bottom: 15px; color: #495057; font-weight: 600; font-size: 16px; display: flex; align-items: center; gap: 8px; }
.join-form-content h4 i { color: #2196f3; }
.inline-join-form { margin: 0; }
.form-row { display: flex; align-items: end; gap: 15px; }
.form-row .form-group { flex: 1; margin-bottom: 0; }
.form-row .form-group label { font-size: 14px; margin-bottom: 8px; color: #6c757d; }
.join-input { width: 100%; padding: 10px 12px; border: 2px solid #dee2e6; border-radius: 8px; font-size: 14px; transition: all 0.2s; background: white; }
.join-input:focus { outline: none; border-color: #2196f3; box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1); }
.form-row .form-actions { display: flex; gap: 8px; margin-bottom: 0; }
.btn-sm { padding: 8px 16px; font-size: 13px; display: flex; align-items: center; gap: 6px; }
.btn-sm i { font-size: 12px; }
.room-title { font-weight: 600; color: #212529; text-align: left; font-size: 16px; }
.room-status { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; min-width: 80px; margin: 0 auto; }
.status-Stop { background: linear-gradient(135deg, #fff3cd, #ffeaa7); color: #856404; border: 1px solid #ffeaa7; }
.status-Discussion { background: linear-gradient(135deg, #d1ecf1, #74b9ff); color: #0c5460; border: 1px solid #74b9ff; }
.status-End { background: linear-gradient(135deg, #f8d7da, #fd79a8); color: #721c24; border: 1px solid #fd79a8; }
.room-time { color: #6c757d; font-size: 14px; text-align: center; font-weight: 500; }
.room-participants { color: #6c757d; font-size: 14px; text-align: center; font-weight: 600; }
.no-rooms { padding: 60px 40px; text-align: center; color: #6c757d; font-style: italic; font-size: 16px; background: linear-gradient(135deg, #f8f9fa, #ffffff); }
/* ... 響應式樣式 ... */
@media (max-width: 768px) { .modal-content.modal-large { max-width: 95% !important; margin: 20px auto; max-height: 90vh; } .room-list-container { margin: 0 10px 15px 10px; padding: 0; } .room-list { margin: 0; border-radius: 8px; } .room-list-header { display: none; } .room-item { display: block; padding: 20px; border-bottom: 1px solid #f1f3f4; text-align: left; } .room-item:hover { transform: none; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); } .room-item.selected { border-left: 4px solid #2196f3; background: linear-gradient(135deg, #f0f7ff, #e3f2fd); } .room-title { display: block; font-size: 16px; font-weight: 600; color: #212529; margin-bottom: 12px; text-align: left !important; } .room-title::before { content: "📋 "; color: #007bff; } .room-status { display: inline-block; margin-bottom: 8px; margin-right: 15px; padding: 6px 12px; font-size: 11px; min-width: auto; } .room-time { display: block; color: #6c757d; font-size: 13px; text-align: left; } .room-time::before { content: "🕒 建立時間："; color: #ffc107; font-weight: 500; } .room-participants { display: inline-block; color: #495057; font-size: 13px; text-align: left; margin-right: 15px; } .room-participants::before { content: "👥 參與人數："; color: #28a745; font-weight: 600; } .filter-section { margin-bottom: 20px; padding: 15px; } .filter-section label { font-size: 15px; margin-bottom: 12px; } .filter-buttons { justify-content: center; gap: 8px; flex-wrap: wrap; } .filter-btn { padding: 8px 14px; font-size: 12px; min-width: 70px; } .room-join-form { background: linear-gradient(135deg, #f8f9fa, #e9ecef); margin: 15px 0 -20px 0; border-radius: 0 0 8px 8px; } .join-form-content { padding: 20px 15px; } .join-form-content h4 { font-size: 15px; margin-bottom: 15px; text-align: center; } .form-row { flex-direction: column; gap: 15px; align-items: stretch; } .form-row .form-group label { font-size: 13px; text-align: center; display: block; margin-bottom: 8px; } .join-input { padding: 12px 15px; font-size: 16px; text-align: center; letter-spacing: 2px; border-radius: 8px; width: 100%; box-sizing: border-box; } .form-row .form-actions { justify-content: center; gap: 12px; } .btn-sm { padding: 10px 20px; font-size: 14px; border-radius: 6px; width: 100%; justify-content: center; } .no-rooms { padding: 40px 20px; font-size: 15px; line-height: 1.5; } }
@media (max-width: 480px) { .modal-content.modal-large { max-width: 98% !important; margin: 10px auto; max-height: 95vh; } .room-list-container { margin: 0 5px 10px 5px; } .filter-section { padding: 12px; } .filter-buttons { gap: 6px; } .filter-btn { padding: 6px 10px; font-size: 11px; min-width: 60px; } .room-item { padding: 15px; } .room-title { font-size: 15px; margin-bottom: 10px; } .room-join-form { margin: 15px 0 -15px 0; } .join-form-content { padding: 15px 10px; } .form-row .form-actions { flex-direction: column; gap: 8px; } .nav-actions { flex-direction: column; gap: 8px; } .nav-actions .btn { font-size: 12px; padding: 8px 12px; } }
</style>