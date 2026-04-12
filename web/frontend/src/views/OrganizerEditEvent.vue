<template>
  <div class="page">
    <div class="top-bar">
      <div>
        <h1>编辑活动</h1>
        <p class="sub-title">组织者可修改自己发布的活动</p>
      </div>

      <div class="top-buttons">
        <button class="gray-btn" @click="goBack">返回我的活动</button>
        <button class="red-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="form-card" v-if="formLoaded">
      <div v-if="message" class="message-box">
        {{ message }}
      </div>

      <div class="form-item">
        <label>活动标题</label>
        <input v-model="form.title" type="text" />
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
        <input v-model="form.location" type="text" />
      </div>

      <div class="form-item">
        <label>开始时间</label>
        <input v-model="form.start_time" type="text" />
      </div>

      <div class="form-item">
        <label>人数上限</label>
        <input v-model="form.max_participants" type="number" />
      </div>

      <div class="form-item">
        <label>活动描述</label>
        <textarea v-model="form.description" rows="5"></textarea>
      </div>

      <button class="submit-btn" @click="submitForm">保存修改</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()
const route = useRoute()

const message = ref('')
const formLoaded = ref(false)

const form = reactive({
  title: '',
  category: '',
  location: '',
  start_time: '',
  max_participants: '',
  description: ''
})

const loadEvent = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/events/${route.params.id}`)
    form.title = res.data.title || ''
    form.category = res.data.category || ''
    form.location = res.data.location || ''
    form.start_time = res.data.start_time || ''
    form.max_participants = res.data.max_participants || ''
    form.description = res.data.description || ''
    formLoaded.value = true
  } catch (error) {
    message.value = '获取活动信息失败'
  }
}

const submitForm = async () => {
  const organizerId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')

  if (!organizerId || role !== 'organizer') {
    router.push('/login')
    return
  }

  try {
    const res = await axios.put(
      `${API_BASE_URL}/organizer/${organizerId}/events/${route.params.id}`,
      { ...form }
    )
    message.value = res.data.message
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '修改活动失败'
    }
  }
}

const goBack = () => {
  router.push('/organizer/my-events')
}

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(() => {
  loadEvent()
})
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
  background: #409eff;
  color: white;
  cursor: pointer;
  font-size: 15px;
}

.submit-btn:hover {
  background: #66b1ff;
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