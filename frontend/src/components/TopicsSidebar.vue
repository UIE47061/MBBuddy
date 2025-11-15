<template>
  <div class="topics-sidebar" :class="{ 'collapsed': isCollapsed, 'panel-style': !isCollapsed }">
    <!-- 折疊時只顯示按鈕 -->
    <div v-if="isCollapsed" class="sidebar-collapsed-toggle" @click="toggleSidebar">
      <i class="fa-solid fa-angles-right"></i>
    </div>
    
    <!-- 展開時顯示完整側邊欄 -->
    <template v-else>
      <div class="panel-header">
        <h2>主題列表</h2>
        <div class="panel-controls">
          <div class="sidebar-toggle" @click="toggleSidebar">
            <i class="fa-solid fa-angles-left"></i>
          </div>
        </div>
      </div>
      <div class="topics-container">
        <div class="topic-item" v-for="(topic, index) in topics" :key="index" 
            :class="{ 'active': selectedTopicIndex === index }" 
            @click="selectTopic(index)">
          <i class="fa-solid fa-list topic-icon"></i>
          <div class="topic-text">{{ topic.title }}</div>
          <button class="topic-edit-btn" @click.stop="editTopic(index)" title="重命名主題">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
        </div>
        
        <!-- 主題新增按鈕 -->
        <div class="topic-actions">
          <button class="btn btn-primary btn-sm" @click="addNewTopic">
            <i class="fa-solid fa-plus"></i>
            <span>新增主題</span>
          </button>
        </div>
      </div>
      <!-- 匯出全部單獨置底 -->
      <div class="sidebar-bottom">
        <button class="btn btn-success btn-sm" @click="generateMindMap" style="width: 90%; margin: 1.5rem auto 0.5rem auto;">
          <i class="fa-solid fa-brain"></i>
          <span>AI心智圖</span>
        </button>
        <button class="btn btn-outline btn-sm" @click="exportAllTopics" style="width: 90%; margin: 0 auto 0 auto;">
          <i class="fa-solid fa-download"></i>
          <span>匯出全部</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
const props = defineProps({
  topics: {
    type: Array,
    required: true
  },
  selectedTopicIndex: {
    type: Number,
    required: true
  },
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'toggle-sidebar', 
  'select-topic', 
  'edit-topic', 
  'add-new-topic', 
  'export-all-topics',
  'generate-mind-map'
])

function toggleSidebar() {
  emit('toggle-sidebar')
}

function selectTopic(index) {
  emit('select-topic', index)
}

function editTopic(index) {
  emit('edit-topic', index)
}

function addNewTopic() {
  emit('add-new-topic')
}

function exportAllTopics() {
  emit('export-all-topics')
}

function generateMindMap() {
  emit('generate-mind-map')
}
</script>

<style scoped>
.topics-sidebar {
  width: 280px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.topics-sidebar.collapsed {
  width: 40px;
  min-height: 60px;
  background: transparent;
  border: none;
  box-shadow: none;
}

.panel-style {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  overflow: hidden;
}

.sidebar-collapsed-toggle {
  position: absolute;
  top: 15px;
  left: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--primary-color);
  font-size: 1.1rem;
  background: var(--surface);
  border-radius: 0 0.5rem 0.5rem 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.sidebar-collapsed-toggle:hover {
  background: var(--primary-color);
  color: white;
  transform: translateX(3px);
}

.panel-header {
  padding: 1.3rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--background);
}

.panel-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.panel-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.sidebar-toggle {
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: var(--border);
  color: var(--primary-color);
}

.topics-container {
  flex: 1 1 0;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.topic-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--background);
  border: 1px solid var(--border);
}

.topic-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
}

.topic-item.active {
  background: var(--surface);
  border-left: 4px solid var(--primary-color);
}

.topic-icon {
  margin-right: 10px;
  font-size: 1rem;
  color: var(--primary-color);
  width: 20px;
  text-align: center;
}

.topic-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  color: var(--text-primary);
}

.topic-edit-btn {
  opacity: 0;
  background: none;
  border: none;
  font-size: 0.9rem;
  padding: 5px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.topic-item:hover .topic-edit-btn {
  opacity: 0.7;
}

.topic-edit-btn:hover {
  opacity: 1 !important;
  background: var(--surface);
  color: var(--primary-color);
}

.topic-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

.sidebar-bottom {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm i {
  font-size: 0.875rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
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

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

/* 響應式調整 */
@media (max-width: 1024px) {
  .host-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    height: auto;
  }
  
  .topics-sidebar {
    width: 100%;
    margin-bottom: 1rem;
    min-height: 600px;
  }
  
  .topics-sidebar.collapsed {
    width: 50px;
    height: auto;
    margin-bottom: 1rem;
    min-height: 300px;
  }
  
  .sidebar-collapsed-toggle {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
    top: 20px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
}
</style>