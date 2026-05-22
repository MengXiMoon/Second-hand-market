<template>
  <el-container class="layout">
    <!-- Premium background glowing blur blobs -->
    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>
    <div class="ambient-glow glow-3"></div>

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
  background: transparent;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
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
  padding: 30px 24px;
  flex: 1;
  width: 100%;
  position: relative;
  z-index: 10;
}

/* Premium ambient backdrop flows */
.ambient-glow {
  position: fixed;
  width: 40vw;
  height: 40vw;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  z-index: 1;
  opacity: 0.15;
  transition: all 1s ease;
}

.glow-1 {
  top: -10vw;
  left: -10vw;
  background: radial-gradient(circle, #5e5bf5 0%, rgba(94, 91, 245, 0) 70%);
  animation: floatSlowly 12s infinite alternate ease-in-out;
}

.glow-2 {
  bottom: -10vw;
  right: -10vw;
  background: radial-gradient(circle, #f43f5e 0%, rgba(244, 63, 94, 0) 70%);
  animation: floatSlowly2 15s infinite alternate ease-in-out;
}

.glow-3 {
  top: 30vh;
  left: 35vw;
  background: radial-gradient(circle, #10b981 0%, rgba(16, 185, 129, 0) 70%);
  width: 30vw;
  height: 30vw;
  opacity: 0.08;
  animation: floatSlowly3 18s infinite alternate ease-in-out;
}

@keyframes floatSlowly {
  0% {
    transform: translate(0, 0) scale(1);
  }
  100% {
    transform: translate(4vw, 3vw) scale(1.1);
  }
}

@keyframes floatSlowly2 {
  0% {
    transform: translate(0, 0) scale(1.1);
  }
  100% {
    transform: translate(-3vw, -4vw) scale(0.9);
  }
}

@keyframes floatSlowly3 {
  0% {
    transform: translate(0, 0) scale(0.9);
  }
  100% {
    transform: translate(2vw, -2vw) scale(1.15);
  }
}
</style>
