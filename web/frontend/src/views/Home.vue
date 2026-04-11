<template>
  <div class="home-page">
    <div class="card">
      <h1>登录成功</h1>
      <p><strong>用户ID：</strong>{{ userId }}</p>
      <p><strong>用户名：</strong>{{ username }}</p>
      <p><strong>角色：</strong>{{ role }}</p>

      <p class="tip" v-if="role === 'admin'">当前是管理员，后面会进入管理员管理界面。</p>
      <p class="tip" v-else-if="role === 'student'">当前是学生，后面会进入学生活动页面。</p>
      <p class="tip" v-else-if="role === 'organizer'">当前是组织者，后面会进入活动发布页面。</p>

      <button @click="logout">退出登录</button>
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
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card {
  width: 420px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  text-align: center;
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

button {
  margin-top: 20px;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: #f56c6c;
  color: white;
  cursor: pointer;
}

button:hover {
  background: #f78989;
}
</style>