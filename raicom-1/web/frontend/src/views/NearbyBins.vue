<template>
  <div class="nearby-page">
    <div class="container">
      <div class="page-header">
        <h1>附近垃圾桶</h1>
        <p>查找您附近的垃圾投放点</p>
      </div>

      <!-- 搜索和定位 -->
      <div class="search-bar">
        <button class="btn btn-primary locate-btn" @click="getCurrentLocation" :disabled="locating">
          {{ locating ? '定位中...' : '重新定位' }}
        </button>
        <input 
          v-model="searchKeyword" 
          placeholder="搜索地点..." 
          class="search-input"
          @keyup.enter="searchLocation"
        />
        <button class="btn btn-primary" @click="searchLocation">搜索</button>
      </div>

      <!-- 当前位置 -->
      <div class="location-info" v-if="currentAddress">
        当前位置：{{ currentAddress }}
      </div>

      <!-- 地图容器 -->
      <div id="map-container" class="map-container"></div>

      <!-- 附近垃圾桶列表 -->
      <div class="bins-section">
        <h2>附近的垃圾投放点 ({{ bins.length }}个)</h2>
        <div class="bins-list" v-if="bins.length > 0">
          <div 
            v-for="(bin, index) in bins" 
            :key="index" 
            class="bin-card"
            @click="focusOnBin(bin)"
          >
            <div class="bin-icon">🗑️</div>
            <div class="bin-info">
              <h3>{{ bin.name }}</h3>
              <p class="bin-address">{{ bin.address }}</p>
              <p class="bin-distance">距离：{{ bin.distance }}米</p>
            </div>
            <button class="nav-btn" @click.stop="navigateTo(bin)">导航</button>
          </div>
        </div>
        <div class="empty-state" v-else-if="!loading">
          <p>{{ searchError || '暂未找到附近的垃圾投放点' }}</p>
        </div>
        <div class="loading-state" v-if="loading">
          <p>正在搜索附近垃圾桶...</p>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const API_BASE = 'http://localhost:5000/api'
const AMAP_JS_KEY = '1645e8700725afc2b2dc1b75e2892ed3'
const AMAP_SECURITY_KEY = '9493e81885fab6c2cb2e42e7bb12505'

const bins = ref([])
const loading = ref(false)
const locating = ref(false)
const searchKeyword = ref('')
const currentAddress = ref('')
const searchError = ref('')
const currentLng = ref(116.397428)
const currentLat = ref(39.90923)

let map = null
let markers = []
let currentMarker = null

