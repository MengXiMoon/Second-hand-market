<template>
  <el-container class="layout">
    <div class="navbar-wrapper">
      <Navbar />
    </div>
    <el-main class="main-content">
      <slot />
    </el-main>
  </el-container>
</template>

<script setup>
import Navbar from './Navbar.vue'
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.navbar-wrapper {
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-shrink: 0;
}

.main-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  flex: 1;
  width: 100%;
}
</style>
