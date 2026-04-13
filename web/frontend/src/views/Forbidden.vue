<template>
  <div class="page">
    <div class="card">
      <h1>403</h1>
      <h2>无权限访问</h2>

      <p class="desc">当前账号没有权限进入这个页面。</p>

      <p v-if="fromPath" class="path-text">
        被拦截页面：{{ fromPath }}
      </p>

      <div class="btn-group">
        <button class="blue-btn" @click="goHome">返回首页</button>
        <button class="gray-btn" @click="goBack">返回上一页</button>
        <button class="red-btn" @click="goLogin">重新登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

const fromPath = computed(() => route.query.from || '')

const goHome = () => {
  router.push('/home')
}

const goBack = () => {
  router.back()
}

const goLogin = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;

  /* ✅ 用你自己的403背景图 */
  background-image: url('../assets/403.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  display: flex;
  justify-content: center;
  align-items: center;
}

/* 🔥 半透明毛玻璃卡片 */
.card {
  width: 520px;

  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);

  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;

  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

h1 {
  margin: 0;
  font-size: 56px;
  color: #f56c6c;
}

h2 {
  margin: 12px 0 18px;
  font-size: 26px;
  color: #333;
}

.desc {
  color: #666;
  margin-bottom: 10px;
}

.path-text {
  color: #999;
  font-size: 14px;
  margin-bottom: 20px;
}

.btn-group {
  display: flex;
  justify-content: center;
  gap: 12px;
}

button {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
}

.blue-btn {
  background: #409eff;
}

.gray-btn {
  background: #909399;
}

.red-btn {
  background: #f56c6c;
}
</style>