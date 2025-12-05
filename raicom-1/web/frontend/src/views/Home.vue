<template>
  <div class="home">
    <div class="container">
      <!-- Hero区域 -->
      <section class="hero">
        <h1 class="hero-title">
          <span class="gradient-text">垃圾分类</span>
          <br>从我做起
        </h1>
        <p class="hero-desc">学习垃圾分类知识，保护我们的地球家园</p>
        <div class="hero-actions">
          <router-link to="/search" class="btn btn-primary">
            开始查询
          </router-link>
          <router-link to="/quiz" class="btn btn-success">
            趣味答题
          </router-link>
          <router-link to="/feedback" class="btn btn-warning">
            质量反馈
          </router-link>
        </div>
      </section>

      <!-- 统计数据 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.categoryCount }}</div>
            <div class="stat-label">垃圾分类</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.itemCount }}</div>
            <div class="stat-label">可查询垃圾</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.newsCount }}</div>
            <div class="stat-label">环保资讯</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.quizCount || 0 }}</div>
            <div class="stat-label">答题题目</div>
          </div>
        </div>
      </section>

      <!-- 分类卡片 -->
      <section class="categories-section">
        <h2 class="section-title">四大垃圾分类</h2>
        <div class="categories-grid">
          <router-link 
            v-for="cat in categories" 
            :key="cat.name"
            :to="`/category/${cat.name}`"
            class="category-card"
            :style="{ '--accent-color': cat.color }"
          >
            <div class="category-icon">{{ cat.icon }}</div>
            <h3 class="category-name">{{ cat.name }}</h3>
            <p class="category-desc">{{ cat.description }}</p>
            <div class="category-count">{{ cat.itemCount }} 种垃圾</div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCategories, getStats } from '../api'

const categories = ref([])
const stats = ref({ categoryCount: 0, itemCount: 0, newsCount: 0, quizCount: 0 })

onMounted(async () => {
  try {
    const [catRes, statsRes] = await Promise.all([getCategories(), getStats()])
    categories.value = catRes.data.data
    stats.value = statsRes.data.data
  } catch (e) {
    console.error('加载数据失败', e)
  }
})
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  margin-bottom: 40px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
}

.hero-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.3;
}

.hero-desc {
  font-size: 18px;
  color: var(--text-light);
  margin-bottom: 30px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--primary);
}

.stat-label {
  color: var(--text-light);
  font-size: 14px;
  margin-top: 4px;
}

.section-title {
  font-size: 28px;
  text-align: center;
  margin-bottom: 30px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 30px 20px;
  text-align: center;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.category-card:hover {
  transform: translateY(-8px);
  border-color: var(--accent-color);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.category-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.category-name {
  font-size: 20px;
  font-weight: bold;
  color: var(--accent-color);
  margin-bottom: 10px;
}

.category-desc {
  font-size: 13px;
  color: var(--text-light);
  line-height: 1.5;
  margin-bottom: 16px;
}

.category-count {
  display: inline-block;
  background: var(--accent-color);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid, .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-title {
    font-size: 32px;
  }
}
</style>
