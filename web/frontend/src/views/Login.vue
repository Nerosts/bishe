<template>
  <div class="login-page">
    <section class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <p class="hero-eyebrow">Campus Activity Platform</p>
        <h1 class="hero-title">校园活动与讲座报名平台</h1>
        <p class="hero-desc">
          面向校园活动、讲座、比赛与社团活动的统一管理平台。
          支持活动发布、报名审核、二维码签到、统计分析与 Excel 导出，
          用更轻量、更高效的方式完成活动全流程管理。
        </p>

        <div class="hero-feature-grid">
          <div class="feature-card glass-card">
            <div class="feature-icon">01</div>
            <div class="feature-title">统一活动管理</div>
            <div class="feature-text">
              支持讲座、比赛、社团活动等多种类别，统一发布、统一查看、统一管理。
            </div>
          </div>

          <div class="feature-card glass-card">
            <div class="feature-icon">02</div>
            <div class="feature-title">报名与审核</div>
            <div class="feature-text">
              学生在线报名，管理员或组织者进行审核，形成清晰可追踪的报名流程。
            </div>
          </div>

          <div class="feature-card glass-card">
            <div class="feature-icon">03</div>
            <div class="feature-title">签到与统计</div>
            <div class="feature-text">
              支持二维码签到、签到记录查看、报名数据统计和 Excel 导出。
            </div>
          </div>
        </div>

        <div class="scroll-tip">
          <span>向下滚动进入登录</span>
          <div class="scroll-line"></div>
        </div>
      </div>
    </section>

    <section class="login-section" ref="loginSectionRef">
      <div class="login-shell">
        <div class="login-panel glass-card">
          <div
            class="login-header reveal-bottom"
            :class="{ visible: hasEnteredLogin }"
          >
            <p class="login-eyebrow">User Login</p>
            <h2 class="login-title">欢迎回来</h2>
            <p class="login-subtitle">
              请输入账号和密码，进入对应角色的功能页面。
            </p>
          </div>

          <transition name="fade-slide">
            <div v-if="message" class="message-box">
              {{ message }}
            </div>
          </transition>

          <form class="login-form" @submit.prevent="handleLogin">
            <div
              class="input-group reveal-left"
              :class="{ visible: hasEnteredLogin }"
            >
              <label>账号</label>
              <input
                v-model="username"
                type="text"
                placeholder="请输入用户名"
                autocomplete="username"
              />
            </div>

            <div
              class="input-group reveal-right"
              :class="{ visible: hasEnteredLogin }"
            >
              <label>密码</label>
              <input
                v-model="password"
                type="password"
                placeholder="请输入密码"
                autocomplete="current-password"
              />
            </div>

            <div
              class="login-actions reveal-bottom delay-2"
              :class="{ visible: hasEnteredLogin }"
            >
              <button class="login-btn" type="submit" :disabled="loading">
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </div>
          </form>

          <div
            class="account-tip reveal-bottom delay-3"
            :class="{ visible: hasEnteredLogin }"
          >
            <div class="tip-title">账号角色说明</div>
            <div class="tip-grid">
              <div class="tip-item">
                <span class="role-pill role-admin">管理员</span>
                <span class="tip-text">审核报名、用户管理、统计分析</span>
              </div>
              <div class="tip-item">
                <span class="role-pill role-organizer">组织者</span>
                <span class="tip-text">发布活动、查看报名、导出名单</span>
              </div>
              <div class="tip-item">
                <span class="role-pill role-student">学生</span>
                <span class="tip-text">浏览活动、报名、签到、查看记录</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

const router = useRouter()

const username = ref('')
const password = ref('')
const message = ref('')
const loading = ref(false)

const loginSectionRef = ref(null)
const hasEnteredLogin = ref(false)

let observer = null

const clearMessageLater = () => {
  setTimeout(() => {
    message.value = ''
  }, 2500)
}

const handleLogin = async () => {
  if (!username.value || !password.value) {
    message.value = '请输入账号和密码'
    clearMessageLater()
    return
  }

  loading.value = true
  try {
    const res = await axios.post(`${API_BASE_URL}/login`, {
      username: username.value,
      password: password.value
    })

    const data = res.data || {}

    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('username', data.username)
    localStorage.setItem('role', data.role)

    message.value = '登录成功'
    setTimeout(() => {
      router.push('/home')
    }, 500)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      message.value = error.response.data.message
    } else {
      message.value = '登录失败'
    }
    clearMessageLater()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          hasEnteredLogin.value = true
        }
      })
    },
    {
      threshold: 0.2
    }
  )

  if (loginSectionRef.value) {
    observer.observe(loginSectionRef.value)
  }
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
:global(body) {
  background: #f5f5f7;
  color: #1d1d1f;
}

.login-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.06), transparent 24%),
    linear-gradient(180deg, #f5f5f7 0%, #f7f7f9 100%);
}

