<template>
  <div class="page">
    <div class="login-card">
      <h1>校园活动与讲座报名平台</h1>
      <p class="sub-title">用户登录</p>

      <div class="form-item">
        <input v-model="username" type="text" placeholder="请输入用户名" />
      </div>

      <div class="form-item">
        <input v-model="password" type="password" placeholder="请输入密码" />
      </div>

      <button class="login-btn" @click="handleLogin">登录</button>

      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const message = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    message.value = '请输入用户名和密码'
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/login`, {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('user_id', res.data.user_id)
    localStorage.setItem('username', res.data.username)
    localStorage.setItem('role', res.data.role)

    const redirectPath = route.query.redirect

    if (redirectPath) {
      router.push(redirectPath)
      return
    }

    router.push('/home')
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '登录失败，请检查后端是否启动'
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 420px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
  text-align: center;
}

h1 {
  font-size: 22px;
  color: #333;
  margin-bottom: 16px;
}

.sub-title {
  color: #666;
  margin-bottom: 24px;
}

.form-item {
  margin-bottom: 16px;
}

input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

input:focus {
  border-color: #409eff;
}

.login-btn {
  width: 100%;
  border: none;
  background: #409eff;
  color: white;
  font-size: 15px;
  padding: 14px;
  border-radius: 8px;
  cursor: pointer;
}

.login-btn:hover {
  background: #66b1ff;
}

.message {
  margin-top: 16px;
  color: #f56c6c;
}
</style>