<template>
  <!-- 取名視窗 -->
  <div v-if="showNameModal" class="name-modal-overlay" @click.self="useAnonymous">
    <div class="name-modal">
      <div class="name-modal-header">
        <h3>歡迎加入討論室</h3>
        <p>請輸入您的暱稱，或選擇以匿名身份參與</p>
      </div>
      <div class="name-modal-body">
        <div class="nickname-input-group">
          <input v-model="nicknameInput" @keyup.enter="confirmInitialNickname" placeholder="輸入您的暱稱..." class="nickname-input" maxlength="10" ref="nicknameInputRef" />
          <div class="input-hint">最多 10 個字元</div>
        </div>
        <div class="name-modal-actions">
          <button @click="confirmInitialNickname" class="btn btn-primary">
            <i class="fa-solid fa-check"></i>
            {{ nicknameInput.trim() ? '使用此暱稱' : '匿名參與' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 暱稱編輯視窗 -->
  <div v-if="showEditModal" class="nickname-edit-modal-overlay" @click.self="closeEditModal">
    <div class="nickname-edit-modal">
      <div class="nickname-edit-modal-header">
        <h3>修改暱稱</h3>
        <button class="btn-close" @click="closeEditModal">&times;</button>
      </div>
      <div class="nickname-edit-modal-body">
        <div class="nickname-edit-input-group">
          <label for="nicknameEdit">新暱稱</label>
          <input id="nicknameEdit" v-model="nicknameInput" @keyup.enter="confirmEdit" placeholder="輸入新的暱稱..." class="nickname-edit-input" maxlength="10" />
          <div class="input-hint">最多 10 個字元，留空則自動產生匿名名稱</div>
        </div>
        <div class="nickname-edit-modal-actions">
          <button @click="confirmEdit" class="btn btn-primary">確認修改</button>
          <button @click="closeEditModal" class="btn btn-outline">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  showNameModal: Boolean,
  showEditModal: Boolean,
  initialNickname: String
});

const emit = defineEmits(['update:showNameModal', 'update:showEditModal', 'nickname-confirmed']);

const nicknameInput = ref('');
const nicknameInputRef = ref(null);

watch(() => props.showNameModal, async (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden';
    await nextTick();
    nicknameInputRef.value?.focus();
  } else {
    document.body.style.overflow = '';
  }
});

watch(() => props.showEditModal, (newVal) => {
  if (newVal) {
    nicknameInput.value = props.initialNickname || '';
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

const getFinalNickname = () => {
  const trimmed = nicknameInput.value.trim();
  return trimmed || `訪客${Math.floor(Math.random() * 10000)}`;
};

const confirmInitialNickname = () => {
  const finalNickname = getFinalNickname();
  emit('nickname-confirmed', finalNickname);
  emit('update:showNameModal', false);
  nicknameInput.value = '';
};

const useAnonymous = () => {
  nicknameInput.value = '';
  confirmInitialNickname();
};

const confirmEdit = () => {
  const finalNickname = getFinalNickname();
  emit('nickname-confirmed', finalNickname);
  emit('update:showEditModal', false);
  nicknameInput.value = '';
};

const closeEditModal = () => {
  emit('update:showEditModal', false);
};
</script>

<style scoped>
/* 從 ParticipantPanel.vue 複製所有與 .name-modal-* 和 .nickname-edit-modal-* 相關的 CSS 樣式到這裡 */
/* ... 此處省略，但您需要將原檔案中的對應 CSS 規則貼過來 ... */
@import url('../assets/styles.css');
/* 取名視窗樣式 */
.name-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.2s ease;
}

.name-modal {
  background: var(--background);
  border-radius: 1.25rem;
  width: 90%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
  border: 1px solid var(--border);
}

.name-modal-header {
  padding: 2rem 2rem 1rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  position: relative;
}

.name-modal-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.name-modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.name-modal-header p {
  font-size: 1rem;
  margin: 0;
  opacity: 0.95;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.name-modal-body {
  padding: 2rem;
}

.nickname-input-group {
  margin-bottom: 1.5rem;
}

.nickname-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.nickname-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
  background: var(--background);
}

.nickname-input::placeholder {
  color: var(--text-secondary);
}

.input-hint {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
}

.name-modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.name-modal-actions .btn {
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.name-modal-actions .btn-primary {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow);
}

.name-modal-actions .btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.name-modal-actions .btn-outline {
  background: transparent;
  border: 2px solid var(--border);
  color: var(--text-secondary);
}

.name-modal-actions .btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

@keyframes modalSlideUp {
  from { 
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 響應式設計 - 取名視窗 */
@media (max-width: 480px) {
  .name-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .name-modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .name-modal-header h3 {
    font-size: 1.3rem;
  }
  
  .name-modal-header p {
    font-size: 0.95rem;
  }
  
  .name-modal-body {
    padding: 1.5rem;
  }
  
  .nickname-input {
    padding: 0.875rem 1rem;
    font-size: 1rem;
  }
}
/* 暱稱編輯視窗樣式 */
.nickname-edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.2s ease;
}

.nickname-edit-modal {
  background: var(--background);
  border-radius: 1rem;
  width: 90%;
  max-width: 450px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
  border: 1px solid var(--border);
}

.nickname-edit-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.nickname-edit-modal-header h3 {
  font-size: 1.25rem;
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
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.btn-close:hover {
  background: var(--border);
  color: var(--text-primary);
}

.nickname-edit-modal-body {
  padding: 2rem;
}

.nickname-edit-input-group {
  margin-bottom: 1.5rem;
}

.nickname-edit-input-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.nickname-edit-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border-radius: 0.5rem;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.nickname-edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  background: var(--background);
}

.nickname-edit-input::placeholder {
  color: var(--text-secondary);
}

.nickname-edit-modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.nickname-edit-modal-actions .btn {
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
}

.nickname-edit-modal-actions .btn-primary {
  background: var(--primary-color);
  color: white;
}

.nickname-edit-modal-actions .btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.nickname-edit-modal-actions .btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.nickname-edit-modal-actions .btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}
</style>