<template>
  <div class="quiz-page">
    <div class="container">
      <!-- 开始界面 -->
      <div v-if="!quizStarted" class="start-screen">
        <div class="start-card">
          <h1>垃圾分类趣味答题</h1>
          <p>测试你的垃圾分类知识，看看能答对多少题！</p>
          <div class="quiz-info">
            <div class="info-item">
              <span class="info-num">{{ questionCount }}</span>
              <span class="info-label">题目数量</span>
            </div>
            <div class="info-item">
              <span class="info-num">30s</span>
              <span class="info-label">每题限时</span>
            </div>
            <div class="info-item">
              <span class="info-num">100</span>
              <span class="info-label">满分</span>
            </div>
          </div>
          <button class="btn btn-primary btn-lg" @click="startQuiz">开始答题</button>
        </div>
      </div>

      <!-- 答题界面 -->
      <div v-else-if="!quizFinished" class="quiz-screen">
        <div class="quiz-header">
          <div class="progress-info">
            <span>第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
          </div>
          <div class="timer" :class="{ warning: timeLeft <= 10 }">
            {{ timeLeft }}s
          </div>
          <div class="score-info">
            <span class="correct">对 {{ correctCount }}</span>
            <span class="wrong">错 {{ wrongCount }}</span>
          </div>
        </div>

        <div class="question-card">
          <h2 class="question-text">{{ currentQuestion.question }}</h2>
          <div class="options">
            <button
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              class="option-btn"
              :class="getOptionClass(index)"
              :disabled="answered"
              @click="selectAnswer(index)"
            >
              <span class="option-letter">{{ ['A', 'B', 'C', 'D'][index] }}</span>
              <span class="option-text">{{ option }}</span>
            </button>
          </div>
        </div>

        <div v-if="answered" class="feedback" :class="isCorrect ? 'correct' : 'wrong'">
          <p>{{ isCorrect ? '回答正确！' : '回答错误！' }}</p>
          <p v-if="!isCorrect">正确答案：{{ ['A', 'B', 'C', 'D'][currentQuestion.answerIndex] }}. {{ currentQuestion.answer }}</p>
          <p class="explanation">{{ currentQuestion.explanation }}</p>
          <button class="btn btn-primary" @click="nextQuestion">
            {{ currentIndex < questions.length - 1 ? '下一题' : '查看结果' }}
          </button>
        </div>
      </div>

      <!-- 结果界面 -->
      <div v-else class="result-screen">
        <div class="result-card">
          <div class="result-icon">{{ score >= 60 ? '🎉' : '💪' }}</div>
          <h1>答题结束</h1>
          <div class="score-display">
            <span class="score-num">{{ score }}</span>
            <span class="score-unit">分</span>
          </div>
          <div class="result-stats">
            <div class="stat-item correct">
              <span class="stat-num">{{ correctCount }}</span>
              <span class="stat-label">答对</span>
            </div>
            <div class="stat-item wrong">
              <span class="stat-num">{{ wrongCount }}</span>
              <span class="stat-label">答错</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">{{ accuracy }}%</span>
              <span class="stat-label">正确率</span>
            </div>
          </div>
          <p class="result-msg">{{ getResultMessage() }}</p>
          <button class="btn btn-primary btn-lg" @click="restartQuiz">再来一次</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, onMounted } from 'vue'

const API_BASE = 'http://localhost:5000/api'

const questionCount = ref(10)
const totalQuestions = ref(100)
const quizStarted = ref(false)
const quizFinished = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const correctCount = ref(0)
const wrongCount = ref(0)
const timeLeft = ref(30)
const answered = ref(false)
const selectedAnswer = ref(null)
const isCorrect = ref(false)
const loading = ref(false)
let timer = null

const currentQuestion = computed(() => {
  const q = questions.value[currentIndex.value]
  if (!q) return {}
  // 转换答案格式：从文字答案转为索引
  const answerIndex = q.options.indexOf(q.answer)
  return { ...q, answerIndex: answerIndex >= 0 ? answerIndex : 0 }
})
const score = computed(() => questions.value.length > 0 ? Math.round(correctCount.value / questions.value.length * 100) : 0)
const accuracy = computed(() => {
  const total = correctCount.value + wrongCount.value
  return total > 0 ? Math.round(correctCount.value / total * 100) : 0
})