.hero-section {
  position: relative;
  min-height: 115vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(0, 113, 227, 0.12), transparent 18%),
    radial-gradient(circle at 80% 30%, rgba(0, 113, 227, 0.08), transparent 20%),
    radial-gradient(circle at 50% 80%, rgba(0, 113, 227, 0.05), transparent 18%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  width: min(1200px, calc(100% - 64px));
  margin: 0 auto;
  padding: 88px 0 120px;
}

.hero-eyebrow {
  margin: 0 0 14px;
  font-size: 13px;
  color: #6e6e73;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-title {
  margin: 0;
  max-width: 860px;
  font-size: clamp(46px, 7vw, 86px);
  line-height: 1.04;
  font-weight: 300;
  letter-spacing: -0.04em;
  color: #1d1d1f;
}

.hero-desc {
  margin: 28px 0 0;
  max-width: 860px;
  font-size: 19px;
  line-height: 2;
  color: #6e6e73;
  font-weight: 400;
}

.hero-feature-grid {
  margin-top: 56px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.05);
  border-radius: 24px;
}

.feature-card {
  padding: 28px;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 46px rgba(0, 0, 0, 0.08);
}

.feature-icon {
  font-size: 14px;
  color: #0071e3;
  margin-bottom: 18px;
  font-weight: 600;
}

.feature-title {
  font-size: 22px;
  font-weight: 300;
  line-height: 1.45;
  color: #1d1d1f;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.feature-text {
  font-size: 15px;
  line-height: 1.9;
  color: #6e6e73;
}

.scroll-tip {
  margin-top: 72px;
  display: inline-flex;
  flex-direction: column;
  gap: 14px;
  color: #6e6e73;
  font-size: 14px;
}

.scroll-line {
  width: 1px;
  height: 56px;
  background: linear-gradient(to bottom, rgba(0, 113, 227, 0.65), transparent);
  margin-left: 8px;
}

.login-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 80px 32px 120px;
  box-sizing: border-box;
}

.login-shell {
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-panel {
  width: min(760px, 100%);
  padding: 48px;
}

.login-header {
  margin-bottom: 28px;
}

.login-eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  color: #6e6e73;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.login-title {
  margin: 0;
  font-size: clamp(34px, 4vw, 48px);
  font-weight: 300;
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: #1d1d1f;
}

.login-subtitle {
  margin: 16px 0 0;
  font-size: 16px;
  line-height: 1.9;
  color: #6e6e73;
}

.message-box {
  margin-bottom: 22px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(234, 247, 238, 0.92);
  color: #146c43;
  font-size: 14px;
  line-height: 1.8;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group label {
  font-size: 14px;
  color: #6e6e73;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  height: 58px;
  padding: 0 18px;
  box-sizing: border-box;
  border: none;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: inset 0 0 0 1px rgba(29, 29, 31, 0.06);
  outline: none;
  font-size: 15px;
  color: #1d1d1f;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-group input:focus {
  box-shadow:
    inset 0 0 0 1px rgba(0, 113, 227, 0.35),
    0 0 0 4px rgba(0, 113, 227, 0.08);
  background: rgba(255, 255, 255, 0.96);
}

.login-actions {
  margin-top: 6px;
}

.login-btn {
  width: 100%;
  height: 56px;
  border: none;
  border-radius: 12px;
  background: #0071e3;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
  background: #0062c6;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.account-tip {
  margin-top: 30px;
  padding: 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.68);
}

.tip-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 16px;
}

.tip-grid {
  display: grid;
  gap: 14px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.role-admin {
  background: rgba(0, 113, 227, 0.12);
  color: #0071e3;
}

.role-organizer {
  background: rgba(52, 199, 89, 0.14);
  color: #1f8f42;
}

.role-student {
  background: rgba(245, 166, 35, 0.16);
  color: #bc7700;
}

.tip-text {
  font-size: 14px;
  color: #6e6e73;
  line-height: 1.8;
}

.reveal-left,
.reveal-right,
.reveal-bottom {
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.reveal-left {
  transform: translateX(-48px);
}

.reveal-right {
  transform: translateX(48px);
}

.reveal-bottom {
  transform: translateY(36px);
}

.reveal-left.visible,
.reveal-right.visible,
.reveal-bottom.visible {
  opacity: 1;
  transform: translate(0, 0);
}

.delay-2 {
  transition-delay: 0.12s;
}

.delay-3 {
  transition-delay: 0.22s;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 1023px) {
  .hero-feature-grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    width: min(100%, calc(100% - 32px));
  }

  .login-panel {
    padding: 32px 22px;
  }
}

@media (max-width: 767px) {
  .hero-section {
    min-height: 105vh;
  }

  .hero-content {
    padding: 64px 0 88px;
  }

  .hero-desc {
    font-size: 16px;
  }

  .login-section {
    padding: 48px 16px 80px;
  }

  .tip-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>