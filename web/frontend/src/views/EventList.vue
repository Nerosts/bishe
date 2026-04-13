<template>
  <div class="page">
    <header class="page-header glass">
      <div class="header-left">
        <p class="eyebrow">Campus Activity System</p>
        <h1>活动列表</h1>
        <p class="subtitle">浏览校园活动，查看详情并进行报名</p>
      </div>

      <div class="header-actions">
        <button class="top-btn btn-success" @click="goMyRegistrations">我的报名</button>
        <button class="top-btn btn-secondary" @click="goHome">返回首页</button>
        <button class="top-btn btn-danger" @click="logout">退出登录</button>
      </div>
    </header>

    <transition name="fade-slide">
      <div v-if="message" class="message-box">
        {{ message }}
      </div>
    </transition>

    <section class="filter-bar glass">
      <div class="filter-item">
        <label>按分类筛选</label>
        <select v-model="selectedCategory">
          <option value="">全部</option>
          <option value="讲座">讲座</option>
          <option value="比赛">比赛</option>
          <option value="社团活动">社团活动</option>
          <option value="test">test</option>
        </select>
      </div>
    </section>

    <section v-if="filteredEvents.length > 0" class="card-grid">
      <article
        class="event-card reveal-card"
        :class="{ visible: visibleIds.has(event.id) }"
        v-for="event in filteredEvents"
        :key="event.id"
        :ref="el => setCardRef(el, event.id)"
      >
        <div class="card-header">
          <div class="title-row">
            <h2 class="event-title">{{ event.title }}</h2>
            <span class="category-pill" :class="getCategoryTagClass(event.category)">
              {{ event.category }}
            </span>
          </div>

          <span class="status-pill" :class="getEventStatusClass(event.status)">
            {{ event.status }}
          </span>
        </div>

        <div class="meta-grid">
          <div class="meta-item">
            <span class="label">地点</span>
            <span class="value">{{ event.location }}</span>
          </div>

          <div class="meta-item">
            <span class="label">开始时间</span>
            <span class="value">{{ event.start_time }}</span>
          </div>

          <div class="meta-item">
            <span class="label">人数上限</span>
            <span class="value">{{ event.max_participants }}</span>
          </div>

          <div class="meta-item">
            <span class="label">已通过人数</span>
            <span class="value">{{ event.approved_count }}</span>
          </div>
        </div>

        <div class="desc-box">
          {{ event.description || '暂无活动描述' }}
        </div>

        <div class="card-footer">
          <div class="registration-state">
            <template v-if="getRegistrationStatus(event.id)">
              <span
                class="registration-pill"
                :class="getRegistrationPillClass(getRegistrationStatus(event.id))"
              >
                {{ getRegistrationStatus(event.id) }}
              </span>
            </template>
            <template v-else>
              <span class="registration-hint">未报名</span>
            </template>
          </div>

          <div class="card-actions">
            <button class="action-btn btn-view" @click="goDetail(event.id)">查看详情</button>

            <button
              v-if="event.status === '已结束'"
              class="action-btn btn-disabled"
              disabled
            >
              活动已结束
            </button>

            <button
              v-else-if="getRegistrationStatus(event.id) === '待审核'"
              class="action-btn btn-waiting"
              disabled
            >
              等待审核
            </button>

            <button
              v-else-if="getRegistrationStatus(event.id) === '已通过'"
              class="action-btn btn-approved"
              disabled
            >
              已通过审核
            </button>

            <button
              v-else-if="getRegistrationStatus(event.id) === '已拒绝'"
              class="action-btn btn-rejected"
              disabled
            >
              已拒绝
            </button>

            <button
              v-else
              class="action-btn btn-primary"
              @click="signup(event.id)"
            >
              立即报名
            </button>
          </div>
        </div>
      </article>
    </section>

    <section v-else class="empty-box glass-soft">
      <div class="empty-icon">◌</div>
      <div class="empty-title">暂无符合条件的活动</div>
      <div class="empty-desc">试试切换分类，或者稍后再来查看</div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()

const events = ref([])
const selectedCategory = ref('')
const message = ref('')
const myRegistrationMap = ref({})
const currentUserId = localStorage.getItem('user_id')
const currentRole = localStorage.getItem('role')

const visibleIds = ref(new Set())
const cardRefs = new Map()
let observer = null

const loadEvents = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/events`)
    events.value = res.data || []
  } catch (error) {
    message.value = '获取活动列表失败'
    clearMessageLater()
  }
}

const loadMyRegistrations = async () => {
  if (!currentUserId || currentRole !== 'student') {
    myRegistrationMap.value = {}
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/users/${currentUserId}/registrations`, {
      params: { user_id: currentUserId }
    })

    const map = {}
    ;(res.data || []).forEach(item => {
      map[item.event_id] = item.status
    })
    myRegistrationMap.value = map
  } catch (error) {
    myRegistrationMap.value = {}
  }
}

const filteredEvents = computed(() => {
  if (!selectedCategory.value) return events.value
  return events.value.filter(item => item.category === selectedCategory.value)
})

const signup = async (eventId) => {
  try {
    const res = await axios.post(`${API_BASE_URL}/registrations`, {
      user_id: currentUserId,
      event_id: eventId
    })

    message.value = res.data.message || '报名成功，请等待审核'
    await Promise.all([loadEvents(), loadMyRegistrations()])
    clearMessageLater()
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '报名失败'
    }
    clearMessageLater()
  }
}

