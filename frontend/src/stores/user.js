import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLogin: false,
    userId: '',
    username: ''
  }),
  actions: {
    login(userInfo) {
      this.isLogin = true
      this.userId = userInfo.userId
      this.username = userInfo.username
    },
    logout() {
      this.isLogin = false
      this.userId = ''
      this.username = ''
    }
  }
})