<template>
  <div class="category-page">
    <div class="container">
      <div v-if="category" class="category-detail">
        <div class="category-header" :style="{ '--color': category.color }">
          <div class="category-icon">{{ category.icon }}</div>
          <h1>{{ category.name }}</h1>
          <p>{{ category.description }}</p>
        </div>

        <div class="items-section">
          <h2>包含的垃圾种类</h2>
          <div class="items-grid">
            <div 
              v-for="item in category.items" 
              :key="item.name"
              class="item-card"
            >
              <h3>{{ item.name }}</h3>
              <p class="item-tips">投放提示：{{ item.tips }}</p>
            </div>
          </div>
        </div>

        <router-link to="/search" class="btn btn-primary back-btn">
          ← 返回查询
        </router-link>
      </div>
      <div v-else class="loading">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getCategoryDetail } from '../api'

const route = useRoute()
const category = ref(null)

onMounted(async () => {
  try {
    const res = await getCategoryDetail(route.params.name)
    category.value = res.data.data
  } catch (e) {
    console.error('加载失败', e)
  }
})
</script>

<style scoped>
.category-header {
  background: var(--color);
  color: white;
  padding: 50px;
  border-radius: 20px;
  text-align: center;
  margin-bottom: 40px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.category-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.category-header h1 {
  font-size: 36px;
  margin-bottom: 12px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.category-header p {
  font-size: 16px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.items-section h2 {
  margin-bottom: 24px;
  font-size: 24px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.item-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.item-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: var(--text-dark);
}

.item-tips {
  color: var(--text-light);
  font-size: 14px;
}

.back-btn {
  display: inline-block;
}

.loading {
  text-align: center;
  padding: 60px;
}

@media (max-width: 768px) {
  .items-grid {
    grid-template-columns: 1fr;
  }
}
</style>
