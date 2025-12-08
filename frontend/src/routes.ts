import { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('./views/MeetingList.vue'),
    meta: { title: '会议列表', requiresAuth: true }
  },
  {
    path: '/meeting/create',
    name: 'MeetingCreate',
    component: () => import('./views/MeetingCreate.vue'),
    meta: { title: '创建会议', requiresAuth: true }
  },
  {
    path: '/meeting/upload',
    name: 'DocumentUpload',
    component: () => import('./views/DocumentUpload.vue'),
    meta: { title: '上传资料', requiresAuth: true }
  },
  {
    path: '/meeting/:id/upload',
    name: 'DocumentUploadWithId',
    component: () => import('./views/DocumentUpload.vue'),
    meta: { title: '上传资料', requiresAuth: true }
  },
  {
    path: '/meeting/:id/complete',
    name: 'MeetingComplete',
    component: () => import('./views/MeetingComplete.vue'),
    meta: { title: '会议创建完成', requiresAuth: true }
  },
  {
    path: '/meeting/:id/live',
    name: 'LiveMeeting',
    component: () => import('./views/LiveMeeting.vue'),
    meta: { title: '实时会议', requiresAuth: true }
  },
  {
    path: '/meeting/:id/summary',
    name: 'MeetingSummary',
    component: () => import('./views/MeetingSummary.vue'),
    meta: { title: '会议总结', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue'),
    meta: { title: '系统设置', requiresAuth: true }
  },
  {
    path: '/demo-ali',
    name: 'DemoAli',
    component: () => import('./views/DemoAli.vue'),
    meta: { title: '阿里云通义听悟实时语音转文字测试', requiresAuth: true }
  },
  {
    path: '/ai-chat',
    name: 'AIChat',
    component: () => import('./views/AIChat.vue'),
    meta: { title: 'AI智能对话', requiresAuth: true }
  },
  {
    path: '/realtime-chat',
    name: 'RealtimeChat',
    component: () => import('./views/RealtimeChat.vue'),
    meta: { title: 'AI实时对话', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('./views/NotFound.vue'),
    meta: { title: 'Page not found' }
  },
]

export { routes }
