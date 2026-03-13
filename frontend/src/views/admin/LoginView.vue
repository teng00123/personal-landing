<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-icon">⚡</div>
      <h1 class="login-title">后台登录</h1>
      <p class="text-muted" style="font-size:.875rem;margin-bottom:28px">Personal Portfolio CMS</p>

      <el-form :model="form" @submit.prevent="submit">
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

      <p style="margin-top:20px;font-size:.8125rem;color:#64748b">
        <router-link to="/" style="color:#64748b">← 返回主页</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth.js'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const loading = ref(false)
const form    = ref({ username: '', password: '' })

async function submit() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/admin/dashboard'
    router.push(decodeURIComponent(redirect))
  } catch (e) {
    ElMessage.error(e?.detail || '用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(ellipse at center, rgba(59,130,246,.12) 0%, transparent 70%);
}
.login-box {
  background: #1e293b; border: 1px solid #334155; border-radius: 16px;
  padding: 48px 40px; width: 100%; max-width: 400px; text-align: center;
}
.login-icon  { font-size: 2.75rem; margin-bottom: 12px; }
.login-title { font-size: 1.625rem; font-weight: 800; color: #f1f5f9; margin-bottom: 6px; }
.el-form-item { margin-bottom: 14px; }
</style>
