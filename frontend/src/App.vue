<template>
  <StartupIntro v-if="showIntro" @finish="showIntro = false" />
  <AppLogo v-if="!showIntro" />
  <router-view />
</template>

<script setup>
import { ref } from 'vue'
import AppLogo from './components/AppLogo.vue'
import StartupIntro from './components/StartupIntro.vue'

const showIntro = ref(true)
</script>
