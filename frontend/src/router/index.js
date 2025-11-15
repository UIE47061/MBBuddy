import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import HostPanel from '../components/HostPanel.vue'
import ParticipantPanel from '../components/ParticipantPanel.vue'
import ScoreJudgePanel from '../components/ScoreJudgePanel.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/host', component: HostPanel },
  { path: '/participant', component: ParticipantPanel },
  { 
    path: '/meeting-summary', 
    component: ScoreJudgePanel,
    name: 'MeetingSummary',
    props: route => ({
      roomCode: route.query.room,
      meetingTitle: route.query.title || '未命名討論',
      // 其他 props 可以根據需要添加
    })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
