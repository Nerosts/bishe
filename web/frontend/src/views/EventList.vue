<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动列表</h1>
        <p class="welcome-text">
          欢迎你，{{ currentUsername }}（{{ roleText }}）
        </p>
      </div>

      <div class="top-buttons">
        <button
          v-if="currentRole === 'student'"
          class="green-btn"
          @click="goMyRegistrations"
        >
          我的报名
        </button>

        <button
          v-if="currentRole === 'organizer'"
          class="teal-btn"
          @click="goOrganizerMyEvents"
        >
          我的活动
        </button>

        <button
          v-if="currentRole === 'admin'"
          class="purple-btn"
          @click="goAdminHome"
        >
          返回管理首页
        </button>

        <button
          v-if="currentRole === 'student' || currentRole === 'organizer'"
          class="gray-btn"
          @click="goHome"
        >
          返回首页
        </button>

        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="filter-box">
      <label>按分类筛选：</label>
      <select v-model="selectedCategory">
        <option value="">全部</option>
        <option value="讲座">讲座</option>
        <option value="比赛">比赛</option>
        <option value="社团活动">社团活动</option>
      </select>
    </div>

    <div class="card-list">
      <div class="event-card" v-for="event in filteredEvents" :key="event.id">
        <div class="card-top">
          <h2>{{ event.title }}</h2>

          <span
            class="category-tag"
            :class="getCategoryClass(event.category)"
          >
            {{ event.category }}
          </span>
        </div>

        <p>
          类别：
          <span :class="getCategoryTextClass(event.category)">
            {{ event.category }}
          </span>
        </p>
        <p>地点：{{ event.location }}</p>
        <p>开始时间：{{ event.start_time }}</p>
        <p>人数上限：{{ event.max_participants }}</p>
        <p>已通过人数：{{ event.approved_count }}</p>
        <p>
          状态：
          <span :class="getStatusClass(event.status)">
            {{ event.status }}
          </span>
        </p>
        <p>{{ event.description }}</p>

        <div class="btn-group">
          <button class="detail-btn" @click="goDetail(event.id)">查看详情</button>

          <button
            v-if="currentRole === 'student' && event.status !== '已结束'"
            class="register-btn"
            @click="registerEvent(event.id)"
          >
            立即报名
          </button>

          <button
            v-if="currentRole === 'student' && event.status === '已结束'"
            class="ended-btn"
            disabled
          >
            活动已结束
          </button>

          <button
            v-if="currentRole !== 'student' && event.status === '已结束'"
            class="ended-btn"
            disabled
          >
            已结束
          </button>
        </div>
      </div>
    </div>

    <div v-if="message" class="message-box">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()

const eventList = ref([])
const selectedCategory = ref('')
const message = ref('')

const currentUserId = localStorage.getItem('user_id')
const currentUsername = localStorage.getItem('username') || '未登录用户'
const currentRole = localStorage.getItem('role') || ''

const roleText = computed(() => {
  if (currentRole === 'student') return '学生'
  if (currentRole === 'organizer') return '组织者'
  if (currentRole === 'admin') return '管理员'
  return '未知角色'
})

const loadEvents = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/events`)
    eventList.value = res.data
  } catch (error) {
    message.value = '获取活动列表失败'
  }
}

const filteredEvents = computed(() => {
  if (!selectedCategory.value) {
    return eventList.value
  }
  return eventList.value.filter(item => item.category === selectedCategory.value)
})

const registerEvent = async (eventId) => {
  if (currentRole !== 'student') {
    message.value = '只有学生可以报名活动'
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/registrations`, {
      user_id: currentUserId,
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

const getCategoryClass = (category) => {
  if (category === '讲座') return 'lecture-tag'
  if (category === '比赛') return 'contest-tag'
  if (category === '社团活动') return 'club-tag'
  return 'default-tag'
}

const getCategoryTextClass = (category) => {
  if (category === '讲座') return 'lecture-text'
  if (category === '比赛') return 'contest-text'
  if (category === '社团活动') return 'club-text'
  return ''
}

const getStatusClass = (status) => {
  if (status === '报名中') return 'status-open'
  if (status === '已结束') return 'status-ended'
  return 'status-default'
}

const goDetail = (id) => {
  router.push(`/events/${id}`)
}

const goMyRegistrations = () => {
  router.push('/my-registrations')
}

const goOrganizerMyEvents = () => {
  router.push('/organizer/my-events')
}

const goAdminHome = () => {
  router.push('/home')
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

.welcome-text {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-box {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-box label {
  font-size: 16px;
  color: #333;
}

.filter-box select {
  width: 150px;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 22px;
}

.event-card {
  background: #fff;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.event-card h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
}

.event-card p {
  margin: 8px 0;
  color: #555;
  line-height: 1.6;
}

.category-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: white;
  white-space: nowrap;
}

.lecture-tag {
  background: #409eff;
}

.contest-tag {
  background: #e6a23c;
}

.club-tag {
  background: #67c23a;
}

.default-tag {
  background: #909399;
}

.lecture-text {
  color: #409eff;
  font-weight: 600;
}

.contest-text {
  color: #e6a23c;
  font-weight: 600;
}

.club-text {
  color: #67c23a;
  font-weight: 600;
}

.status-open {
  color: #67c23a;
  font-weight: 700;
}

.status-ended {
  color: #909399;
  font-weight: 700;
}

.status-default {
  color: #606266;
  font-weight: 700;
}

.btn-group {
  margin-top: 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.detail-btn {
  background: #5b8def;
}

.detail-btn:hover {
  background: #7aa5f3;
}

.register-btn {
  background: #409eff;
}

.register-btn:hover {
  background: #66b1ff;
}

.ended-btn {
  background: #909399;
  cursor: not-allowed;
}

.green-btn {
  background: #67c23a;
}

.green-btn:hover {
  background: #85ce61;
}

.teal-btn {
  background: #14b8a6;
}

.teal-btn:hover {
  background: #2dd4bf;
}

.purple-btn {
  background: #8b5cf6;
}

.purple-btn:hover {
  background: #a78bfa;
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
  margin-top: 24px;
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
}
</style>