<template>
  <StartupIntro v-if="showIntro" @finish="showIntro = false" />
  <router-view />
</template>

<script setup>
import { ref } from 'vue'
import StartupIntro from './components/StartupIntro.vue'

const showIntro = ref(true)
</script>