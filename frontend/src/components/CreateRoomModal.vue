<template>
  <div class="modal" :class="{ active: visible }" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>建立新討論室</h3>
        <button class="modal-close" @click="close">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="submitForm">
        <div class="form-group">
          <label for="roomTitle">討論室名稱</label>
          <input type="text" id="roomTitle" v-model="form.title" required placeholder="請輸入「討論室名稱」" />
        </div>
        <div class="form-group">
          <label for="topic">題目</label>
          <input type="text" id="topic" v-model="form.topic" required placeholder="請輸入「討論題目」" />
        </div>
        <div class="form-group">
          <label for="topicSummary">題目摘要資訊</label>
          <textarea id="topicSummary" v-model="form.topicSummary" rows="4" placeholder="簡短說明這個題目（可選）"></textarea>
        </div>
        <div class="form-group">
          <label for="desiredOutcome">想達到的討論效果</label>
          <input type="text" id="desiredOutcome" v-model="form.desiredOutcome" placeholder="ex. 製作企劃書、方案發想..." />
        </div>
        <div class="form-group">
          <label for="topic-count">問題/主題數量（1~5）</label>
          <div class="slider-container">
            <span class="slider-value">{{ form.topicCount }}</span>
            <input type="range" id="topicCount" class="slider" min="1" max="5" step="1" v-model="form.topicCount" />
          </div>
        </div>
        <div class="form-group">
          <label>討論時間</label>
          <div style="display:flex; gap:8px; align-items:center; justify-content:space-evenly">
            <input type="number" v-model.number="form.timeHours" min="0" max="23" style="width:80px" aria-label="時" />
            <span>時</span>
            <input type="number" v-model.number="form.timeMinutes" min="0" max="59" style="width:80px" aria-label="分" />
            <span>分</span>
            <input type="number" v-model.number="form.timeSeconds" min="0" max="59" style="width:80px" aria-label="秒" />
            <span>秒</span>
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-outline" @click="close">取消</button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? '建立中...' : '建立討論室' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';

const props = defineProps({
  visible: Boolean
});

const emit = defineEmits(['close', 'create-success']);

const isSubmitting = ref(false);
const form = reactive({
  title: '',
  topic: '',
  topicSummary: '',
  desiredOutcome: '',
  topicCount: 1,
  timeHours: 0,
  timeMinutes: 15,
  timeSeconds: 0,
});

// --- API 位址 ---
import { API_BASE_URL } from '@/utils/api';
const API_BASE = API_BASE_URL;

// --- 當 Modal 顯示時，重設表單 ---
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm();
    setTimeout(() => document.getElementById('roomTitle')?.focus(), 200);
  }
});

function resetForm() {
    form.title = '';
    form.topic = '';
    form.topicSummary = '';
    form.desiredOutcome = '';
    form.topicCount = 1;
    form.timeHours = 0;
    form.timeMinutes = 15;
    form.timeSeconds = 0;
}

function close() {
  emit('close');
}

async function submitForm() {
  if (!form.title.trim()) {
    emit('show-notification', { text: '請填寫討論室名稱', type: 'error' });
    return;
  }
  isSubmitting.value = true;

  try {
    const h = Number(form.timeHours || 0);
    const m = Number(form.timeMinutes || 0);
    const s = Number(form.timeSeconds || 0);
    const duration = Math.max(0, (h * 3600) + (m * 60) + s);

    const resp = await fetch(`${API_BASE}/api/create_room`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: form.title.trim(),
        topics: ["預設主題"],
        topic_summary: form.topicSummary?.trim() || '',
        desired_outcome: form.desiredOutcome?.trim() || '',
        topic_count: form.topicCount,
        countdown: duration || 0,
      })
    });

    if (!resp.ok) {
      const errorData = await resp.json().catch(() => ({}));
      throw new Error(`建立討論室失敗: ${errorData.detail || '請檢查後端日誌'}`);
    }
    const roomData = await resp.json();
    emit('create-success', roomData);
    close();
  } catch (err) {
    emit('show-notification', { text: err.message || '操作失敗', type: 'error' });
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* 從 Home.vue 複製過來的 Modal 和 Form 相關樣式 */
@import url('../assets/styles.css');

.slider-container {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.slider-value {
    font-size: 1.2rem;
    font-weight: bold;
    color: #007bff;
}
.slider {
    width: 100%;
}
</style>