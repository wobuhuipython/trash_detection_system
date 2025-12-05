<template>
  <div class="feedback-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>模型质量反馈</h1>
      <p>查看检测历史记录，对检测结果进行反馈评价</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_feedback || 0 }}</div>
        <div class="stat-label">总反馈数</div>
      </div>
      <div class="stat-card correct">
        <div class="stat-value">{{ stats.accuracy_rate || 0 }}%</div>
        <div class="stat-label">检测准确率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.correct_count || 0 }}</div>
        <div class="stat-label">正确检测</div>
      </div>
      <div class="stat-card incorrect">
        <div class="stat-value">{{ stats.incorrect_count || 0 }}</div>
        <div class="stat-label">错误检测</div>
      </div>
      <div class="stat-card satisfaction">
        <div class="stat-value">{{ stats.avg_satisfaction || 0 }}</div>
        <div class="stat-label">平均满意度</div>
      </div>
    </div>

    <!-- 检测历史记录 -->
    <div class="detection-history-section">
      <div class="section-header">
        <h2>检测历史记录</h2>
        <button class="refresh-btn" @click="fetchDetectionHistory">刷新</button>
      </div>
      
      <div class="history-list" v-if="detectionHistory.length > 0">
        <div 
          v-for="record in detectionHistory" 
          :key="record.id" 
          class="history-item"
        >
          <div class="history-info">
            <div class="history-time">{{ record.detection_time }}</div>
            <div class="history-results">
              <span 
                v-for="(result, idx) in getFormattedResults(record)" 
                :key="idx"
                class="result-tag"
                :class="getCategoryClass(result.category)"
              >
                {{ result.name }} - {{ result.category }}
                <span class="confidence" v-if="result.confidence">
                  ({{ (result.confidence * 100).toFixed(1) }}%)
                </span>
              </span>
            </div>
            <div class="history-meta">
              <span>来源: {{ getSourceLabel(record.source_type) }}</span>
              <span v-if="record.processing_time">耗时: {{ record.processing_time.toFixed(2) }}秒</span>
            </div>
          </div>
          <div class="history-actions">
            <button 
              v-if="!isFeedbacked(record.id)"
              class="feedback-btn"
              @click="openFeedbackModal(record)"
            >
              提交反馈
            </button>
            <span v-else class="feedbacked-badge">已反馈</span>
          </div>
        </div>
      </div>
      <div class="empty-state" v-else>
        暂无检测历史记录
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 左侧：分类准确率统计 -->
      <div class="stats-section">
        <h2>分类准确率统计</h2>
        <div class="category-stats" v-if="stats.category_stats && stats.category_stats.length > 0">
          <div 
            v-for="item in stats.category_stats" 
            :key="item.category" 
            class="category-item"
          >
            <div class="category-header">
              <span class="category-name">{{ item.category }}</span>
              <span class="category-accuracy">{{ item.accuracy }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: item.accuracy + '%' }"
                :class="getAccuracyClass(item.accuracy)"
              ></div>
            </div>
            <div class="category-detail">
              共 {{ item.total }} 次检测，正确 {{ item.correct }} 次
            </div>
          </div>
        </div>
        <div class="empty-stats" v-else>暂无统计数据</div>
      </div>

      <!-- 右侧：满意度分布 + 最近反馈 -->
      <div class="stats-section">
        <h2>满意度分布</h2>
        <div class="satisfaction-stats">
          <div 
            v-for="score in [5, 4, 3, 2, 1]" 
            :key="score" 
            class="satisfaction-item"
          >
            <span class="score-label">{{ score }}星</span>
            <div class="bar-container">
              <div 
                class="bar-fill" 
                :style="{ width: getSatisfactionWidth(stats.satisfaction_distribution?.[score] || 0) + '%' }"
              ></div>
            </div>
            <span class="count-label">{{ stats.satisfaction_distribution?.[score] || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近反馈列表 -->
    <div class="feedback-list-section">
      <h2>最近反馈记录</h2>
      <div class="feedback-list" v-if="feedbackList.length > 0">
        <div 
          v-for="item in feedbackList" 
          :key="item.id" 
          class="feedback-item"
          :class="{ correct: item.is_correct, incorrect: !item.is_correct }"
        >
          <div class="feedback-main">
            <span class="garbage-name">{{ item.garbage_name }}</span>
            <span class="arrow">→</span>
            <span class="predicted">{{ item.predicted_category }}</span>
            <span class="result-badge" :class="item.is_correct ? 'correct' : 'incorrect'">
              {{ item.is_correct ? '正确' : '错误' }}
            </span>
            <span v-if="!item.is_correct && item.correct_category" class="correction">
              (应为: {{ item.correct_category }})
            </span>
          </div>
          <div class="feedback-meta">
            <span class="satisfaction-stars" v-if="item.satisfaction">
              {{ '★'.repeat(item.satisfaction) }}{{ '☆'.repeat(5 - item.satisfaction) }}
            </span>
            <span class="time">{{ item.feedback_time }}</span>
          </div>
          <div class="feedback-comment" v-if="item.feedback_comment">
            {{ item.feedback_comment }}
          </div>
          <button class="delete-feedback-btn" @click="deleteFeedback(item.id)">删除</button>
        </div>
      </div>
      <div class="empty-state" v-else>
        暂无反馈记录
      </div>
    </div>

    <!-- 反馈弹窗 -->
    <div class="modal-overlay" v-if="showFeedbackModal" @click.self="closeFeedbackModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>提交检测反馈</h3>
          <button class="close-btn" @click="closeFeedbackModal">×</button>
        </div>
        <div class="modal-body">
          <div class="selected-record" v-if="selectedRecord">
            <div class="record-time">检测时间: {{ selectedRecord.detection_time }}</div>
            <div class="record-results">
              检测结果:
              <span 
                v-for="(result, idx) in formattedSelectedResults" 
                :key="idx"
                class="result-tag small"
              >
                {{ result.name }} - {{ result.category }}
              </span>
            </div>
          </div>
          
          <div class="form-group">
            <label>选择要反馈的检测项</label>
            <select v-model="feedbackForm.selectedResultIndex">
              <option value="">请选择</option>
              <option 
                v-for="(result, idx) in formattedSelectedResults" 
                :key="idx"
                :value="idx"
              >
                {{ result.name }} - {{ result.category }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>检测结果是否正确？</label>
            <div class="radio-group">
              <label class="radio-item">
                <input type="radio" v-model="feedbackForm.is_correct" :value="true" />
                <span class="radio-label correct">正确</span>
              </label>
              <label class="radio-item">
                <input type="radio" v-model="feedbackForm.is_correct" :value="false" />
                <span class="radio-label incorrect">错误</span>
              </label>
            </div>
          </div>
          
          <div class="form-group" v-if="!feedbackForm.is_correct">
            <label>正确的分类应该是</label>
            <select v-model="feedbackForm.correct_category">
              <option value="">请选择正确分类</option>
              <option value="塑料瓶">塑料瓶 (可回收物)</option>
              <option value="电池">电池 (有害垃圾)</option>
              <option value="塑料袋">塑料袋 (其他垃圾)</option>
              <option value="玻璃">玻璃 (可回收物)</option>
              <option value="金属罐">金属罐 (可回收物)</option>
              <option value="湿垃圾">湿垃圾 (厨余垃圾)</option>
              <option value="碎玻璃">碎玻璃 (可回收物)</option>
              <option value="盒子">盒子 (可回收物)</option>
              <option value="其他">其他 (模型未识别)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>满意度评分</label>
            <div class="satisfaction-rating">
              <span 
                v-for="i in 5" 
                :key="i" 
                class="star"
                :class="{ active: feedbackForm.satisfaction >= i }"
                @click="feedbackForm.satisfaction = i"
              >★</span>
            </div>
          </div>
          
          <div class="form-group">
            <label>反馈意见（可选）</label>
            <textarea v-model="feedbackForm.feedback_comment" placeholder="请输入您的意见或建议..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeFeedbackModal">取消</button>
          <button class="submit-btn" @click="submitFeedback" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const API_BASE = 'http://localhost:5000/api'

const stats = ref({
  total_feedback: 0,
  correct_count: 0,
  incorrect_count: 0,
  accuracy_rate: 0,
  avg_satisfaction: 0,
  category_stats: [],
  satisfaction_distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  daily_trend: []
})

const detectionHistory = ref([])
const feedbackList = ref([])
const feedbackedIds = ref([])  // 已反馈的检测记录ID
const submitting = ref(false)
const showFeedbackModal = ref(false)
const selectedRecord = ref(null)

const feedbackForm = ref({
  selectedResultIndex: '',
  is_correct: true,
  correct_category: '',
  satisfaction: 0,
  feedback_comment: ''
})

// 垃圾分类映射表（8个垃圾类别）
const garbageMapping = {
  "Plastic Bottle": { name: "塑料瓶", category: "可回收物" },
  "Battery": { name: "电池", category: "有害垃圾" },
  "Plastic Bag": { name: "塑料袋", category: "其他垃圾" },
  "Glass": { name: "玻璃", category: "可回收物" },
  "Can": { name: "金属罐", category: "可回收物" },
  "Wet Garbage": { name: "湿垃圾", category: "厨余垃圾" },
  "Broken Glass": { name: "碎玻璃", category: "可回收物" },
  "Box": { name: "盒子", category: "可回收物" },
  // 兼容旧格式
  "Broken_Glass": { name: "碎玻璃", category: "可回收物" },
}

// 格式化检测结果（兼容新旧数据格式）
const getFormattedResults = (record) => {
  if (!record || !record.detection_results) return []
  
  return record.detection_results.map((result, idx) => {
    // 新格式：已有name和category
    if (result.name && result.category) {
      return {
        name: result.name,
        category: result.category,
        confidence: result.confidence || (record.confidence_scores && record.confidence_scores[idx]) || 0
      }
    }
    // 旧格式：只有class
    const className = result.class || result
    const mapping = garbageMapping[className] || { name: className, category: '未知分类' }
    return {
      name: mapping.name,
      category: mapping.category,
      confidence: result.confidence || (record.confidence_scores && record.confidence_scores[idx]) || 0
    }
  })
}

// 计算属性：格式化选中记录的结果
const formattedSelectedResults = computed(() => {
  if (!selectedRecord.value) return []
  return getFormattedResults(selectedRecord.value)
})

// 获取检测历史记录
const fetchDetectionHistory = async () => {
  try {
    const response = await fetch(`${API_BASE}/detection/history?limit=20`)
    const data = await response.json()
    if (data.success) {
      detectionHistory.value = data.data
    }
  } catch (error) {
    console.error('获取检测历史失败:', error)
  }
}

// 获取已反馈的检测记录ID
const fetchFeedbackedIds = async () => {
  try {
    const response = await fetch(`${API_BASE}/feedback/detection-ids`)
    const data = await response.json()
    if (data.success) {
      feedbackedIds.value = data.data
    }
  } catch (error) {
    console.error('获取已反馈ID失败:', error)
  }
}

// 检查是否已反馈
const isFeedbacked = (detectionId) => {
  return feedbackedIds.value.includes(detectionId)
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/feedback/stats`)
    const data = await response.json()
    if (data.success && data.data) {
      stats.value = data.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取反馈列表
const fetchFeedbackList = async () => {
  try {
    const response = await fetch(`${API_BASE}/feedback/list?limit=20`)
    const data = await response.json()
    if (data.success) {
      feedbackList.value = data.data
    }
  } catch (error) {
    console.error('获取反馈列表失败:', error)
  }
}

// 打开反馈弹窗
const openFeedbackModal = (record) => {
  selectedRecord.value = record
  feedbackForm.value = {
    selectedResultIndex: '',
    is_correct: true,
    correct_category: '',
    satisfaction: 0,
    feedback_comment: ''
  }
  showFeedbackModal.value = true
}

// 关闭反馈弹窗
const closeFeedbackModal = () => {
  showFeedbackModal.value = false
  selectedRecord.value = null
}

// 提交反馈
const submitFeedback = async () => {
  if (feedbackForm.value.selectedResultIndex === '') {
    alert('请选择要反馈的检测项')
    return
  }
  
  // 使用格式化后的结果
  const selectedResult = formattedSelectedResults.value[feedbackForm.value.selectedResultIndex]
  
  if (!selectedResult || !selectedResult.name || !selectedResult.category) {
    alert('检测项数据异常，请重新选择')
    return
  }
  
  submitting.value = true
  try {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        detection_id: selectedRecord.value.id,
        garbage_name: selectedResult.name,
        predicted_category: selectedResult.category,
        is_correct: feedbackForm.value.is_correct,
        correct_category: feedbackForm.value.correct_category || null,
        satisfaction: feedbackForm.value.satisfaction || null,
        feedback_comment: feedbackForm.value.feedback_comment || null
      })
    })
    const data = await response.json()
    
    if (data.success) {
      alert('反馈提交成功！')
      closeFeedbackModal()
      fetchStats()
      fetchFeedbackList()
      fetchFeedbackedIds()
    } else {
      alert(data.message || '提交失败')
    }
  } catch (error) {
    console.error('提交反馈失败:', error)
    alert('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 获取分类样式类
const getCategoryClass = (category) => {
  const classMap = {
    '可回收物': 'recyclable',
    '有害垃圾': 'hazardous',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return classMap[category] || ''
}

// 获取来源标签
const getSourceLabel = (sourceType) => {
  const labelMap = {
    'upload': '图片上传',
    'camera': '摄像头',
    'manual_save': '手动保存'
  }
  return labelMap[sourceType] || sourceType
}

// 获取准确率对应的样式类
const getAccuracyClass = (accuracy) => {
  if (accuracy >= 80) return 'high'
  if (accuracy >= 60) return 'medium'
  return 'low'
}

// 计算满意度条宽度
const getSatisfactionWidth = (count) => {
  const dist = stats.value.satisfaction_distribution || {}
  const total = Object.values(dist).reduce((a, b) => a + b, 0)
  return total > 0 ? (count / total) * 100 : 0
}

// 删除反馈记录
const deleteFeedback = async (feedbackId) => {
  if (!confirm('确定要删除这条反馈记录吗？删除后可以重新反馈对应的检测记录。')) {
    return
  }
  try {
    const response = await fetch(`${API_BASE}/feedback/${feedbackId}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.success) {
      alert('删除成功')
      fetchFeedbackList()
      fetchFeedbackedIds()
      fetchStats()
    } else {
      alert(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除反馈失败:', error)
    alert('删除失败')
  }
}

onMounted(() => {
  fetchDetectionHistory()
  fetchFeedbackedIds()
  fetchStats()
  fetchFeedbackList()
})
</script>


<style scoped>
.feedback-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 16px;
}

/* 统计概览 */
.stats-overview {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 150px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-card.correct { background: linear-gradient(135deg, #d4edda, #c3e6cb); }
.stat-card.incorrect { background: linear-gradient(135deg, #f8d7da, #f5c6cb); }
.stat-card.satisfaction { background: linear-gradient(135deg, #fff3cd, #ffeeba); }

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

/* 检测历史记录 */
.detection-history-section {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.refresh-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover {
  background: #5a6fd6;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  border: 1px solid #eee;
}

.history-info {
  flex: 1;
}

.history-time {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.history-results {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.result-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.result-tag.small {
  padding: 4px 10px;
  font-size: 13px;
}

.result-tag.recyclable { background: #e3f2fd; color: #1976d2; }
.result-tag.hazardous { background: #ffebee; color: #c62828; }
.result-tag.kitchen { background: #e8f5e9; color: #2e7d32; }
.result-tag.other { background: #f5f5f5; color: #616161; }

.confidence {
  font-size: 12px;
  opacity: 0.8;
}

.history-meta {
  font-size: 13px;
  color: #999;
  display: flex;
  gap: 15px;
}

.feedback-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #4CAF50, #8BC34A);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: transform 0.2s;
}

.feedback-btn:hover {
  transform: scale(1.05);
}

/* 主要内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .main-content { grid-template-columns: 1fr; }
}

.stats-section {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stats-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.category-stats { margin-bottom: 20px; }

.category-item { margin-bottom: 15px; }

.category-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.category-name { font-weight: 500; color: #333; }
.category-accuracy { font-weight: bold; color: #4CAF50; }

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-fill.high { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
.progress-fill.medium { background: linear-gradient(90deg, #FFC107, #FFEB3B); }
.progress-fill.low { background: linear-gradient(90deg, #f44336, #FF5722); }

.category-detail {
  font-size: 12px;
  color: #999;
  margin-top: 3px;
}

.empty-stats {
  text-align: center;
  padding: 30px;
  color: #999;
}

/* 满意度分布 */
.satisfaction-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.satisfaction-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-label { width: 40px; font-size: 14px; color: #666; }

.bar-container {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffc107, #ff9800);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.count-label {
  width: 30px;
  text-align: right;
  font-size: 14px;
  color: #666;
}

/* 反馈列表 */
.feedback-list-section {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.feedback-list-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feedback-item {
  padding: 15px;
  border-radius: 8px;
  background: #f9f9f9;
  border-left: 4px solid #ddd;
}

.feedback-item.correct { border-left-color: #28a745; }
.feedback-item.incorrect { border-left-color: #dc3545; }

.feedback-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.garbage-name { font-weight: 500; color: #333; }
.arrow { color: #999; }
.predicted { color: #666; }

.result-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.result-badge.correct { background: #d4edda; color: #155724; }
.result-badge.incorrect { background: #f8d7da; color: #721c24; }

.correction { color: #dc3545; font-size: 13px; }

.feedback-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 13px;
  color: #999;
}

.satisfaction-stars { color: #ffc107; }

.feedback-comment {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #eee;
  font-size: 13px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.close-btn:hover { color: #333; }

.modal-body { padding: 20px; }

.selected-record {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.record-time {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.record-results {
  font-size: 14px;
  color: #333;
}

.form-group { margin-bottom: 20px; }

.form-group label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-item input { margin-right: 8px; }
.radio-label.correct { color: #28a745; font-weight: 500; }
.radio-label.incorrect { color: #dc3545; font-weight: 500; }

.satisfaction-rating {
  display: flex;
  gap: 8px;
}

.star {
  font-size: 28px;
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s;
}

.star:hover,
.star.active { color: #ffc107; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 12px 24px;
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover { background: #eee; }

.submit-btn {
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.submit-btn:hover:not(:disabled) { background: #45a049; }
.submit-btn:disabled { background: #ccc; cursor: not-allowed; }

.feedbacked-badge {
  display: inline-block;
  padding: 10px 20px;
  background: #e0e0e0;
  color: #666;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.delete-feedback-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  background: #ff5252;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.feedback-item {
  position: relative;
}

.feedback-item:hover .delete-feedback-btn {
  opacity: 1;
}

.delete-feedback-btn:hover {
  background: #d32f2f;
}
</style>
