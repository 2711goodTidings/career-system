<template>
  <div class="ability-page">
    <FeaturePageNav current="ability" />

    <main class="ability-shell">
      <section class="ability-placeholder">
        <p>ABILITY EVALUATION</p>
        <h1>能力评估</h1>
      </section>
    </main>
  </div>
</template>

<script setup>
import FeaturePageNav from '../components/FeaturePageNav.vue'
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.ability-page {
  min-height: 100vh;
  background: #3f7fb6;
  color: #f5f5f3;
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  padding: 34px;
}

.ability-shell {
  width: min(1280px, 100%);
  margin: 0 auto;
}

.ability-placeholder {
  min-height: 72vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.ability-placeholder p {
  margin: 0 0 18px;
  font-size: 14px;
  letter-spacing: 4px;
  opacity: 0.86;
}

.ability-placeholder h1 {
  margin: 0;
  font-size: clamp(58px, 10vw, 132px);
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .ability-page {
    padding: 18px 14px 28px;
  }

  .ability-placeholder h1 {
    font-size: clamp(42px, 18vw, 76px);
  }
}
</style>
