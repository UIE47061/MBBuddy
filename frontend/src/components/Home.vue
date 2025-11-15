<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand" @click="router.push('/')" aria-label="返回主頁">
          <img src="/icon.png" alt="MBBuddy" class="brand-icon" />
          <!-- <h1>MBBuddy</h1> -->
          <!-- <span>互動問答平台</span> -->
        </div>
        <div class="nav-actions">
          <button class="btn btn-outline" @click="showJoinModal = true">加入討論</button>
          <button class="btn btn-primary" @click="showCreateModal = true">建立討論室</button>
        </div>
      </div>
    </nav>

    <!-- 主內容 -->
    <main class="main-content">
      <section class="hero">
        <div class="hero-content">
          <h2>讓每個聲音都被聽見</h2>
          <p>建立互動討論室，讓參與者匿名提問、投票，讓討論更有參與感</p>
          <div class="hero-actions">
            <button class="btn btn-primary btn-large" @click="showCreateModal = true">
              <span>➕</span>
              建立新討論室
            </button>
          </div>
        </div>
      </section>
      <section class="features">
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">❓</div>
            <h3>匿名提問</h3>
            <p>參與者可以匿名提出問題，消除發言障礙</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">👍</div>
            <h3>即時投票</h3>
            <p>對問題進行投票，熱門問題自動排序</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>AI即時統整</h3>
            <p>本地AI及時統整大家意見並給出建議</p>
          </div>
        </div>
      </section>
    </main>

    <!-- 建立討論室 Modal -->
    <CreateRoomModal 
      :visible="showCreateModal" 
      @close="showCreateModal = false"
      @create-success="handleCreateSuccess"
      @show-notification="handleShowNotification"
    />

    <!-- 加入討論室 Modal -->
    <JoinRoomModal
      :visible="showJoinModal"
      @close="showJoinModal = false"
      @join-success="handleJoinSuccess"
      @show-notification="handleShowNotification"
    />

    <!-- 通知訊息 -->
    <TransitionGroup name="fade">
      <div
        v-for="(msg, i) in notifications"
        :key="i"
        :class="['notification', `notification-${msg.type}`]"
        style="position: fixed; top: 20px; right: 20px; z-index: 2000; margin-bottom: 12px;"
      >
        <span>{{ msg.text }}</span>
        <button @click="removeNotification(i)">&times;</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import CreateRoomModal from './CreateRoomModal.vue';
import JoinRoomModal from './JoinRoomModal.vue';

const router = useRouter();

// --- Modal 狀態 ---
const showCreateModal = ref(false);
const showJoinModal = ref(false);

// --- 通知 ---
const notifications = ref([]);

function handleShowNotification({ text, type }) {
  showNotification(text, type);
}

function handleCreateSuccess(roomData) {
  showNotification(`討論室建立成功！代碼：${roomData.code}`, 'success');
  // 立刻跳轉到主持人頁面
  router.push(`/host?room=${roomData.code}&new=true`);
}

function handleJoinSuccess(roomCode) {
  showNotification('正在加入討論室...', 'success');
  setTimeout(() => {
    router.push(`/participant?room=${roomCode}`);
  }, 1000);
}

// --- 通知管理 ---
function showNotification(text, type = 'info') {
  notifications.value.push({ text, type });
  setTimeout(() => notifications.value.shift(), 4000);
}
function removeNotification(i) {
  notifications.value.splice(i, 1);
}
</script>

<style scoped>
@import url('../assets/styles.css');

.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 響應式設計 - 只保留 Home.vue 頁面本身需要的 */
@media (max-width: 480px) {
  .nav-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .nav-actions .btn {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>
