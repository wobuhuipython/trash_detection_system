<template>
  <div class="search-page">
    <div class="container">
      <div class="search-header">
        <h1>垃圾分类查询</h1>
        <p>输入垃圾名称，快速查询分类方式</p>
      </div>

      <div class="search-box card">
        <input 
          v-model="keyword" 
          @keyup.enter="handleSearch"
          class="search-input" 
          placeholder="请输入垃圾名称，如：塑料瓶、电池..."
        />
        <button @click="handleSearch" class="btn btn-primary search-btn">
          搜索
        </button>
      </div>

      <div v-if="loading" class="loading">搜索中...</div>

      <div v-else-if="results.length > 0" class="results">
        <h3 class="results-title">找到 {{ results.length }} 个结果</h3>
        <div class="results-grid">
          <div 
            v-for="item in results" 
            :key="item.name"
            class="result-card"
            :style="{ '--color': item.color }"
          >
            <div class="result-icon">{{ item.icon }}</div>
            <div class="result-info">
              <h4 class="result-name">{{ item.name }}</h4>
              <div class="result-category">{{ item.category }}</div>
              <p class="result-tips" v-if="item.tips">
                <strong>解释：</strong>{{ item.tips }}
              </p>
              <p class="result-contain" v-if="item.contain">
                <strong>包含：</strong>{{ item.contain }}
              </p>
              <p class="result-tip" v-if="item.tip">
                <strong>投放提示：</strong>{{ item.tip }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="searched && results.length === 0" class="no-results">
        <div class="no-results-icon">😕</div>
        <p>未找到相关结果，请尝试其他关键词</p>
      </div>

      <!-- 热门搜索 -->
      <div class="hot-search card">
        <h3>热门搜索</h3>
        <div class="hot-tags">
          <span 
            v-for="tag in hotTags" 
            :key="tag"
            @click="quickSearch(tag)"
            class="hot-tag"
          >
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { searchGarbage } from '../api'

const keyword = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)

const hotTags = ['塑料瓶', '电池', '剩饭', '纸箱', '玻璃瓶', '旧衣服', '药品', '灯管']

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await searchGarbage(keyword.value)
    results.value = res.data.data
  } catch (e) {
    console.error('搜索失败', e)
  } finally {
    loading.value = false
  }
}

const quickSearch = (tag) => {
  keyword.value = tag
  handleSearch()
}
</script>

<style scoped>
.search-header {
  text-align: center;
  margin-bottom: 30px;
}

.search-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.search-header p {
  color: var(--text-light);
}

.search-box {
  display: flex;
  gap: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: 2px solid var(--border);
  border-radius: 12px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
}

.search-btn {
  padding: 16px 32px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-light);
}

.results-title {
  margin-bottom: 20px;
  color: var(--text-dark);
}

.results-grid {
  display: grid;
  gap: 16px;
}

.result-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid var(--color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.result-icon {
  font-size: 40px;
}

.result-name {
  font-size: 18px;
  margin-bottom: 4px;
}

.result-category {
  display: inline-block;
  background: var(--color);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  margin-bottom: 8px;
}

.result-tips,
.result-contain,
.result-tip {
  color: var(--text-light);
  font-size: 14px;
  margin-top: 6px;
  line-height: 1.5;
}

.result-tips strong,
.result-contain strong,
.result-tip strong {
  color: var(--text-dark);
}

.no-results {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
}

.no-results-icon {
  font-size: 60px;
  margin-bottom: 16px;
}

.hot-search {
  margin-top: 30px;
}

.hot-search h3 {
  margin-bottom: 16px;
}

.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hot-tag {
  padding: 8px 16px;
  background: var(--bg-light);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.hot-tag:hover {
  background: var(--primary);
  color: white;
}
</style>
