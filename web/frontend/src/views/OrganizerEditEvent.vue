<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>编辑活动</h1>
        <p class="sub">组织者可以修改自己发布的活动信息</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goMyEvents">返回我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="form-card">
      <div class="message-box" v-if="message">
        {{ message }}
      </div>

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
        <label>活动状态</label>
        <input v-model="form.status" type="text" placeholder="如：报名中 / 已结束" />
      </div>

      <div class="form-item">
        <label>活动描述</label>
        <textarea v-model="form.description" placeholder="请输入活动描述"></textarea>
      </div>

      <button class="blue-btn submit-btn" @click="submitEdit">保存修改</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const message = ref('')

const form = reactive({
  title: '',
  category: '',
  location: '',
  start_time: '',
  max_participants: '',
  description: '',
  status: ''
})

const loadEvent = async () => {
  const eventId = route.params.id

  try {
    const res = await axios.get(`http://127.0.0.1:5000/events/${eventId}`)
    form.title = res.data.title || ''
    form.category = res.data.category || ''
    form.location = res.data.location || ''
    form.start_time = res.data.start_time || ''
    form.max_participants = res.data.max_participants || ''
    form.description = res.data.description || ''
    form.status = res.data.status || ''
  } catch (error) {
    message.value = '加载活动信息失败'
  }
}

const submitEdit = async () => {
  const organizerId = localStorage.getItem('user_id')
  const eventId = route.params.id

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
    const res = await axios.put(`http://127.0.0.1:5000/organizer/${organizerId}/events/${eventId}`, {
      title: form.title,
      category: form.category,
      location: form.location,
      start_time: form.start_time,
      max_participants: form.max_participants,
      description: form.description,
      status: form.status
    })

    message.value = res.data.message

    setTimeout(() => {
      router.push('/organizer/my-events')
    }, 800)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '活动修改失败'
    }
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
  const role = localStorage.getItem('role')
  if (role !== 'organizer') {
    router.push('/login')
    return
  }

  loadEvent()
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
  margin-bottom: 18px;
}
</style>