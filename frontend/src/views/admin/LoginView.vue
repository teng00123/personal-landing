<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-icon">⚡</div>
      <h1 class="login-title">后台登录</h1>
      <p class="text-muted" style="font-size:.875rem;margin-bottom:28px">Personal Portfolio CMS</p>

      <!-- Step 1: 用户名 + 密码 -->
      <el-form v-if="step === 'password'" :model="form" @submit.prevent="submit">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            autocomplete="current-password"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          style="width:100%"
          @click="submit"
        >
          登 录
        </el-button>
      </el-form>

      <!-- Step 2: MFA TOTP 验证码 -->
      <div v-else-if="step === 'mfa'" class="mfa-step">
        <div class="mfa-hint">
          <span class="mfa-icon-sm">🔐</span>
          请输入 Authenticator App 中的 6 位验证码
        </div>
        <input
          ref="codeInputRef"
          v-model="mfaCode"
          class="code-input"
          placeholder="000000"
          maxlength="6"
          inputmode="numeric"
          autocomplete="one-time-code"
          @keyup.enter="submitMfa"
        />
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="mfaCode.length < 6"
          style="width:100%;margin-top:12px"
          @click="submitMfa"
        >
          {{ loading ? '验证中...' : '验 证' }}
        </el-button>
        <p class="back-link" @click="backToPassword">← 使用其他账号登录</p>
      </div>
    </div>

    <p style="margin-top:20px;font-size:.8125rem;color:#64748b">
      <router-link to="/" style="color:#64748b">← 返回主页</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth.js'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const loading      = ref(false)
const form         = ref({ username: '', password: '' })
const step         = ref('password')   // 'password' | 'mfa'
const mfaCode      = ref('')
const mfaToken     = ref('')
const codeInputRef = ref(null)

async function submit() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const data = await auth.login(form.value.username, form.value.password)

    if (data?.mfa_required) {
      // 进入 MFA 第二步
      mfaToken.value = data.mfa_token
      step.value     = 'mfa'
      mfaCode.value  = ''
      await nextTick()
      codeInputRef.value?.focus()
      return
    }

    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/admin/dashboard'
    router.push(decodeURIComponent(redirect))
  } catch (e) {
    ElMessage.error(e?.detail || '用户名或密码错误')
  } finally {
    loading.value = false
  }
}

async function submitMfa() {
  if (mfaCode.value.length < 6) return
  loading.value = true
  try {
    await auth.loginMfa(mfaToken.value, mfaCode.value)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/admin/dashboard'
    router.push(decodeURIComponent(redirect))
  } catch (e) {
    ElMessage.error(e?.detail || '验证码错误或已过期')
    mfaCode.value = ''
    codeInputRef.value?.focus()
  } finally {
    loading.value = false
  }
}

function backToPassword() {
  step.value    = 'password'
  mfaCode.value = ''
  mfaToken.value = ''
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: radial-gradient(ellipse at center, rgba(59,130,246,.12) 0%, transparent 70%);
}
.login-box {
  background: #1e293b; border: 1px solid #334155; border-radius: 16px;
  padding: 48px 40px; width: 100%; max-width: 400px; text-align: center;
}
.login-icon  { font-size: 2.75rem; margin-bottom: 12px; }
.login-title { font-size: 1.625rem; font-weight: 800; color: #f1f5f9; margin-bottom: 6px; }
.el-form-item { margin-bottom: 14px; }

/* MFA step */
.mfa-step   { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.mfa-hint   { display: flex; align-items: center; gap: 8px; color: #94a3b8; font-size: .9rem; text-align: left; }
.mfa-icon-sm { font-size: 1.25rem; }
.code-input {
  width: 180px; text-align: center; letter-spacing: .5em;
  font-size: 1.75rem; font-family: monospace; font-weight: 700;
  padding: 12px 8px; border-radius: 10px;
  border: 2px solid #334155; background: #0f172a;
  color: #f1f5f9; outline: none;
  transition: border-color .15s;
}
.code-input:focus { border-color: #3b82f6; }
.back-link {
  font-size: .8125rem; color: #64748b; cursor: pointer; margin-top: 4px;
}
.back-link:hover { color: #94a3b8; }
</style>
