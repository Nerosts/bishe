<template>
  <div class="login-page">
    <div class="login-box">
      <h2>校园活动与讲座报名平台</h2>
      <p class="sub-title">用户登录</p>

      <input v-model="username" type="text" placeholder="请输入用户名" />
      <input v-model="password" type="password" placeholder="请输入密码" />

      <button @click="handleLogin">登录</button>

      <p class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const message = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    message.value = '请输入用户名和密码'
    return
  }

  try {
    const res = await axios.post('http://127.0.0.1:5000/login', {
      username: username.value,
      password: password.value
    })

    const data = res.data

    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('username', data.username)
    localStorage.setItem('role', data.role)

    message.value = '登录成功'

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
.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 360px;
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  text-align: center;
}

h2 {
  margin-bottom: 10px;
  color: #333;
}

.sub-title {
  color: #666;
  margin-bottom: 25px;
}

input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
}

button {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

button:hover {
  background: #66b1ff;
}

.message {
  margin-top: 15px;
  color: #e74c3c;
  min-height: 20px;
}
</style>