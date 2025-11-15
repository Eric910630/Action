import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/hotspots'
  },
  {
    path: '/hotspots',
    name: 'Hotspots',
    component: () => import('@/views/HotspotsView.vue')
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/ProductsView.vue')
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/AnalysisView.vue')
  },
  {
    path: '/scripts',
    name: 'Scripts',
    component: () => import('@/views/ScriptsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

