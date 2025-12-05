<template>
  <div class="knowledge-page">
    <div class="container">
      <div class="page-header">
        <h1>环保资讯</h1>
        <p>了解最新环保动态，关注垃圾分类资讯</p>
      </div>

      <div class="loading" v-if="loading">
        <span>加载中...</span>
      </div>

      <div class="knowledge-grid" v-else>
        <div 
          v-for="item in knowledge" 
          :key="item.id"
          class="knowledge-card card"
          @click="openArticle(item)"
        >
          <img v-if="item.imgUrl" :src="item.imgUrl" class="card-image" alt="">
          <div class="card-body">
            <div class="knowledge-meta">
              <span class="knowledge-source">{{ item.source }}</span>
              <span class="knowledge-time">{{ item.time }}</span>
            </div>
            <h3>{{ item.title }}</h3>
            <p class="knowledge-preview">{{ getPreview(item.content) }}</p>
            <div class="read-more">
              <span>阅读原文 →</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getKnowledge } from '../api'

const knowledge = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getKnowledge()
    knowledge.value = res.data.data
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
})

const getPreview = (content) => {
  if (!content) return '点击查看详情...'
  // 去除HTML标签
  const text = content.replace(/<[^>]+>/g, '')
  return text.length > 100 ? text.slice(0, 100) + '...' : text
}

const openArticle = (item) => {
  if (item.url) {
    window.open(item.url, '_blank')
  }
}
</script>

<style scoped>
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.page-header p {
  color: var(--text-light);
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--text-light);
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.knowledge-card {
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
  padding: 0;
}

.knowledge-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.card-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.card-body {
  padding: 20px;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--text-light);
}

.knowledge-source {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 3px 10px;
  border-radius: 10px;
}

.knowledge-card h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: var(--text-dark);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.knowledge-preview {
  color: var(--text-light);
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.read-more {
  color: var(--primary);
  font-size: 13px;
  font-weight: 500;
}

.read-more:hover {
  text-decoration: underline;
}

@media (max-width: 992px) {
  .knowledge-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .knowledge-grid {
    grid-template-columns: 1fr;
  }
}
</style>
