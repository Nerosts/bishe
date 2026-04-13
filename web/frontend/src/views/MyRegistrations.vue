<template>
  <div class="page">
    <div class="page-header">
      <div class="header-left">
        <h1>我的报名</h1>
        <p>查看当前学生账号的活动报名记录</p>
      </div>

      <div class="header-actions">
        <button class="top-btn primary-btn" @click="goEvents">活动列表</button>
        <button class="top-btn secondary-btn" @click="goHome">返回首页</button>
        <button class="top-btn danger-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <transition name="fade">
      <div v-if="message" class="message-box">
        {{ message }}
      </div>
    </transition>

    <div v-if="registrationList.length > 0" class="card-grid">
      <div
        class="registration-card"
        v-for="item in registrationList"
        :key="item.registration_id"
      >
        <div class="card-header">
          <div class="title-line">
            <h2 class="event-title">{{ item.event_title }}</h2>
            <span
              class="category-tag"
              :class="getCategoryTagClass(item.event_category)"
            >
              {{ item.event_category }}
            </span>
          </div>

          <span
            class="status-pill"
            :class="getStatusClass(item.status)"
          >
            {{ item.status }}
          </span>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">报名记录ID</span>
            <span class="value">{{ item.registration_id }}</span>
          </div>

          <div class="info-item">
            <span class="label">活动ID</span>
            <span class="value">{{ item.event_id }}</span>
          </div>

          <div class="info-item full-width">
            <span class="label">地点</span>
            <span class="value">{{ item.event_location }}</span>
          </div>

          <div class="info-item">
            <span class="label">开始时间</span>
            <span class="value">{{ item.event_start_time }}</span>
          </div>

          <div class="info-item">
            <span class="label">报名时间</span>
            <span class="value">{{ item.signup_time }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button class="action-btn view-btn" @click="goEventDetail(item.event_id)">
            查看活动
          </button>
          <button class="action-btn cancel-btn" @click="cancelRegistration(item.registration_id)">
            取消报名
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-box">
      <div class="empty-icon">📄</div>
      <div class="empty-title">暂无报名记录</div>
      <div class="empty-desc">你还没有报名任何活动，先去活动列表看看吧</div>
      <button class="top-btn primary-btn" @click="goEvents">去活动列表</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const registrationList = ref([])
const message = ref('')

const currentUserId = localStorage.getItem('user_id')

const loadMyRegistrations = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/users/${currentUserId}/registrations`, {
      params: {
        user_id: currentUserId
      }
    })
    registrationList.value = res.data || []
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取报名记录失败'
    }
  }
}

const cancelRegistration = async (registrationId) => {
  try {
    const res = await axios.delete(`${API_BASE_URL}/registrations/${registrationId}`, {
      data: {
        user_id: currentUserId
      }
    })
    message.value = res.data.message || '取消报名成功'
    await loadMyRegistrations()

    setTimeout(() => {
      message.value = ''
    }, 2500)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '取消报名失败'
    }

    setTimeout(() => {
      message.value = ''
    }, 2500)
  }
}

const getStatusClass = (status) => {
  if (status === '待审核') return 'status-pending'
  if (status === '已通过') return 'status-approved'
  if (status === '已拒绝') return 'status-rejected'
  return 'status-default'
}

const getCategoryTagClass = (category) => {
  if (category === '讲座') return 'tag-lecture'
  if (category === '比赛') return 'tag-contest'
  if (category === '社团活动') return 'tag-club'
  return 'tag-default'
}

const goEventDetail = (eventId) => {
  router.push(`/events/${eventId}`)
}

const goEvents = () => {
  router.push('/events')
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
  loadMyRegistrations()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 32px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 26%),
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 24%),
    linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
}

.header-left h1 {
  margin: 0;
  font-size: 38px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 0.5px;
}

.header-left p {
  margin-top: 10px;
  color: #64748b;
  font-size: 15px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.top-btn {
  border: none;
  border-radius: 12px;
  padding: 11px 18px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.top-btn:hover {
  transform: translateY(-2px);
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.primary-btn:hover {
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
}

.secondary-btn {
  background: linear-gradient(135deg, #94a3b8, #a8b4c7);
}

.secondary-btn:hover {
  box-shadow: 0 8px 20px rgba(148, 163, 184, 0.25);
}

.danger-btn {
  background: linear-gradient(135deg, #f87171, #fb7185);
}

.danger-btn:hover {
  box-shadow: 0 8px 20px rgba(248, 113, 113, 0.25);
}

.message-box {
  margin-bottom: 24px;
  padding: 14px 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.registration-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 24px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.registration-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.98);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 20px;
}

.title-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.event-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.tag-lecture {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.tag-contest {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.tag-club {
  background: linear-gradient(135deg, #22c55e, #4ade80);
}

.tag-default {
  background: linear-gradient(135deg, #9ca3af, #b6bcc6);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.status-pending {
  color: #b45309;
  background: rgba(251, 191, 36, 0.18);
}

.status-approved {
  color: #15803d;
  background: rgba(34, 197, 94, 0.18);
}

.status-rejected {
  color: #dc2626;
  background: rgba(248, 113, 113, 0.18);
}

.status-default {
  color: #475569;
  background: rgba(148, 163, 184, 0.18);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
  margin-bottom: 22px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
}

.full-width {
  grid-column: 1 / -1;
}

.label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.value {
  font-size: 15px;
  color: #334155;
  font-weight: 600;
  word-break: break-word;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.view-btn {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.view-btn:hover {
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
}

.cancel-btn {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.cancel-btn:hover {
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.25);
}

.empty-box {
  margin-top: 60px;
  text-align: center;
  padding: 64px 24px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 52px;
  margin-bottom: 14px;
}

.empty-title {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
}

.empty-desc {
  margin-top: 10px;
  font-size: 15px;
  color: #64748b;
  margin-bottom: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 767px) {
  .page {
    padding: 18px;
  }

  .page-header {
    flex-direction: column;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1199px) {
  .card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1200px) {
  .card-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>