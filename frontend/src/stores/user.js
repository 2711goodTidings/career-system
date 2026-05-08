import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLogin: false,
    userId: '',
    username: '',
    avatar: ''
  }),
  actions: {
    login(userInfo) {
      this.isLogin = true
      this.userId = userInfo.userId
      this.username = userInfo.username
      this.avatar = userInfo.avatar || ''
    },
    setAvatar(avatar) {
      this.avatar = avatar || ''
    },
    logout() {
      this.isLogin = false
      this.userId = ''
      this.username = ''
      this.avatar = ''
    }
  }
})
