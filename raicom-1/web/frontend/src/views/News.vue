<template>
  <div class="news-page">
    <div class="container">
      <div class="page-header">
        <h1>环保资讯</h1>
        <p>了解最新环保政策和垃圾分类动态</p>
      </div>

      <!-- 资讯分类 -->
      <div class="news-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >{{ tab.name }}</button>
      </div>

      <!-- 资讯列表 -->
      <div class="news-grid">
        <div 
          v-for="news in filteredNews" 
          :key="news.id"
          class="news-card card"
          @click="showDetail(news)"
        >
          <div class="news-tag" :style="{ background: getTagColor(news.category) }">{{ news.category }}</div>
          <h3>{{ news.title }}</h3>
          <p class="news-summary">{{ news.summary }}</p>
          <div class="news-meta">
            <span class="news-date">{{ news.date }}</span>
            <span class="news-source">{{ news.source }}</span>
          </div>
        </div>
      </div>

      <!-- 环保小贴士 -->
      <section class="tips-section card">
        <h2>日常环保小贴士</h2>
        <div class="tips-grid">
          <div v-for="(tip, i) in ecoTips" :key="i" class="tip-item">
            <span class="tip-icon">{{ tip.icon }}</span>
            <div class="tip-content">
              <h4>{{ tip.title }}</h4>
              <p>{{ tip.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 详情弹窗 -->
      <div v-if="selectedNews" class="modal-overlay" @click="selectedNews = null">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="selectedNews = null">×</button>
          <div class="modal-tag" :style="{ background: getTagColor(selectedNews.category) }">{{ selectedNews.category }}</div>
          <h2>{{ selectedNews.title }}</h2>
          <div class="modal-meta">
            <span>{{ selectedNews.date }}</span>
            <span>来源：{{ selectedNews.source }}</span>
          </div>
          <div class="modal-body" v-html="selectedNews.content"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeTab = ref('all')
const selectedNews = ref(null)

const tabs = [
  { key: 'all', name: '全部' },
  { key: 'policy', name: '政策法规' },
  { key: 'tech', name: '环保科技' },
  { key: 'action', name: '环保行动' }
]

const newsData = ref([
  {
    id: 1,
    title: '全国垃圾分类工作取得显著成效',
    category: '政策法规',
    date: '2024-12-01',
    source: '环保部',
    summary: '截至2024年底，全国地级及以上城市生活垃圾分类覆盖率已超过90%，居民分类投放准确率显著提升。',
    content: '<p>截至2024年底，全国地级及以上城市生活垃圾分类覆盖率已超过90%，居民分类投放准确率显著提升。</p><p>各地积极推进垃圾分类工作，通过宣传教育、设施建设、监督考核等多种措施，有效提高了居民的环保意识和分类投放习惯。</p><p>下一步将继续完善分类收运体系，提高资源化利用水平。</p>'
  },
  {
    id: 2,
    title: '智能垃圾分类设备助力社区环保',
    category: '环保科技',
    date: '2024-11-28',
    source: '科技日报',
    summary: '新型AI智能垃圾分类设备在多个城市试点应用，通过图像识别技术自动识别垃圾类型，准确率达95%以上。',
    content: '<p>新型AI智能垃圾分类设备在多个城市试点应用，通过图像识别技术自动识别垃圾类型，准确率达95%以上。</p><p>该设备配备触摸屏和语音提示功能，方便居民使用。投放正确还可获得积分奖励，有效提高了居民参与积极性。</p>'
  },
  {
    id: 3,
    title: '世界环境日：共建清洁美丽世界',
    category: '环保行动',
    date: '2024-11-20',
    source: '新华网',
    summary: '今年世界环境日主题为"共建清洁美丽世界"，全国各地开展丰富多彩的环保宣传活动。',
    content: '<p>今年世界环境日主题为"共建清洁美丽世界"，全国各地开展丰富多彩的环保宣传活动。</p><p>活动包括环保知识竞赛、垃圾分类体验、植树造林等，吸引了大量市民参与，营造了浓厚的环保氛围。</p>'
  },
  {
    id: 4,
    title: '新版《生活垃圾分类标志》标准发布',
    category: '政策法规',
    date: '2024-11-15',
    source: '住建部',
    summary: '新版生活垃圾分类标志标准正式发布，统一了全国垃圾分类标志的图形符号、颜色和文字说明。',
    content: '<p>新版生活垃圾分类标志标准正式发布，统一了全国垃圾分类标志的图形符号、颜色和文字说明。</p><p>新标准将垃圾分为可回收物、有害垃圾、厨余垃圾和其他垃圾四大类，并明确了各类垃圾的具体范围和投放要求。</p>'
  },
  {
    id: 5,
    title: '可降解塑料技术取得重大突破',
    category: '环保科技',
    date: '2024-11-10',
    source: '科学网',
    summary: '国内科研团队研发出新型可降解塑料材料，可在自然环境中3个月内完全降解，有望替代传统塑料。',
    content: '<p>国内科研团队研发出新型可降解塑料材料，可在自然环境中3个月内完全降解，有望替代传统塑料。</p><p>该材料以玉米淀粉为原料，生产成本与传统塑料相当，具有良好的市场应用前景。</p>'
  },
  {
    id: 6,
    title: '青年志愿者开展垃圾分类宣传活动',
    category: '环保行动',
    date: '2024-11-05',
    source: '中国青年报',
    summary: '全国各地青年志愿者深入社区、学校开展垃圾分类宣传活动，通过互动游戏、知识讲座等形式普及环保知识。',
    content: '<p>全国各地青年志愿者深入社区、学校开展垃圾分类宣传活动，通过互动游戏、知识讲座等形式普及环保知识。</p><p>志愿者们还制作了精美的宣传手册和视频，帮助居民更好地理解和掌握垃圾分类方法。</p>'
  }
])

const ecoTips = ref([
  { icon: '🛍️', title: '自带购物袋', desc: '减少一次性塑料袋使用' },
  { icon: '🚰', title: '节约用水', desc: '随手关闭水龙头' },
  { icon: '💡', title: '节约用电', desc: '离开房间随手关灯' },
  { icon: '🚲', title: '绿色出行', desc: '多乘公交或骑行' },
  { icon: '📦', title: '减少包装', desc: '选择简易包装商品' },
  { icon: '🌱', title: '绿色消费', desc: '购买环保认证产品' }
])

const filteredNews = computed(() => {
  if (activeTab.value === 'all') return newsData.value
  const categoryMap = { policy: '政策法规', tech: '环保科技', action: '环保行动' }
  return newsData.value.filter(n => n.category === categoryMap[activeTab.value])
})

const getTagColor = (category) => {
  const colors = { '政策法规': '#667eea', '环保科技': '#27ae60', '环保行动': '#f39c12' }
  return colors[category] || '#667eea'
}

const showDetail = (news) => { selectedNews.value = news }
</script>

<style scoped>
.page-header { text-align: center; margin-bottom: 30px; }
.page-header h1 { font-size: 32px; margin-bottom: 10px; }
.page-header p { color: var(--text-light); }

.news-tabs { display: flex; justify-content: center; gap: 12px; margin-bottom: 30px; }
.tab-btn { padding: 10px 24px; border: 2px solid var(--border); border-radius: 20px; background: white; cursor: pointer; font-size: 14px; transition: all 0.3s; }
.tab-btn:hover, .tab-btn.active { background: var(--primary); color: white; border-color: var(--primary); }

.news-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 40px; }
.news-card { cursor: pointer; transition: all 0.3s; }
.news-card:hover { transform: translateY(-6px); }
.news-tag { display: inline-block; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-bottom: 12px; }
.news-card h3 { font-size: 17px; margin-bottom: 10px; color: var(--text-dark); line-height: 1.4; }
.news-summary { color: var(--text-light); font-size: 14px; line-height: 1.6; margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.news-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-light); }

