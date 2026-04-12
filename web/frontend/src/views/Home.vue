<template>
  <div class="home-page">
    <div class="card">
      <img
        v-if="role === 'admin'"
        src="../assets/admin-banner.jpg"
        alt="管理员图片"
        class="admin-image"
      />

      <h1>登录成功</h1>
      <p><strong>用户ID：</strong>{{ userId }}</p>
      <p><strong>用户名：</strong>{{ username }}</p>
      <p><strong>角色：</strong>{{ role }}</p>

      <p class="tip" v-if="role === 'admin'">当前是管理员，可以进入报名审核和统计分析页面。</p>
      <p class="tip" v-else-if="role === 'organizer'">当前是组织者，可以发布活动并查看自己发布的活动。</p>
      <p class="tip" v-else>当前是普通用户。</p>

      <div class="btn-group">
        <button class="blue-btn" @click="goEvents">查看活动列表</button>

        <button
          v-if="role === 'admin'"
          class="green-btn"
          @click="goAdminReview"
        >
          报名审核
        </button>

        <button
          v-if="role === 'admin'"
          class="purple-btn"
          @click="goAdminStats"
        >
          统计分析
        </button>

        <button
          v-if="role === 'organizer'"
          class="orange-btn"
          @click="goOrganizerPublish"
        >
          发布活动
        </button>

        <button
          v-if="role === 'organizer'"
          class="cyan-btn"
          @click="goOrganizerMyEvents"
        >
          我的活动
        </button>

        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const userId = ref('')
const username = ref('')
const role = ref('')

onMounted(() => {
  userId.value = localStorage.getItem('user_id') || ''
  username.value = localStorage.getItem('username') || ''
  role.value = localStorage.getItem('role') || ''

  if (!userId.value) {
    router.push('/login')
  }
})

const goEvents = () => {
  router.push('/events')
}

const goAdminReview = () => {
  router.push('/admin/review')
}

const goAdminStats = () => {
  router.push('/admin/stats')
}

const goOrganizerPublish = () => {
  router.push('/organizer/publish')
}

const goOrganizerMyEvents = () => {
  router.push('/organizer/my-events')
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
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  padding: 20px;
  box-sizing: border-box;
}

.card {
  width: 560px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  text-align: center;
}

.admin-image {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 24px;
}

h1 {
  margin-bottom: 20px;
}

p {
  margin: 10px 0;
  color: #333;
}

.tip {
  margin-top: 20px;
  color: #409eff;
}

.btn-group {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

button {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  color: white;
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

.cyan-btn {
  background: #14b8a6;
}

.cyan-btn:hover {
  background: #2dd4bf;
}

.red-btn {
  background: #f56c6c;
}

.red-btn:hover {
  background: #f78989;
}
</style>