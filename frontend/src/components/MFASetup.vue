<template>
  <div class="mfa-setup">
    <div v-if="step === 'idle'" class="mfa-idle">
      <div class="mfa-status" :class="mfaEnabled ? 'status-on' : 'status-off'">
        <span class="mfa-icon">{{ mfaEnabled ? '🔐' : '🔓' }}</span>
        <div>
          <div class="mfa-title">双因子认证 (MFA)</div>
          <div class="mfa-desc">{{ mfaEnabled ? '已启用 TOTP 双因子认证' : '未启用，建议开启以增强安全性' }}</div>
        </div>
      </div>
      <button v-if="!mfaEnabled" class="btn-primary" @click="startSetup">开启 MFA</button>
      <button v-else class="btn-danger" @click="step = 'disable'">关闭 MFA</button>
    </div>

    <!-- 扫码绑定 -->
    <div v-if="step === 'setup'" class="mfa-setup-flow">
      <h3>扫描二维码</h3>
      <p class="mfa-guide">使用 Google Authenticator / Authy 扫描以下二维码：</p>
      <div class="qr-wrap">
        <img v-if="qrCode" :src="qrCode" alt="MFA QR Code" class="qr-img" />
        <div v-else class="qr-loading skeleton" style="width:200px;height:200px;"></div>
      </div>
      <div class="manual-key">
        <span class="key-label">手动输入密钥：</span>
        <code class="key-code">{{ secret }}</code>
        <button class="btn-copy" @click="copySecret">📋</button>
      </div>
      <div class="verify-section">
        <p>输入 App 中显示的 6 位验证码确认绑定：</p>
        <input
          v-model="code"
          class="code-input"
          placeholder="000000"
          maxlength="6"
          @keydown.enter="confirmMfa"
        />
        <div class="btn-row">
          <button class="btn-primary" :disabled="code.length < 6 || loading" @click="confirmMfa">
            {{ loading ? '验证中...' : '确认绑定' }}
          </button>
          <button class="btn-secondary" @click="step = 'idle'">取消</button>
        </div>
      </div>
    </div>

    <!-- 关闭 MFA -->
    <div v-if="step === 'disable'" class="mfa-disable-flow">
      <h3>关闭 MFA</h3>
      <p>请输入当前 TOTP 验证码以确认：</p>
      <input v-model="code" class="code-input" placeholder="000000" maxlength="6" />
      <div class="btn-row">
        <button class="btn-danger" :disabled="code.length < 6 || loading" @click="disableMfa">
          {{ loading ? '处理中...' : '确认关闭' }}
        </button>
        <button class="btn-secondary" @click="step = 'idle'">取消</button>
      </div>
    </div>

    <!-- 结果 -->
    <div v-if="message" :class="['mfa-msg', msgType]">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import http from '@/api/http.js'

const mfaEnabled = ref(false)
const step    = ref('idle')
const qrCode  = ref('')
const secret  = ref('')
const code    = ref('')
const loading = ref(false)
const message = ref('')
const msgType = ref('success')

async function startSetup() {
  loading.value = true
  try {
    const data = await http.post('/api/v1/auth/security/mfa/setup')
    qrCode.value = data.qr_code
    secret.value = data.secret
    step.value   = 'setup'
  } catch (e) {
    showMsg(e.message || '获取 QR 码失败', 'error')
  } finally {
    loading.value = false
  }
}

async function confirmMfa() {
  if (code.value.length < 6) return
  loading.value = true
  try {
    await http.post('/api/v1/auth/security/mfa/confirm', { code: code.value })
    mfaEnabled.value = true
    step.value = 'idle'
    code.value = ''
    showMsg('MFA 绑定成功 🎉', 'success')
  } catch (e) {
    showMsg(e.message || '验证码错误', 'error')
  } finally {
    loading.value = false
  }
}

async function disableMfa() {
  if (code.value.length < 6) return
  loading.value = true
  try {
    await http.post('/api/v1/auth/security/mfa/disable', { code: code.value })
    mfaEnabled.value = false
    step.value = 'idle'
    code.value = ''
    showMsg('MFA 已关闭', 'success')
  } catch (e) {
    showMsg(e.message || '验证码错误', 'error')
  } finally {
    loading.value = false
  }
}

function copySecret() {
  navigator.clipboard?.writeText(secret.value)
  showMsg('密钥已复制', 'success')
}

function showMsg(msg, type = 'success') {
  message.value = msg
  msgType.value = type
  setTimeout(() => { message.value = '' }, 4000)
}
</script>

<style scoped>
.mfa-setup { display: flex; flex-direction: column; gap: 16px; }

.mfa-status {
  display: flex; align-items: center; gap: 14px;
  padding: 16px; border-radius: var(--radius);
  border: 1px solid var(--c-border);
}
.status-on  { background: rgba(16,185,129,.07); border-color: rgba(16,185,129,.3); }
.status-off { background: rgba(239,68,68,.05);  border-color: rgba(239,68,68,.2); }
.mfa-icon   { font-size: 2rem; }
.mfa-title  { font-weight: 600; color: var(--c-text); }
.mfa-desc   { font-size: .875rem; color: var(--c-text-muted); margin-top: 2px; }

.mfa-setup-flow, .mfa-disable-flow {
  display: flex; flex-direction: column; gap: 14px;
}
.mfa-guide { color: var(--c-text-muted); font-size: .9rem; }
.qr-wrap   { display: flex; justify-content: center; }
.qr-img    { width: 200px; height: 200px; border-radius: 8px; border: 1px solid var(--c-border); }

.manual-key {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; background: var(--c-bg-card2);
  border-radius: 8px; flex-wrap: wrap;
}
.key-label  { color: var(--c-text-muted); font-size: .875rem; }
.key-code   { font-family: monospace; color: var(--c-primary); font-size: .875rem; letter-spacing: .1em; }
.btn-copy   { background: none; border: none; cursor: pointer; font-size: 1rem; }

.verify-section { display: flex; flex-direction: column; gap: 10px; }
.code-input {
  width: 160px; text-align: center; letter-spacing: .4em;
  font-size: 1.5rem; font-family: monospace; font-weight: 700;
  padding: 10px; border-radius: 8px;
  border: 2px solid var(--c-border); background: var(--c-bg-card2);
  color: var(--c-text); outline: none;
  transition: border-color .15s;
}
.code-input:focus { border-color: var(--c-primary); }

.btn-row  { display: flex; gap: 10px; flex-wrap: wrap; }

.btn-primary, .btn-secondary, .btn-danger {
  padding: 8px 20px; border: none; border-radius: 8px;
  font-size: .9375rem; font-weight: 600; cursor: pointer;
  transition: all .15s;
}
.btn-primary   { background: var(--c-primary); color: #fff; }
.btn-primary:hover { background: var(--c-primary-d); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }
.btn-secondary { background: var(--c-bg-card2); color: var(--c-text-muted); border: 1px solid var(--c-border); }
.btn-danger    { background: var(--c-danger); color: #fff; }
.btn-danger:hover { opacity: .85; }
.btn-danger:disabled { opacity: .5; cursor: not-allowed; }

.mfa-msg { padding: 10px 16px; border-radius: 8px; font-size: .875rem; font-weight: 500; }
.mfa-msg.success { background: rgba(16,185,129,.12); color: var(--c-success); border: 1px solid rgba(16,185,129,.25); }
.mfa-msg.error   { background: rgba(239,68,68,.1);   color: var(--c-danger);  border: 1px solid rgba(239,68,68,.2); }
</style>
