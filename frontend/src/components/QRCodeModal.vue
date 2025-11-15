<template>
  <div v-if="isVisible" class="qrcode-modal-overlay" @click.self="hideModal">
    <div class="qrcode-modal">
      <div class="qrcode-modal-header">
        <h3>討論室 QR Code</h3>
        <button class="btn-close" @click="hideModal">&times;</button>
      </div>
      <div class="qrcode-modal-body">
        <div class="qrcode-large">
          <qrcode-vue :value="roomLink" :size="qrcodeSize" level="H" />
        </div>
        <div class="qrcode-modal-info">
          <div class="qrcode-room-code">討論室代碼：{{ roomCode }}</div>
          <div class="qrcode-link-text">{{ roomLink }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import QrcodeVue from 'qrcode.vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true
  },
  roomCode: {
    type: String,
    required: true
  },
  roomLink: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['hide-modal'])

const qrcodeSize = ref(window.innerWidth < 768 ? 320 : 640)

function hideModal() {
  emit('hide-modal')
}

function updateQRCodeSize() {
  qrcodeSize.value = Math.max(120, Math.min(280, Math.floor(window.innerWidth * 0.3)))
}

onMounted(() => {
  updateQRCodeSize()
  window.addEventListener('resize', updateQRCodeSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateQRCodeSize)
})
</script>

<style scoped>
.qrcode-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.2s;
  backdrop-filter: blur(4px);
}

.qrcode-modal {
  background: var(--background, #fff);
  border-radius: 1rem;
  width: 98vw;
  max-width: 420px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem;
  overflow: hidden;
}

.qrcode-modal-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.qrcode-modal-header h3 {
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
}

.qrcode-modal-body {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qrcode-large {
  background: #fff;
  border-radius: 0.7rem;
  margin-bottom: 1.2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 320px;
  max-height: 320px;
  padding: 1rem;
  box-sizing: border-box;
}

.qrcode-modal-info {
  width: 100%;
  text-align: center;
  font-size: 1rem;
  word-break: break-all;
}

.qrcode-room-code {
  font-size: 1.08rem;
  font-weight: 500;
  color: var(--primary-color, #3451db);
  margin-bottom: 0.3em;
}

.qrcode-link-text {
  color: var(--text-secondary, #666);
  font-size: 0.93em;
  margin-top: 0.4em;
  word-break: break-all;
}

@media (max-width: 767px) {
  .qrcode-modal {
    width: 95%;
    max-width: 360px;
  }
  
  .qrcode-large {
    padding: 0.75rem;
  }
}

@media (max-width: 500px) {
  .qrcode-modal { 
    max-width: 98vw; 
    padding: 0.7rem 0.2rem; 
  }
  .qrcode-large { 
    max-width: 80vw; 
    max-height: 80vw; 
    padding: 0.4rem; 
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>