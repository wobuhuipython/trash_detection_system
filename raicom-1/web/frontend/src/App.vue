<template>
  <div class="app">
    <nav class="navbar">
      <div class="container nav-content">
        <router-link to="/" class="logo">
          <span class="logo-text">垃圾分类科普平台</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/search" class="nav-link">分类查询</router-link>
          <router-link to="/nearby" class="nav-link">附近垃圾桶</router-link>
          <router-link to="/knowledge" class="nav-link">环保资讯</router-link>
          <router-link to="/quiz" class="nav-link">趣味答题</router-link>
          <router-link to="/feedback" class="nav-link">质量反馈</router-link>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer">
      <div class="container">
        <p>垃圾分类科普知识平台 | 保护环境，从我做起</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-weight: bold;
  font-size: 20px;
}

.logo-icon {
  font-size: 28px;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.main-content {
  flex: 1;
  padding: 30px 0;
}

.footer {
  background: #2c3e50;
  color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  text-align: center;
  font-size: 14px;
}
</style>
