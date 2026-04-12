<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>统计分析</h1>
        <p class="sub-title">管理员查看活动报名、签到率、热度和时段分析</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <h2>活动报名人数对比</h2>
        <canvas id="registrationChart"></canvas>
      </div>

      <div class="chart-card">
        <h2>活动签到率统计</h2>
        <canvas id="attendanceChart"></canvas>
      </div>

      <div class="chart-card">
        <h2>活动热度排行</h2>
        <canvas id="hotChart"></canvas>
      </div>

      <div class="chart-card">
        <h2>活动时段分析</h2>
        <canvas id="timeSlotChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { API_BASE_URL } from '../config'

const router = useRouter()
const message = ref('')

let registrationChartInstance = null
let attendanceChartInstance = null
let hotChartInstance = null
let timeSlotChartInstance = null

const goHome = () => {
  router.push('/home')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

const loadRegistrationChart = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/charts/registrations`)
    const ctx = document.getElementById('registrationChart')

    if (registrationChartInstance) {
      registrationChartInstance.destroy()
    }

    registrationChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: res.data.titles,
        datasets: [
          {
            label: '报名人数',
            data: res.data.registration_counts
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  } catch (error) {
    message.value = '加载报名人数图表失败'
  }
}

const loadAttendanceChart = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/charts/attendance`)
    const ctx = document.getElementById('attendanceChart')

    if (attendanceChartInstance) {
      attendanceChartInstance.destroy()
    }

    attendanceChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: res.data.titles,
        datasets: [
          {
            label: '签到率(%)',
            data: res.data.attendance_rates
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  } catch (error) {
    message.value = '加载签到率图表失败'
  }
}

const loadHotChart = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/charts/hot`)
    const ctx = document.getElementById('hotChart')

    if (hotChartInstance) {
      hotChartInstance.destroy()
    }

    hotChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: res.data.titles,
        datasets: [
          {
            label: '热度值',
            data: res.data.heats
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  } catch (error) {
    message.value = '加载热度图表失败'
  }
}

const loadTimeSlotChart = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/charts/time-slots`)
    const ctx = document.getElementById('timeSlotChart')

    if (timeSlotChartInstance) {
      timeSlotChartInstance.destroy()
    }

    timeSlotChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: res.data.labels,
        datasets: [
          {
            label: '活动数量',
            data: res.data.counts
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  } catch (error) {
    message.value = '加载时段分析图表失败'
  }
}

onMounted(async () => {
  const role = localStorage.getItem('role')
  if (role !== 'admin') {
    router.push('/login')
    return
  }

  await loadRegistrationChart()
  await loadAttendanceChart()
  await loadHotChart()
  await loadTimeSlotChart()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30px;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  color: #333;
}

.sub-title {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  color: white;
  cursor: pointer;
}

.gray-btn {
  background: #909399;
}
.gray-btn:hover {
  background: #a6a9ad;
}

.red-btn {
  background: #f56c6c;
}
.red-btn:hover {
  background: #f78989;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  height: 420px;
  display: flex;
  flex-direction: column;
}

.chart-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
  font-size: 20px;
}

.chart-card canvas {
  flex: 1;
}

@media (max-width: 1100px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>