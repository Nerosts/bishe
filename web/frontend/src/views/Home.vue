<template>
  <div class="home-page" :class="{ 'admin-page': role === 'admin' }">
    <div v-if="role === 'admin'" class="admin-bg-overlay"></div>

    <div class="hero-wrap">
      <div class="glass-card">
        <p class="hero-eyebrow">Campus Activity Platform</p>
        <h1 class="hero-title">登录成功</h1>
        <p class="hero-desc">
          欢迎回来，系统已识别你的身份，并为你展示对应的功能入口。
        </p>

        <div class="user-meta">
          <div class="meta-row">
            <span class="meta-label">用户ID</span>
            <span class="meta-value">{{ userId }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">用户名</span>
            <span class="meta-value">{{ username }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">角色</span>
            <span class="meta-value">{{ role }}</span>
          </div>
        </div>

        <div class="role-intro">
          {{ roleIntro }}
        </div>

        <div class="action-grid">
          <template v-if="role === 'admin'">
            <button class="action-btn primary" @click="goTo('/events')">查看活动列表</button>
            <button class="action-btn secondary" @click="goTo('/admin/review')">报名审核</button>
            <button class="action-btn secondary" @click="goTo('/admin/stats')">统计分析</button>
            <button class="action-btn secondary" @click="goTo('/admin/checkins')">签到查询</button>
            <button class="action-btn secondary" @click="goTo('/admin/users')">用户管理</button>
          </template>

          <template v-else-if="role === 'organizer'">
            <button class="action-btn primary" @click="goTo('/organizer/publish')">发布活动</button>
            <button class="action-btn secondary" @click="goTo('/organizer/my-events')">我的活动</button>
          </template>

          <template v-else-if="role === 'student'">
            <button class="action-btn primary" @click="goTo('/events')">活动列表</button>
            <button class="action-btn secondary" @click="goTo('/my-registrations')">我的报名</button>
          </template>

          <button class="action-btn danger" @click="logout">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import adminBanner from '../assets/admin-banner.jpg'

const router = useRouter()

const userId = localStorage.getItem('user_id') || ''
const username = localStorage.getItem('username') || ''
const role = localStorage.getItem('role') || ''

const roleIntro = computed(() => {
  if (role === 'admin') {
    return '当前是管理员身份，可进行报名审核、用户管理、签到记录查询与统计分析。'
  }
  if (role === 'organizer') {
    return '当前是组织者身份，可发布活动、管理自己发布的活动，并导出活动报名名单。'
  }
  if (role === 'student') {
    return '当前是学生身份，可浏览活动、在线报名、扫码签到并查看自己的报名记录。'
  }
  return '当前角色信息读取失败，请重新登录。'
})

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>

<style scoped>
:global(body) {
  background: #f5f5f7;
  color: #1d1d1f;
}

.home-page {
  min-height: 100vh;
  position: relative;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.05), transparent 22%),
    linear-gradient(180deg, #f5f5f7 0%, #f7f7f9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  box-sizing: border-box;
  overflow: hidden;
}

/* 管理员专属背景图 */
.admin-page {
  background-image: url('../assets/admin-banner.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.admin-bg-overlay {
  position: absolute;
  inset: 0;
  background: rgba(245, 245, 247, 0.38);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.hero-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.glass-card {
  width: min(760px, 100%);
  padding: 52px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.66);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.05);
}

.hero-eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  color: #6e6e73;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-title {
  margin: 0;
  font-size: clamp(38px, 5vw, 56px);
  font-weight: 300;
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: #1d1d1f;
}

.hero-desc {
  margin: 18px 0 0;
  font-size: 17px;
  line-height: 1.95;
  color: #6e6e73;
}

.user-meta {
  margin-top: 34px;
  display: grid;
  gap: 14px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  background: rgba(245, 245, 247, 0.88);
}

.meta-label {
  font-size: 14px;
  color: #6e6e73;
  font-weight: 500;
}

.meta-value {
  font-size: 15px;
  color: #1d1d1f;
  font-weight: 500;
  text-align: right;
  word-break: break-word;
}

.role-intro {
  margin-top: 28px;
  padding: 20px 22px;
  border-radius: 18px;
  background: rgba(0, 113, 227, 0.06);
  color: #0071e3;
  font-size: 15px;
  line-height: 1.9;
}

.action-grid {
  margin-top: 34px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.action-btn {
  min-height: 52px;
  padding: 0 18px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn:hover {
  transform: translateY(-2px) scale(1.01);
}

.action-btn.primary {
  background: #0071e3;
  color: #fff;
}

.action-btn.primary:hover {
  background: #0062c6;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.92);
  color: #1d1d1f;
  box-shadow: inset 0 0 0 1px rgba(29, 29, 31, 0.08);
}

.action-btn.secondary:hover {
  background: #ffffff;
}

.action-btn.danger {
  background: #ff5a5f;
  color: #fff;
}

.action-btn.danger:hover {
  background: #ef4c51;
}

@media (max-width: 767px) {
  .home-page {
    padding: 16px;
  }

  .glass-card {
    padding: 32px 22px;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }

  .meta-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .meta-value {
    text-align: left;
  }
}
</style>