// 加载高德地图JS API
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      resolve()
      return
    }
    
    // 设置安全密钥
    window._AMapSecurityConfig = {
      securityJsCode: AMAP_SECURITY_KEY
    }
    
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_JS_KEY}`
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

// 初始化地图
const initMap = async () => {
  try {
    await loadAMapScript()
    map = new window.AMap.Map('map-container', {
      zoom: 15,
      center: [currentLng.value, currentLat.value]
    })
    getCurrentLocation()
  } catch (error) {
    console.error('地图加载失败:', error)
    searchError.value = '地图加载失败，请刷新页面重试'
  }
}

// 获取当前位置
const getCurrentLocation = () => {
  locating.value = true
  searchError.value = ''
  
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        currentLng.value = position.coords.longitude
        currentLat.value = position.coords.latitude
        
        if (map) {
          map.setCenter([currentLng.value, currentLat.value])
          updateCurrentMarker()
        }
        
        // 逆地理编码获取地址
        await getAddressFromLocation()
        // 搜索附近垃圾桶
        await searchNearbyBins()
        locating.value = false
      },
      (error) => {
        console.error('定位失败:', error)
        searchError.value = '定位失败，请检查位置权限或手动搜索'
        locating.value = false
        // 使用默认位置搜索
        searchNearbyBins()
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  } else {
    searchError.value = '浏览器不支持定位功能'
    locating.value = false
  }
}

// 更新当前位置标记
const updateCurrentMarker = () => {
  if (currentMarker) {
    currentMarker.setMap(null)
  }
  currentMarker = new window.AMap.Marker({
    position: [currentLng.value, currentLat.value],
    title: '我的位置',
    icon: new window.AMap.Icon({
      size: new window.AMap.Size(32, 32),
      image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
    })
  })
  currentMarker.setMap(map)
}

// 逆地理编码
const getAddressFromLocation = async () => {
  try {
    const response = await fetch(
      `${API_BASE}/amap/regeo?lng=${currentLng.value}&lat=${currentLat.value}`
    )
    const data = await response.json()
    if (data.success) {
      currentAddress.value = data.address
    }
  } catch (error) {
    console.error('获取地址失败:', error)
  }
}

// 搜索附近垃圾桶
const searchNearbyBins = async () => {
  loading.value = true
  bins.value = []
  clearMarkers()
  
  try {
    const response = await fetch(
      `${API_BASE}/amap/nearby?lng=${currentLng.value}&lat=${currentLat.value}&keyword=垃圾`
    )
    const data = await response.json()
    
    if (data.success && data.data.length > 0) {
      bins.value = data.data
      addBinMarkers()
    } else {
      searchError.value = '附近暂未找到垃圾投放点'
    }
  } catch (error) {
    console.error('搜索失败:', error)
    searchError.value = '搜索失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 搜索地点
const searchLocation = async () => {
  if (!searchKeyword.value.trim()) return
  
  loading.value = true
  try {
    const response = await fetch(
      `${API_BASE}/amap/geocode?address=${encodeURIComponent(searchKeyword.value)}`
    )
    const data = await response.json()
    
    if (data.success && data.lng && data.lat) {
      currentLng.value = data.lng
      currentLat.value = data.lat
      currentAddress.value = data.address || searchKeyword.value
      
      if (map) {
        map.setCenter([currentLng.value, currentLat.value])
        updateCurrentMarker()
      }
      await searchNearbyBins()
    } else {
      searchError.value = '未找到该地点'
    }
  } catch (error) {
    console.error('搜索地点失败:', error)
    searchError.value = '搜索失败'
  } finally {
    loading.value = false
  }
}

// 添加垃圾桶标记
const addBinMarkers = () => {
  bins.value.forEach((bin, index) => {
    const marker = new window.AMap.Marker({
      position: [bin.lng, bin.lat],
      title: bin.name,
      label: {
        content: `<div class="marker-label">${index + 1}</div>`,
        direction: 'top'
      }
    })
    marker.on('click', () => focusOnBin(bin))
    marker.setMap(map)
    markers.push(marker)
  })
}

// 清除标记
const clearMarkers = () => {
  markers.forEach(m => m.setMap(null))
  markers = []
}

// 聚焦到某个垃圾桶
const focusOnBin = (bin) => {
  if (map) {
    map.setCenter([bin.lng, bin.lat])
    map.setZoom(17)
  }
}

// 导航到垃圾桶
const navigateTo = (bin) => {
  const url = `https://uri.amap.com/navigation?to=${bin.lng},${bin.lat},${encodeURIComponent(bin.name)}&mode=walk&callnative=1`
  window.open(url, '_blank')
}

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})
</script>


<style scoped>
.nearby-page {
  padding-bottom: 40px;
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
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
  background: white;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.locate-btn {
  white-space: nowrap;
}

.location-info {
  background: #e8f5e9;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 15px;
  color: #2e7d32;
  font-size: 14px;
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.bins-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.bins-section h2 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #333;
}

.bins-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bin-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.bin-card:hover {
  background: #f0f0f0;
  transform: translateX(5px);
}

.bin-icon {
  font-size: 32px;
}

.bin-info {
  flex: 1;
}

.bin-info h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 4px;
}

.bin-address {
  font-size: 13px;
  color: #666;
  margin-bottom: 2px;
}

.bin-distance {
  font-size: 12px;
  color: #27ae60;
  font-weight: 500;
}

.nav-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: transform 0.2s;
}

.nav-btn:hover {
  transform: scale(1.05);
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

:deep(.marker-label) {
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .search-bar {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
  
  .map-container {
    height: 300px;
  }
}
</style>
