<template>
  <div class="page">
    <div class="card">
      <h1>404</h1>
      <h2>页面不存在</h2>

      <p class="desc">你访问的页面地址不存在，请检查路径。</p>

      <div class="btn-group">
        <button class="blue-btn" @click="goHome">返回首页</button>
        <button class="gray-btn" @click="goLogin">返回登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  const userId = localStorage.getItem('user_id')
  if (userId) {
    router.push('/home')
  } else {
    router.push('/login')
  }
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;

  /* ✅ 用你自己的404背景图 */
  background-image: url('../assets/404.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  display: flex;
  justify-content: center;
  align-items: center;
}

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
  color: #909399;
}

h2 {
  margin: 12px 0 18px;
  font-size: 26px;
  color: #333;
}

.desc {
  color: #666;
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
</style>