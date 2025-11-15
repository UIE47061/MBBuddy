<template>
  <TransitionGroup name="fade">
    <div
      v-for="(msg, i) in notifications"
      :key="i"
      :class="['notification', `notification-${msg.type}`]"
      style="position: fixed; bottom: 32px; right: 32px; z-index: 2000; margin-bottom: 12px; top: auto;"
    >
      <span>{{ msg.text }}</span>
      <button @click="removeNotification(i)">&times;</button>
    </div>
  </TransitionGroup>
</template>

<script setup>
// defineProps 和 defineEmits 是编译器宏，无需导入

const props = defineProps({
  notifications: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['remove-notification'])

function removeNotification(index) {
  emit('remove-notification', index)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.notification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  backdrop-filter: blur(10px);
}

.notification-success {
  background: linear-gradient(135deg, #10b981, #059669);
}

.notification-error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.notification-info {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.notification-warn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.notification button {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  margin-left: 12px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.notification button:hover {
  opacity: 1;
}
</style>