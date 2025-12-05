<template>
  <div class="guide-page">
    <div class="container">
      <div class="page-header">
        <h1>分类指南</h1>
        <p>详细了解各类垃圾的分类方法和投放要求</p>
      </div>

      <!-- 分类流程图 -->
      <section class="flow-section card">
        <h2>垃圾分类流程</h2>
        <div class="flow-chart">
          <div class="flow-step">
            <div class="step-num">1</div>
            <div class="step-content">
              <h4>识别垃圾</h4>
              <p>判断垃圾的材质和性质</p>
            </div>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            <div class="step-num">2</div>
            <div class="step-content">
              <h4>确定分类</h4>
              <p>根据标准确定所属类别</p>
            </div>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            <div class="step-num">3</div>
            <div class="step-content">
              <h4>正确处理</h4>
              <p>按要求清洗、沥干等</p>
            </div>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            <div class="step-num">4</div>
            <div class="step-content">
              <h4>定点投放</h4>
              <p>投入对应颜色垃圾桶</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 分类详解 -->
      <section class="detail-section">
        <h2>四大分类详解</h2>
        <div class="detail-grid">
          <div v-for="cat in guideData" :key="cat.name" class="detail-card" :style="{ '--cat-color': cat.color }">
            <div class="detail-header">
              <span class="cat-icon">{{ cat.icon }}</span>
              <h3>{{ cat.name }}</h3>
            </div>
            <p class="cat-desc">{{ cat.description }}</p>
            <div class="cat-bin">
              <span class="bin-label">垃圾桶颜色：</span>
              <span class="bin-color" :style="{ background: cat.binColor }"></span>
              <span>{{ cat.binName }}</span>
            </div>
            <div class="cat-tips">
              <h4>投放要点</h4>
              <ul>
                <li v-for="(tip, i) in cat.tips" :key="i">{{ tip }}</li>
              </ul>
            </div>
            <div class="cat-examples">
              <h4>常见物品</h4>
              <div class="example-tags">
                <span v-for="item in cat.examples" :key="item" class="example-tag">{{ item }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 常见误区 -->
      <section class="mistakes-section card">
        <h2>常见分类误区</h2>
        <div class="mistakes-grid">
          <div v-for="(m, i) in mistakes" :key="i" class="mistake-item">
            <div class="mistake-wrong">
              <span class="wrong-icon">✗</span>
              <span>{{ m.wrong }}</span>
            </div>
            <div class="mistake-right">
              <span class="right-icon">✓</span>
              <span>{{ m.right }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const guideData = ref([
  {
    name: '可回收物',
    icon: '♻️',
    color: '#3498db',
    binColor: '#3498db',
    binName: '蓝色',
    description: '适宜回收利用和资源化利用的生活废弃物',
    tips: ['清空内容物', '保持清洁干燥', '压扁后投放节省空间', '大件物品可预约回收'],
    examples: ['塑料瓶', '废纸', '玻璃', '金属', '旧衣物', '电子产品']
  },
  {
    name: '有害垃圾',
    icon: '☠️',
    color: '#e74c3c',
    binColor: '#e74c3c',
    binName: '红色',
    description: '对人体健康或自然环境造成直接或潜在危害的废弃物',
    tips: ['轻放防止破损', '保持完整包装', '电池单独收集', '药品连同包装投放'],
    examples: ['废电池', '废灯管', '过期药品', '油漆', '杀虫剂', '温度计']
  },
  {
    name: '厨余垃圾',
    icon: '🍎',
    color: '#27ae60',
    binColor: '#27ae60',
    binName: '绿色',
    description: '居民日常生活及食品加工等过程中产生的废弃物',
    tips: ['沥干水分', '去除包装', '避免混入杂物', '定时定点投放'],
    examples: ['剩菜剩饭', '果皮果核', '蛋壳', '茶叶渣', '菜叶', '过期食品']
  },
  {
    name: '其他垃圾',
    icon: '🗑️',
    color: '#95a5a6',
    binColor: '#95a5a6',
    binName: '灰色',
    description: '除可回收物、有害垃圾、厨余垃圾以外的其他生活废弃物',
    tips: ['尽量沥干水分', '难以辨别时选此类', '包裹尖锐物品', '不可回收的纸类投此'],
    examples: ['卫生纸', '烟蒂', '陶瓷', '一次性餐具', '尘土', '污染纸张']
  }
])

const mistakes = ref([
  { wrong: '用过的餐巾纸是可回收物', right: '用过的餐巾纸已污染，属于其他垃圾' },
  { wrong: '大骨头是厨余垃圾', right: '大骨头难以降解，属于其他垃圾' },
  { wrong: '椰子壳是厨余垃圾', right: '椰子壳太硬，属于其他垃圾' },
  { wrong: '塑料袋都是可回收物', right: '污染的塑料袋属于其他垃圾' },
  { wrong: '碎玻璃直接扔', right: '碎玻璃需包裹后投放可回收物' },
  { wrong: '过期化妆品是其他垃圾', right: '过期化妆品含化学成分，属于有害垃圾' }
])
</script>

<style scoped>
.page-header { text-align: center; margin-bottom: 40px; }
.page-header h1 { font-size: 32px; margin-bottom: 10px; }
.page-header p { color: var(--text-light); }

.flow-section { margin-bottom: 40px; }
.flow-section h2 { text-align: center; margin-bottom: 30px; font-size: 24px; }
.flow-chart { display: flex; align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap; }
.flow-step { display: flex; align-items: center; gap: 12px; background: var(--bg-light); padding: 16px 20px; border-radius: 12px; }
.step-num { width: 36px; height: 36px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.step-content h4 { font-size: 15px; margin-bottom: 4px; }
.step-content p { font-size: 12px; color: var(--text-light); }
.flow-arrow { font-size: 24px; color: var(--primary); font-weight: bold; }

.detail-section h2 { text-align: center; margin-bottom: 30px; font-size: 24px; }
.detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 40px; }
.detail-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid var(--cat-color); }
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.cat-icon { font-size: 32px; }
.detail-header h3 { font-size: 20px; color: var(--cat-color); }
.cat-desc { color: var(--text-light); font-size: 14px; margin-bottom: 16px; line-height: 1.6; }
.cat-bin { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 14px; }
.bin-color { width: 20px; height: 20px; border-radius: 4px; }
.cat-tips, .cat-examples { margin-bottom: 12px; }
.cat-tips h4, .cat-examples h4 { font-size: 14px; margin-bottom: 8px; color: var(--text-dark); }
.cat-tips ul { padding-left: 20px; }
.cat-tips li { font-size: 13px; color: var(--text-light); margin-bottom: 4px; }
.example-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.example-tag { background: var(--bg-light); padding: 4px 12px; border-radius: 12px; font-size: 12px; color: var(--text-dark); }

.mistakes-section h2 { text-align: center; margin-bottom: 24px; font-size: 24px; }
.mistakes-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.mistake-item { background: var(--bg-light); border-radius: 12px; padding: 16px; }
.mistake-wrong, .mistake-right { display: flex; align-items: center; gap: 10px; font-size: 14px; }
.mistake-wrong { margin-bottom: 10px; color: #e74c3c; }
.mistake-right { color: #27ae60; }
.wrong-icon, .right-icon { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }
.wrong-icon { background: rgba(231,76,60,0.15); }
.right-icon { background: rgba(39,174,96,0.15); }

@media (max-width: 768px) {
  .detail-grid, .mistakes-grid { grid-template-columns: 1fr; }
  .flow-chart { flex-direction: column; }
  .flow-arrow { transform: rotate(90deg); }
}
</style>
