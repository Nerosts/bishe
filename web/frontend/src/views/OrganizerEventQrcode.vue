<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>活动签到二维码</h1>
        <p class="sub">组织者可查看本活动的签到二维码与签到链接</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goMyEvents">返回我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="message-box" v-if="message">
      {{ message }}
    </div>

    <div class="card" v-if="eventInfo">
      <h2>{{ eventInfo.event_title }}</h2>
      <p><strong>活动ID：</strong>{{ eventInfo.event_id }}</p>
      <p><strong>说明：</strong>请将下方二维码提供给已审核通过的学生进行签到。</p>
      <p><strong>当前自动识别IP：</strong>{{ eventInfo.current_ip }}</p>

      <div class="qrcode-box" v-if="eventInfo.qrcode_image_url">
        <img :src="eventInfo.qrcode_image_url" alt="签到二维码" />
      </div>

      <div class="link-box">
        <label>签到链接</label>
        <input :value="eventInfo.checkin_url" readonly />
      </div>

      <div class="btn-row">
        <button class="purple-btn" @click="openQrcodeImage">打开二维码图片</button>
        <button class="blue-btn" @click="copyLink">复制签到链接</button>
        <button class="green-btn" @click="refreshQrcode">刷新二维码</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const route = useRoute()

const message = ref('')
const eventInfo = ref(null)

const loadQrcode = async () => {
  const role = localStorage.getItem('role')
  const eventId = route.params.id

  if (role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/events/${eventId}/qrcode`)
    eventInfo.value = res.data
    message.value = ''
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '获取签到二维码失败'
    }
  }
}

const refreshQrcode = async () => {
  await loadQrcode()
  message.value = '二维码已刷新为当前网络环境地址'
}

const openQrcodeImage = () => {
  if (eventInfo.value && eventInfo.value.qrcode_image_url) {
    window.open(eventInfo.value.qrcode_image_url, '_blank')
  }
}

const copyLink = async () => {
  if (!eventInfo.value || !eventInfo.value.checkin_url) {
    message.value = '没有可复制的签到链接'
    return
  }

  try {
    await navigator.clipboard.writeText(eventInfo.value.checkin_url)
    message.value = '签到链接已复制'
  } catch (error) {
    message.value = '复制失败，请手动复制'
  }
}

const goMyEvents = () => {
  router.push('/organizer/my-events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  loadQrcode()
})
</script>

<style scoped>
.page {
  padding: 30px;
  background: #f5f7fa;
  min-height: 100vh;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.top-bar h1 {
  margin: 0;
  color: #333;
}

.sub {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  cursor: pointer;
  color: white;
}

.gray-btn {
  background: #909399;
}

.gray-btn:hover {
  background: #a6a9ad;
}

.red-btn {
  background: #f56c6c;
}

.red-btn:hover {
  background: #f78989;
}

.blue-btn {
  background: #409eff;
}

.blue-btn:hover {
  background: #66b1ff;
}

.purple-btn {
  background: #8b5cf6;
}

.purple-btn:hover {
  background: #a78bfa;
}

.green-btn {
  background: #67c23a;
}

.green-btn:hover {
  background: #85ce61;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 18px;
}

.card {
  max-width: 760px;
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.card h2 {
  margin-top: 0;
  color: #333;
}

.card p {
  color: #555;
  margin: 10px 0;
}

.qrcode-box {
  margin: 24px 0;
  text-align: center;
}

.qrcode-box img {
  width: 280px;
  max-width: 100%;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 10px;
  background: white;
}

.link-box {
  margin-top: 20px;
}

.link-box label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.link-box input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
}

.btn-row {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>