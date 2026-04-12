<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>发布活动</h1>
        <p class="sub">组织者可在这里创建新的校园活动</p>
      </div>

      <div class="top-buttons">
        <button class="cyan-btn" @click="goMyEvents">我的活动</button>
        <button class="gray-btn" @click="goHome">返回首页</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="form-card">
      <div class="form-item">
        <label>活动标题</label>
        <input v-model="form.title" type="text" placeholder="请输入活动标题" />
      </div>

      <div class="form-item">
        <label>活动类别</label>
        <input v-model="form.category" type="text" placeholder="如：讲座 / 比赛 / 社团活动" />
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
        <textarea v-model="form.description" placeholder="请输入活动描述"></textarea>
      </div>

      <button class="orange-btn submit-btn" @click="submitEvent">发布活动</button>

      <div class="message-box" v-if="message">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

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

const submitEvent = async () => {
  const organizerId = localStorage.getItem('user_id')

  if (
    !form.title ||
    !form.category ||
    !form.location ||
    !form.start_time ||
    !form.max_participants
  ) {
    message.value = '请填写完整信息'
    return
  }

  try {
    const res = await axios.post('http://127.0.0.1:5000/events', {
      title: form.title,
      category: form.category,
      location: form.location,
      start_time: form.start_time,
      max_participants: form.max_participants,
      description: form.description,
      organizer_id: organizerId
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
      message.value = '活动发布失败'
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

onMounted(() => {
  const role = localStorage.getItem('role') || ''
  if (role !== 'organizer') {
    router.push('/login')
  }
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

.form-card {
  max-width: 720px;
  background: white;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
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
.form-item textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
}

.form-item textarea {
  min-height: 120px;
  resize: vertical;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
}

.message-box {
  background: #fff3cd;
  color: #856404;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 18px;
}
</style>