// 从API获取题目
const fetchQuestions = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/quiz/questions?limit=${questionCount.value}`)
    const data = await response.json()
    if (data.success && data.data.length > 0) {
      questions.value = data.data
      return true
    }
  } catch (error) {
    console.error('获取题目失败:', error)
  }
  loading.value = false
  return false
}

const startQuiz = async () => {
  loading.value = true
  const success = await fetchQuestions()
  loading.value = false
  
  if (!success || questions.value.length === 0) {
    alert('获取题目失败，请确保后端服务已启动')
    return
  }
  
  currentIndex.value = 0
  correctCount.value = 0
  wrongCount.value = 0
  quizStarted.value = true
  quizFinished.value = false
  startTimer()
}

onMounted(async () => {
  // 获取题库总数
  try {
    const response = await fetch(`${API_BASE}/stats`)
    const data = await response.json()
    if (data.success && data.data.quizCount) {
      totalQuestions.value = data.data.quizCount
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  }
})

const startTimer = () => {
  timeLeft.value = 30
  answered.value = false
  selectedAnswer.value = null
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      handleTimeout()
    }
  }, 1000)
}

const handleTimeout = () => {
  answered.value = true
  isCorrect.value = false
  wrongCount.value++
}

const selectAnswer = (index) => {
  if (answered.value) return
  clearInterval(timer)
  selectedAnswer.value = index
  answered.value = true
  // 使用answerIndex来判断正确性
  isCorrect.value = index === currentQuestion.value.answerIndex
  if (isCorrect.value) {
    correctCount.value++
  } else {
    wrongCount.value++
  }
}

const getOptionClass = (index) => {
  if (!answered.value) return ''
  if (index === currentQuestion.value.answerIndex) return 'correct'
  if (index === selectedAnswer.value && !isCorrect.value) return 'wrong'
  return 'disabled'
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    startTimer()
  } else {
    quizFinished.value = true
    clearInterval(timer)
  }
}

const restartQuiz = () => {
  quizStarted.value = false
  quizFinished.value = false
}

const getResultMessage = () => {
  if (score.value >= 90) return '太棒了！你是垃圾分类达人！'
  if (score.value >= 70) return '不错哦！继续加油！'
  if (score.value >= 60) return '及格了，还需要多学习！'
  return '要多多学习垃圾分类知识哦！'
}

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.start-screen, .result-screen { display: flex; justify-content: center; align-items: center; min-height: 70vh; }
.start-card, .result-card { background: white; border-radius: 20px; padding: 50px; text-align: center; max-width: 500px; width: 100%; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
.start-card h1, .result-card h1 { font-size: 28px; margin-bottom: 16px; color: var(--text-dark); }
.start-card p { color: var(--text-light); margin-bottom: 30px; }
.quiz-info { display: flex; justify-content: center; gap: 30px; margin-bottom: 30px; }
.info-item { text-align: center; }
.info-num { display: block; font-size: 28px; font-weight: bold; color: var(--primary); }
.info-label { font-size: 13px; color: var(--text-light); }
.btn-lg { padding: 14px 40px; font-size: 16px; }

.quiz-screen { max-width: 700px; margin: 0 auto; }
.quiz-header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 24px; border-radius: 12px; margin-bottom: 20px; }
.timer { font-size: 24px; font-weight: bold; color: var(--primary); padding: 8px 20px; background: rgba(102,126,234,0.1); border-radius: 20px; }
.timer.warning { color: #e74c3c; background: rgba(231,76,60,0.1); }
.score-info { display: flex; gap: 16px; }
.score-info .correct { color: #27ae60; font-weight: bold; }
.score-info .wrong { color: #e74c3c; font-weight: bold; }

.question-card { background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; }
.question-text { font-size: 20px; margin-bottom: 24px; color: var(--text-dark); line-height: 1.5; }
.options { display: flex; flex-direction: column; gap: 12px; }
.option-btn { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border: 2px solid var(--border); border-radius: 12px; background: white; cursor: pointer; transition: all 0.2s; text-align: left; font-size: 15px; }
.option-btn:hover:not(:disabled) { border-color: var(--primary); background: rgba(102,126,234,0.05); }
.option-btn:disabled { cursor: not-allowed; opacity: 0.7; }
.option-btn.correct { border-color: #27ae60; background: rgba(39,174,96,0.1); }
.option-btn.wrong { border-color: #e74c3c; background: rgba(231,76,60,0.1); }
.option-letter { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: var(--bg-light); border-radius: 8px; font-weight: bold; color: var(--primary); }

.feedback { background: white; border-radius: 12px; padding: 24px; text-align: center; }
.feedback.correct { border: 2px solid #27ae60; }
.feedback.wrong { border: 2px solid #e74c3c; }
.feedback p { margin-bottom: 12px; }
.explanation { color: var(--text-light); font-size: 14px; margin-bottom: 20px; }

.result-icon { font-size: 60px; margin-bottom: 16px; }
.score-display { margin: 24px 0; }
.score-num { font-size: 64px; font-weight: bold; color: var(--primary); }
.score-unit { font-size: 24px; color: var(--text-light); }
.result-stats { display: flex; justify-content: center; gap: 40px; margin: 30px 0; }
.stat-item { text-align: center; }
.stat-item .stat-num { display: block; font-size: 28px; font-weight: bold; }
.stat-item.correct .stat-num { color: #27ae60; }
.stat-item.wrong .stat-num { color: #e74c3c; }
.stat-label { font-size: 13px; color: var(--text-light); }
.result-msg { color: var(--text-light); margin-bottom: 24px; }
</style>