const clearMessageLater = () => {
  setTimeout(() => {
    message.value = ''
  }, 2500)
}

const getRegistrationStatus = (eventId) => {
  return myRegistrationMap.value[eventId] || ''
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

const getCategoryTagClass = (category) => {
  if (category === '讲座') return 'tag-lecture'
  if (category === '比赛') return 'tag-contest'
  if (category === '社团活动') return 'tag-club'
  return 'tag-default'
}

const getEventStatusClass = (status) => {
  if (status === '报名中') return 'event-open'
  if (status === '已结束') return 'event-end'
  return 'event-default'
}

const getRegistrationPillClass = (status) => {
  if (status === '待审核') return 'reg-pending'
  if (status === '已通过') return 'reg-approved'
  if (status === '已拒绝') return 'reg-rejected'
  return 'reg-default'
}

const setCardRef = (el, id) => {
  if (el) {
    cardRefs.set(id, el)
    if (observer) observer.observe(el)
  }
}

const initObserver = async () => {
  await nextTick()

  if (observer) observer.disconnect()

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const targetId = Number(entry.target.dataset.id)
        if (entry.isIntersecting && !Number.isNaN(targetId)) {
          visibleIds.value.add(targetId)
          observer.unobserve(entry.target)
        }
      })
    },
    {
      threshold: 0.12
    }
  )

  cardRefs.forEach((el, id) => {
    el.dataset.id = String(id)
    observer.observe(el)
  })
}

watch(filteredEvents, async () => {
  cardRefs.clear()
  visibleIds.value = new Set()
  await initObserver()
})

onMounted(async () => {
  await Promise.all([loadEvents(), loadMyRegistrations()])
  await initObserver()
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
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

.glass-soft {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
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
  font-size: 52px;
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
  margin-bottom: 28px;
  padding: 16px 20px;
  border-radius: 20px;
  background: rgba(226, 250, 235, 0.92);
  color: #136c3f;
  font-weight: 500;
  line-height: 1.8;
  box-shadow: 0 8px 26px rgba(0, 0, 0, 0.04);
}

.filter-bar {
  margin-bottom: 40px;
  padding: 26px 30px;
  border-radius: 26px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 260px;
}

.filter-item label {
  font-size: 14px;
  font-weight: 500;
  color: #6e6e73;
}

.filter-item select {
  padding: 13px 16px;
  border-radius: 16px;
  border: none;
  background: rgba(255, 255, 255, 0.86);
  font-size: 14px;
  color: #1d1d1f;
  outline: none;
  box-shadow: inset 0 0 0 1px rgba(29, 29, 31, 0.06);
}

.card-grid {
  display: grid;
  gap: 32px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.event-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.event-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.98);
}

.reveal-card {
  opacity: 0;
  transform: translateY(32px);
}

.reveal-card.visible {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.5s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 24px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.event-title {
  margin: 0;
  font-size: 22px;
  font-weight: 200;
  line-height: 1.55;
  color: #1d1d1f;
  letter-spacing: -0.015em;
}

.category-pill,
.status-pill,
.registration-pill {
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

.status-pill {
  width: fit-content;
}

.event-open {
  background: rgba(0, 113, 227, 0.1);
  color: #0071e3;
}

.event-end {
  background: rgba(142, 142, 147, 0.12);
  color: #6e6e73;
}

.event-default {
  background: rgba(142, 142, 147, 0.12);
  color: #6e6e73;
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(245, 245, 247, 0.9);
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

.desc-box {
  margin-bottom: 28px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(245, 245, 247, 0.85);
  color: #6e6e73;
  font-size: 14px;
  line-height: 1.9;
  min-height: 88px;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.registration-state {
  min-height: 30px;
  display: flex;
  align-items: center;
}

.registration-hint {
  font-size: 13px;
  color: #8e8e93;
  font-weight: 500;
}

.reg-pending {
  background: rgba(245, 166, 35, 0.14);
  color: #c67a00;
}

.reg-approved {
  background: rgba(52, 199, 89, 0.14);
  color: #1f8f42;
}

.reg-rejected {
  background: rgba(255, 90, 95, 0.14);
  color: #d6454a;
}

.reg-default {
  background: rgba(142, 142, 147, 0.12);
  color: #6e6e73;
}

.card-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.action-btn {
  width: 100%;
  border: none;
  border-radius: 16px;
  padding: 14px 16px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn:hover {
  transform: translateY(-2px) scale(1.02);
}

.btn-view {
  background: #e9f3ff;
  color: #0071e3;
}

.btn-view:hover {
  background: #dcecff;
}

.btn-primary {
  background: #0071e3;
}

.btn-primary:hover {
  background: #0062c6;
}

.btn-disabled {
  background: #d2d2d7;
  color: #6e6e73;
  cursor: not-allowed;
}

.btn-waiting {
  background: #f5a623;
  color: #fff;
  cursor: not-allowed;
}

.btn-approved {
  background: #34c759;
  color: #fff;
  cursor: not-allowed;
}

.btn-rejected {
  background: #ff5a5f;
  color: #fff;
  cursor: not-allowed;
}

.empty-box {
  margin-top: 80px;
  padding: 80px 32px;
  border-radius: 28px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 18px;
  color: #8e8e93;
}

.empty-title {
  font-size: 30px;
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
    font-size: 38px;
  }

  .card-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1199px) {
  .card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1200px) and (max-width: 1599px) {
  .card-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1600px) {
  .card-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>