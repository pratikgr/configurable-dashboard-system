import { createRouter, createWebHistory } from 'vue-router'
import DashboardRenderer from '@/components/Dashboard/DashboardRenderer.vue'
import DashboardList from '@/components/Dashboard/DashboardList.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: DashboardList
  },
  {
    path: '/dashboard/:dashboardId',
    name: 'dashboard',
    component: DashboardRenderer,
    props: true
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/components/Admin/AdminPanel.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