.tips-section h2 { text-align: center; margin-bottom: 24px; font-size: 24px; }
.tips-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.tip-item { display: flex; align-items: center; gap: 16px; background: var(--bg-light); padding: 20px; border-radius: 12px; }
.tip-icon { font-size: 32px; }
.tip-content h4 { font-size: 15px; margin-bottom: 4px; }
.tip-content p { font-size: 13px; color: var(--text-light); }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 40px; border-radius: 20px; max-width: 700px; width: 90%; position: relative; max-height: 80vh; overflow-y: auto; }
.modal-close { position: absolute; top: 16px; right: 20px; background: none; border: none; font-size: 28px; cursor: pointer; color: var(--text-light); }
.modal-tag { display: inline-block; color: white; padding: 6px 16px; border-radius: 12px; font-size: 13px; margin-bottom: 16px; }
.modal-content h2 { font-size: 24px; margin-bottom: 12px; line-height: 1.4; }
.modal-meta { display: flex; gap: 20px; font-size: 13px; color: var(--text-light); margin-bottom: 20px; }
.modal-body { color: var(--text-dark); line-height: 1.8; font-size: 15px; }
.modal-body p { margin-bottom: 16px; }

@media (max-width: 768px) {
  .news-grid, .tips-grid { grid-template-columns: 1fr; }
}
</style>
