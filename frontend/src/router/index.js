import { createRouter, createWebHistory } from 'vue-router'
import Landing from '../views/Landing.vue'
import Profile from '../views/Profile.vue'
import Assessment from '../views/Assessment.vue'
import Career from '../views/Career.vue'
import Planning from '../views/Planning.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/assessment',
    name: 'Assessment',
    component: Assessment
  },
  {
    path: '/ability',
    redirect: '/assessment'
  },
  {
    path: '/career',
    name: 'Career',
    component: Career
  },
  {
    path: '/planning',
    name: 'Planning',
    component: Planning
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
