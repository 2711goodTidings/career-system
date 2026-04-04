import { createRouter, createWebHistory } from 'vue-router'
import Landing from '../views/Landing.vue'
import Register from '../views/Register.vue'
import Profile from '../views/Profile.vue'
import Ability from '../views/Ability.vue'
import Career from '../views/Career.vue'
import Planning from '../views/Planning.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/ability',
    name: 'Ability',
    component: Ability
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