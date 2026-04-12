<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>发布活动</h1>
        <p class="sub-title">组织者可在这里创建新的校园活动</p>
      </div>

      <div class="top-buttons">
        <button class="green-btn" @click="goMyEvents">我的活动</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="form-card">
      <div v-if="message" class="message-box">
        {{ message }}
      </div>

      <div class="form-item">
        <label>活动标题</label>
        <input v-model="form.title" type="text" placeholder="请输入活动标题" />
      </div>

      <div class="form-item">
        <label>活动类别</label>
        <select v-model="form.category">
          <option value="">请选择活动类别</option>
          <option value="讲座">讲座</option>
          <option value="比赛">比赛</option>
          <option value="社团活动">社团活动</option>
        </select>
      </div>

      <div class="form-item">
        <label>活动地点</label>
        <input v-model="form.location" type="text" placeholder="请输入活动地点" />
      </div>

      <div class="form-item">
        <label>开始时间</label>
        <input v-model="form.start_time" type="text" placeholder="格式：2026-04-20 14:00:00" />
      </div>

      <div class="form-item">
        <label>人数上限</label>
        <input v-model="form.max_participants" type="number" placeholder="请输入人数上限" />
      </div>

      <div class="form-item">
        <label>活动描述</label>
        <textarea v-model="form.description" rows="5" placeholder="请输入活动描述"></textarea>
      </div>

      <button class="submit-btn" @click="submitForm">发布活动</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const message = ref('')

const form = reactive({
  title: '',
  category: '',
  location: '',
  start_time: '',
  max_participants: '',
  description: ''
})

const submitForm = async () => {
  const organizerId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')

  if (!organizerId || role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.post(`${API_BASE_URL}/events`, {
      ...form,
      organizer_id: Number(organizerId)
    })

    message.value = res.data.message

    form.title = ''
    form.category = ''
    form.location = ''
    form.start_time = ''
    form.max_participants = ''
    form.description = ''
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '发布活动失败'
    }
  }
}

const goMyEvents = () => {
  router.push('/organizer/my-events')
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
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30px;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  color: #333;
}

.sub-title {
  margin-top: 8px;
  color: #666;
}

.top-buttons {
  display: flex;
  gap: 12px;
}

.form-card {
  max-width: 760px;
  background: white;
  border-radius: 16px;
  padding: 26px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.form-item {
  margin-bottom: 18px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: bold;
}

.form-item input,
.form-item textarea,
.form-item select {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.submit-btn {
  width: 100%;
  border: none;
  border-radius: 8px;
  padding: 12px;
  background: #e6a23c;
  color: white;
  cursor: pointer;
  font-size: 15px;
}

.submit-btn:hover {
  background: #ebb563;
}

.green-btn {
  background: #14b8a6;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
}

.green-btn:hover {
  background: #2dd4bf;
}

.gray-btn {
  background: #909399;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
}

.gray-btn:hover {
  background: #a6a9ad;
}

.red-btn {
  background: #f56c6c;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
}

.red-btn:hover {
  background: #f78989;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>