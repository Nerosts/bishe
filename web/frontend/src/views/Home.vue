<template>
  <div
    class="home-page"
    :class="{ 'admin-bg': userRole === 'admin' }"
    :style="adminBackgroundStyle"
  >
    <div class="home-card" :class="{ 'admin-card': userRole === 'admin' }">
      <h1>登录成功</h1>
      <p><strong>用户ID：</strong>{{ userId }}</p>
      <p><strong>用户名：</strong>{{ username }}</p>
      <p><strong>角色：</strong>{{ userRole }}</p>

      <p class="tip-text" v-if="userRole === 'student'">
        当前是学生，可以进入活动列表和我的报名页面。
      </p>

      <p class="tip-text" v-if="userRole === 'organizer'">
        当前是组织者，可以发布活动并管理自己发布的活动。
      </p>

      <p class="tip-text" v-if="userRole === 'admin'">
        当前是管理员，可以进入报名审核、统计分析、签到查询和用户管理页面。
      </p>

      <div class="button-group" v-if="userRole === 'student'">
        <button class="blue-btn" @click="goEvents">查看活动列表</button>
        <button class="green-btn" @click="goMyRegistrations">我的报名</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>

      <div class="button-group" v-if="userRole === 'organizer'">
        <button class="orange-btn" @click="goPublish">发布活动</button>
        <button class="green-btn" @click="goOrganizerEvents">我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>

      <div class="button-group" v-if="userRole === 'admin'">
        <button class="blue-btn" @click="goEvents">查看活动列表</button>
        <button class="green-btn" @click="goReview">报名审核</button>
        <button class="purple-btn" @click="goStats">统计分析</button>
        <button class="orange-btn" @click="goUsers">用户管理</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import adminBanner from '../assets/admin-banner.jpg'

const router = useRouter()

const userId = localStorage.getItem('user_id')
const username = localStorage.getItem('username')
const userRole = localStorage.getItem('role')

if (!userId || !username || !userRole) {
  router.push('/login')
}

const adminBackgroundStyle = computed(() => {
  if (userRole === 'admin') {
    return {
      backgroundImage: `linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)), url(${adminBanner})`
    }
  }
  return {}
})

const goEvents = () => {
  router.push('/events')
}

const goMyRegistrations = () => {
  router.push('/my-registrations')
}

const goPublish = () => {
  router.push('/organizer/publish')
}

const goOrganizerEvents = () => {
  router.push('/organizer/my-events')
}

const goReview = () => {
  router.push('/admin/review')
}

const goStats = () => {
  router.push('/admin/stats')
}

const goUsers = () => {
  router.push('/admin/users')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px;
  box-sizing: border-box;
}

.admin-bg {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.home-card {
  width: 100%;
  max-width: 560px;
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 36px;
  text-align: center;
}

.admin-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
}

h1 {
  margin-bottom: 24px;
  color: #222;
  font-size: 24px;
}

p {
  margin: 12px 0;
  color: #444;
  font-size: 16px;
}

.tip-text {
  margin-top: 20px;
  color: #60a5fa;
  font-size: 15px;
}

.button-group {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
}

button {
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  color: white;
  font-size: 14px;
  cursor: pointer;
}

.blue-btn {
  background: #409eff;
}
.blue-btn:hover {
  background: #66b1ff;
}

.green-btn {
  background: #67c23a;
}
.green-btn:hover {
  background: #85ce61;
}

.purple-btn {
  background: #8b5cf6;
}
.purple-btn:hover {
  background: #a78bfa;
}

.orange-btn {
  background: #e6a23c;
}
.orange-btn:hover {
  background: #ebb563;
}

.red-btn {
  background: #f56c6c;
}
.red-btn:hover {
  background: #f78989;
}
</style>