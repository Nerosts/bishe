<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动列表</h1>
        <p class="sub-title">欢迎你，{{ username }}（{{ roleText }}）</p>
      </div>

      <div class="top-buttons">
        <button
          v-if="role === 'student'"
          class="green-btn"
          @click="goMyRegistrations"
        >
          我的报名
        </button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="filter-bar">
      <label>按分类筛选：</label>
      <select v-model="selectedCategory">
        <option value="">全部</option>
        <option value="讲座">讲座</option>
        <option value="比赛">比赛</option>
        <option value="社团活动">社团活动</option>
      </select>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>

    <div class="card-list">
      <div class="event-card" v-for="item in filteredEvents" :key="item.id">
        <h2>{{ item.title }}</h2>
        <p>类别：{{ item.category }}</p>
        <p>地点：{{ item.location }}</p>
        <p>开始时间：{{ item.start_time }}</p>
        <p>人数上限：{{ item.max_participants }}</p>
        <p>已通过人数：{{ item.approved_count }}</p>
        <p>
          状态：
          <span :class="item.status === '已结束' ? 'status-ended' : 'status-open'">
            {{ item.status }}
          </span>
        </p>
        <p>{{ item.description }}</p>

        <div class="btn-group">
          <button class="detail-btn" @click="goDetail(item.id)">查看详情</button>

          <button
            v-if="role === 'student'"
            class="signup-btn"
            :disabled="item.status === '已结束'"
            @click="signup(item.id)"
          >
            {{ item.status === '已结束' ? '活动已结束' : '立即报名' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const eventList = ref([])
const message = ref('')
const selectedCategory = ref('')

const username = localStorage.getItem('username') || ''
const role = localStorage.getItem('role') || ''

const roleText = computed(() => {
  if (role === 'student') return '学生'
  if (role === 'organizer') return '组织者'
  if (role === 'admin') return '管理员'
  return '未知角色'
})

const filteredEvents = computed(() => {
  if (!selectedCategory.value) {
    return eventList.value
  }
  return eventList.value.filter(item => item.category === selectedCategory.value)
})

const loadEvents = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/events`)
    eventList.value = res.data
  } catch (error) {
    message.value = '获取活动列表失败'
  }
}

const signup = async (eventId) => {
  const userId = localStorage.getItem('user_id')

  if (!userId) {
    message.value = '请先登录'
    router.push('/login')
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/registrations`, {
      user_id: Number(userId),
      event_id: eventId
    })
    message.value = res.data.message
    await loadEvents()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '报名失败'
    }
  }
}

const goDetail = (eventId) => {
  router.push(`/events/${eventId}`)
}

const goMyRegistrations = () => {
  router.push('/my-registrations')
}

const goHome = () => {
  router.push('/home')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  loadEvents()
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
  font-size: 24px;
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

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #333;
}

.filter-bar select {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: white;
}

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.event-card {
  width: 430px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.event-card h2 {
  margin-top: 0;
  color: #333;
}

.event-card p {
  margin: 8px 0;
  color: #555;
}

.btn-group {
  margin-top: 18px;
  display: flex;
  gap: 10px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.green-btn {
  background: #67c23a;
}
.green-btn:hover {
  background: #85ce61;
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

.detail-btn {
  background: #5b8def;
}
.detail-btn:hover {
  background: #7aa5f3;
}

.signup-btn {
  background: #409eff;
}
.signup-btn:hover {
  background: #66b1ff;
}

.signup-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.status-open {
  color: #16a34a;
  font-weight: bold;
}

.status-ended {
  color: #ef4444;
  font-weight: bold;
}
</style>