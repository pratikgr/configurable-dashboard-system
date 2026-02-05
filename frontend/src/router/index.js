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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
