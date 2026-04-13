<template>
  <div class="page">
    <div class="page-header glass">
      <div class="header-left">
        <p class="eyebrow">ORGANIZER PANEL</p>
        <h1>活动报名名单</h1>
        <p class="subtitle">查看当前活动的报名记录，并导出 Excel 报名名单</p>
      </div>

      <div class="header-actions">
        <button class="top-btn btn-success" @click="exportExcel">导出 Excel</button>
        <button class="top-btn btn-secondary" @click="goBack">返回我的活动</button>
        <button class="top-btn btn-danger" @click="logout">退出登录</button>
      </div>
    </div>

    <transition name="fade-slide">
      <div v-if="message" class="message-box">
        {{ message }}
      </div>
    </transition>

    <div v-if="eventInfo" class="event-info-card">
      <div class="event-info-top">
        <h2>{{ eventInfo.event_title }}</h2>
        <span class="category-pill" :class="getCategoryClass(eventInfo.event_category)">
          {{ eventInfo.event_category }}
        </span>
      </div>

      <div class="event-meta-grid">
        <div class="meta-item">
          <span class="label">活动ID</span>
          <span class="value">{{ eventInfo.event_id }}</span>
        </div>
        <div class="meta-item">
          <span class="label">地点</span>
          <span class="value">{{ eventInfo.event_location }}</span>
        </div>
        <div class="meta-item">
          <span class="label">开始时间</span>
          <span class="value">{{ eventInfo.event_start_time }}</span>
        </div>
        <div class="meta-item">
          <span class="label">报名人数</span>
          <span class="value">{{ registrations.length }}</span>
        </div>
      </div>
    </div>

    <div class="table-card">
      <div class="table-header">
        <h3>报名名单</h3>
        <span class="count-text">共 {{ registrations.length }} 条记录</span>
      </div>

      <div v-if="registrations.length > 0" class="table-wrapper">
        <table class="custom-table">
          <thead>
            <tr>
              <th>报名记录ID</th>
              <th>用户ID</th>
              <th>用户名</th>
              <th>活动ID</th>
              <th>审核状态</th>
              <th>报名时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in registrations" :key="item.registration_id">
              <td>{{ item.registration_id }}</td>
              <td>{{ item.user_id }}</td>
              <td>{{ item.username }}</td>
              <td>{{ item.event_id }}</td>
              <td>
                <span class="status-pill" :class="getStatusClass(item.status)">
                  {{ item.status }}
                </span>
              </td>
              <td>{{ item.signup_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-box">
        <div class="empty-icon">📄</div>
        <div class="empty-title">暂无报名记录</div>
        <div class="empty-desc">当前活动还没有学生报名</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const route = useRoute()
const router = useRouter()

const organizerId = localStorage.getItem('user_id')
const eventId = route.params.eventId || route.params.id || route.params.event_id

const eventInfo = ref(null)
const registrations = ref([])
const message = ref('')

const normalizeResponseData = (data) => {
  return {
    event_id: data.event_id,
    event_title: data.event_title,
    event_category: data.event_category,
    event_location: data.event_location,
    event_start_time: data.event_start_time,
    registrations: data.registrations || []
  }
}

const tryFetchRegistrations = async (url) => {
  const res = await axios.get(url, {
    params: {
      user_id: organizerId
    }
  })
  return normalizeResponseData(res.data || {})
}

const loadRegistrations = async () => {
  if (!eventId) {
    message.value = '活动ID不存在，无法获取报名名单'
    return
  }

  const candidateUrls = [
    `${API_BASE_URL}/organizer/${organizerId}/events/${eventId}/registrations`,
    `${API_BASE_URL}/organizer/events/${eventId}/registrations`
  ]

  let lastError = null

  for (const url of candidateUrls) {
    try {
      const data = await tryFetchRegistrations(url)

      eventInfo.value = {
        event_id: data.event_id,
        event_title: data.event_title,
        event_category: data.event_category,
        event_location: data.event_location,
        event_start_time: data.event_start_time
      }

      registrations.value = data.registrations
      message.value = ''
      return
    } catch (error) {
      lastError = error
    }
  }

  if (lastError && lastError.response && lastError.response.data && lastError.response.data.message) {
    message.value = lastError.response.data.message
  } else {
    message.value = '获取报名名单失败'
  }
}

const exportExcel = () => {
  if (!eventId) {
    message.value = '活动ID不存在，无法导出'
    clearMessageLater()
    return
  }

  // 先直接使用你已有的导出接口
  const exportUrl = `${API_BASE_URL}/events/${eventId}/export?user_id=${organizerId}`
  window.open(exportUrl, '_blank')
}

const clearMessageLater = () => {
  setTimeout(() => {
    message.value = ''
  }, 2500)
}

const goBack = () => {
  router.push('/organizer/my-events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

const getStatusClass = (status) => {
  if (status === '待审核') return 'status-pending'
  if (status === '已通过') return 'status-approved'
  if (status === '已拒绝') return 'status-rejected'
  return 'status-default'
}

const getCategoryClass = (category) => {
  if (category === '讲座') return 'tag-lecture'
  if (category === '比赛') return 'tag-contest'
  if (category === '社团活动') return 'tag-club'
  return 'tag-default'
}

onMounted(() => {
  loadRegistrations()
})
</script>

<style scoped>
:global(body) {
  background: #f5f5f7;
}

.page {
  min-height: 100vh;
  padding: 40px 32px 72px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.05), transparent 22%),
    linear-gradient(180deg, #f5f5f7 0%, #f7f7f9 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
  padding: 32px 36px;
  border-radius: 30px;
}

.glass {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.header-left {
  max-width: 760px;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6e6e73;
}

.header-left h1 {
  margin: 0;
  font-size: 46px;
  font-weight: 300;
  line-height: 1.08;
  color: #1d1d1f;
  letter-spacing: -0.02em;
}

.subtitle {
  margin-top: 16px;
  font-size: 17px;
  line-height: 1.95;
  color: #6e6e73;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-self: center;
}

.top-btn {
  border: none;
  border-radius: 999px;
  padding: 12px 20px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.top-btn:hover {
  transform: translateY(-2px) scale(1.02);
}

.btn-success {
  background: #0071e3;
}

.btn-success:hover {
  background: #0062c6;
}

.btn-secondary {
  background: #8e8e93;
}

.btn-secondary:hover {
  background: #7b7b80;
}

.btn-danger {
  background: #ff5a5f;
}

.btn-danger:hover {
  background: #ef4c51;
}

.message-box {
  margin-bottom: 24px;
  padding: 16px 20px;
  border-radius: 20px;
  background: rgba(226, 250, 235, 0.92);
  color: #136c3f;
  font-weight: 500;
  line-height: 1.8;
  box-shadow: 0 8px 26px rgba(0, 0, 0, 0.04);
}

.event-info-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  margin-bottom: 28px;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.event-info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.event-info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.event-info-top h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 300;
  color: #1d1d1f;
  line-height: 1.5;
}

.event-meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.meta-item {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(245, 245, 247, 0.92);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-size: 12px;
  color: #6e6e73;
  font-weight: 500;
}

.value {
  font-size: 15px;
  color: #1d1d1f;
  font-weight: 500;
  line-height: 1.75;
  word-break: break-word;
}

.category-pill,
.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.category-pill {
  color: #fff;
}

.tag-lecture {
  background: #4f9df6;
}

.tag-contest {
  background: #f5a623;
}

.tag-club {
  background: #34c759;
}

.tag-default {
  background: #8e8e93;
}

.status-pending {
  background: rgba(245, 166, 35, 0.14);
  color: #c67a00;
}

.status-approved {
  background: rgba(52, 199, 89, 0.14);
  color: #1f8f42;
}

.status-rejected {
  background: rgba(255, 90, 95, 0.14);
  color: #d6454a;
}

.status-default {
  background: rgba(142, 142, 147, 0.12);
  color: #6e6e73;
}

.table-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}

.table-header h3 {
  margin: 0;
  font-size: 26px;
  font-weight: 300;
  color: #1d1d1f;
}

.count-text {
  color: #6e6e73;
  font-size: 14px;
}

.table-wrapper {
  overflow-x: auto;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

.custom-table thead th {
  text-align: left;
  padding: 16px 18px;
  font-size: 13px;
  font-weight: 600;
  color: #6e6e73;
  background: #f5f5f7;
}

.custom-table thead th:first-child {
  border-top-left-radius: 16px;
  border-bottom-left-radius: 16px;
}

.custom-table thead th:last-child {
  border-top-right-radius: 16px;
  border-bottom-right-radius: 16px;
}

.custom-table tbody td {
  padding: 18px;
  font-size: 14px;
  color: #1d1d1f;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.custom-table tbody tr {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-table tbody tr:hover {
  background: rgba(0, 113, 227, 0.03);
}

.empty-box {
  text-align: center;
  padding: 72px 24px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 18px;
  color: #8e8e93;
}

.empty-title {
  font-size: 28px;
  font-weight: 300;
  color: #1d1d1f;
  line-height: 1.5;
}

.empty-desc {
  margin-top: 12px;
  color: #6e6e73;
  font-size: 15px;
  line-height: 1.9;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

@media (max-width: 767px) {
  .page {
    padding: 20px 16px 48px;
  }

  .page-header {
    flex-direction: column;
    padding: 24px 20px;
  }

  .header-left h1 {
    font-size: 36px;
  }

  .event-info-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .event-meta-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1199px) {
  .event-meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>