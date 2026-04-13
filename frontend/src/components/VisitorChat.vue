<template>
  <!-- 浮动触发按钮 -->
  <div class="visitor-chat-root">
    <transition name="chat-bounce">
      <div v-if="!isOpen" class="chat-fab-wrap">
        <!-- Tooltip 气泡 -->
        <transition name="tooltip-fade">
          <div class="chat-tooltip" v-if="showTooltip">
            <span>👋 有任何问题，随时问我！</span>
            <button class="tooltip-close" @click.stop="dismissTooltip">✕</button>
          </div>
        </transition>
        <!-- FAB 按钮 -->
        <button
          class="chat-fab"
          @click="openChat"
          aria-label="和 AI 聊聊"
        >
          <span class="fab-glow"></span>
          <span class="fab-icon">🤖</span>
          <span class="fab-label">AI 助手</span>
          <span class="fab-dot" v-if="showTooltip"></span>
        </button>
      </div>
    </transition>

    <!-- 聊天面板 -->
    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-panel" role="dialog" aria-label="AI 助手对话">
        <!-- Header -->
        <div class="chat-header">
          <div class="chat-header-info">
            <div class="chat-avatar">🤖</div>
            <div>
              <div class="chat-name">AI 助手</div>
              <div class="chat-status">
                <span class="status-dot" :class="{ thinking: isStreaming }"></span>
                {{ isStreaming ? '正在思考…' : '在线' }}
              </div>
            </div>
          </div>
          <button class="chat-close" @click="closeChat" aria-label="关闭">✕</button>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesEl">
          <!-- 欢迎语 -->
          <div class="msg msg-ai welcome-msg">
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble">
              👋 你好！我是博主的专属 AI 助手，了解他的技能、项目和所有文章。有什么想知道的？
              <div class="quick-questions">
                <button
                  v-for="q in quickQuestions"
                  :key="q"
                  class="quick-btn"
                  @click="sendQuick(q)"
                  :disabled="isStreaming"
                >{{ q }}</button>
              </div>
            </div>
          </div>

          <!-- 对话消息 -->
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="msg"
            :class="[msg.role === 'user' ? 'msg-user' : 'msg-ai', { 'msg-error': msg.isError }]"
          >
            <div class="msg-avatar" v-if="msg.role === 'ai'">🤖</div>
            <div class="msg-bubble">
              <div v-html="renderContent(msg.content)"></div>
              <button
                v-if="msg.canRetry"
                class="retry-btn"
                @click="retryMessage(msg)"
                :disabled="isStreaming"
              >
                🔄 重试
              </button>
            </div>
            <div class="msg-avatar user-avatar" v-if="msg.role === 'user'">你</div>
          </div>

          <!-- 流式输出中的消息 -->
          <div v-if="isStreaming" class="msg msg-ai">
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble streaming" v-html="renderContent(streamingText) || '<span class=\'typing-dots\'><span></span><span></span><span></span></span>'"></div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-input-area">
          <textarea
            ref="inputEl"
            v-model="inputText"
            class="chat-input"
            :placeholder="isStreaming ? 'AI 正在回复…' : '输入你的问题…'"
            :disabled="isStreaming"
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResize"
          ></textarea>
          <button
            class="send-btn"
            :disabled="!inputText.trim() || isStreaming"
            @click="sendMessage"
            aria-label="发送"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>

        <div class="chat-footer">按 Enter 发送 · Shift+Enter 换行</div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'

const isOpen = ref(false)
const hasOpened = ref(false)
const isStreaming = ref(false)

// Tooltip 逻辑
const TOOLTIP_KEY = 'vc_tooltip_dismissed'
const showTooltip = ref(false)

function dismissTooltip() {
  showTooltip.value = false
  localStorage.setItem(TOOLTIP_KEY, '1')
}

onMounted(() => {
  if (!localStorage.getItem(TOOLTIP_KEY)) {
    setTimeout(() => { showTooltip.value = true }, 2000)
  }
})
const inputText = ref('')
const streamingText = ref('')
const messages = ref([])
const messagesEl = ref(null)
const inputEl = ref(null)

const quickQuestions = [
  '作者擅长哪些技术？',
  '有哪些推荐的文章？',
  '做过哪些项目？',
]

function openChat() {
  isOpen.value = true
  hasOpened.value = true
  showTooltip.value = false
  nextTick(() => inputEl.value?.focus())
}

function closeChat() {
  isOpen.value = false
}

function _buildErrorMessage(type) {
  switch (type) {
    case 'network':
      return '😔 网络连接不稳定，请检查网络后重试。'
    case 'openai_unavailable':
      return '🤖 AI 服务暂时不可用（可能 OpenAI API 不通）。<br>您可以通过其他方式联系博主：<br>· GitHub: <a href="https://github.com/teng00123" target="_blank">@teng00123</a><br>· Email: 页面底部有联系方式'
    default:
      return '😞 抱歉，出了点小问题。请稍后重试或直接联系博主。'
  }
}

function retryMessage(msg) {
  if (!msg.canRetry || !msg.retryQuestion) return
  // 移除错误消息，重新发送
  const idx = messages.value.indexOf(msg)
  if (idx > -1) messages.value.splice(idx, 1)
  sendAsk(msg.retryQuestion)
}

function renderContent(text) {
  if (!text) return ''
  // 简单 markdown：粗体、代码、换行
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

async function scrollBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function sendQuick(q) {
  inputText.value = q
  await sendMessage()
}

async function sendMessage() {
  const question = inputText.value.trim()
  if (!question || isStreaming.value) return

  // 推入用户消息
  messages.value.push({ role: 'user', content: question })
  inputText.value = ''
  if (inputEl.value) {
    inputEl.value.style.height = 'auto'
  }
  await scrollBottom()

  // 开始流式请求
  isStreaming.value = true
  streamingText.value = ''
  let errorOccurred = false
  let errorType = 'generic'  // 'generic' | 'network' | 'openai_unavailable'

  try {
    const res = await fetch('/api/v1/ai/chat/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })

    if (!res.ok) {
      // 判断错误类型
      if (res.status === 503 || res.status === 502) {
        errorType = 'openai_unavailable'
      } else if (res.status >= 500) {
        errorType = 'generic'
      }
      throw new Error(`HTTP ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() // 保留最后一个不完整的行

      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (data === '[DONE]') break
        if (data.startsWith('[ERROR]')) {
          errorOccurred = true
          const errMsg = data.slice(7).trim()
          // 判断是否 OpenAI 不可用
          if (errMsg.includes('OpenAI') || errMsg.includes('API') || errMsg.includes('timeout')) {
            errorType = 'openai_unavailable'
          }
          streamingText.value = errMsg || 'AI 服务暂时不可用，请稍后重试'
          break
        }
        // 反转义换行
        streamingText.value += data.replace(/\\n/g, '\n')
        await scrollBottom()
      }
    }

    // 流结束，把 streaming 内容固化为消息
    if (streamingText.value && !errorOccurred) {
      messages.value.push({ role: 'ai', content: streamingText.value })
    } else if (errorOccurred) {
      // 流式输出中错误，添加错误消息
      messages.value.push({
        role: 'ai',
        content: _buildErrorMessage(errorType),
        isError: true,
        canRetry: true,
        retryQuestion: question,
      })
    }
  } catch (err) {
    // 网络错误或 fetch 失败
    if (err.name === 'TypeError' || err.message.includes('fetch')) {
      errorType = 'network'
    }
    messages.value.push({
      role: 'ai',
      content: _buildErrorMessage(errorType),
      isError: true,
      canRetry: true,
      retryQuestion: question,
    })
  } finally {
    isStreaming.value = false
    streamingText.value = ''
    await scrollBottom()
    nextTick(() => inputEl.value?.focus())
  }
}
</script>

<style scoped>
.visitor-chat-root {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 9999;
  font-family: var(--font-sans, system-ui, sans-serif);
}

/* ── FAB 包裹（含 tooltip） ── */
.chat-fab-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

/* ── FAB 按钮（胶囊形，更醒目） ── */
.chat-fab {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 22px 14px 16px;
  border-radius: 50px;
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  border: none;
  cursor: pointer;
  color: #fff;
  font-size: .9375rem;
  font-weight: 700;
  letter-spacing: .02em;
  box-shadow: 0 6px 24px rgba(91,141,238,.5), 0 2px 8px rgba(0,0,0,.15);
  transition: transform .2s ease, box-shadow .2s ease;
  white-space: nowrap;
}
.chat-fab:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 12px 36px rgba(91,141,238,.6), 0 4px 12px rgba(0,0,0,.2);
}

/* 光晕呼吸动画 */
.fab-glow {
  position: absolute;
  inset: -2px;
  border-radius: 50px;
  background: linear-gradient(135deg, #5b8dee, #8b6cf7);
  opacity: .4;
  filter: blur(10px);
  animation: glow-pulse 2.5s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}
@keyframes glow-pulse {
  0%, 100% { opacity: .3; transform: scale(1); }
  50%       { opacity: .6; transform: scale(1.06); }
}

.fab-icon { font-size: 22px; line-height: 1; flex-shrink: 0; }
.fab-label { letter-spacing: .03em; }

/* 红点提示 */
.fab-dot {
  position: absolute;
  top: 8px; right: 10px;
  width: 9px; height: 9px;
  background: #ff4d4f;
  border-radius: 50%;
  border: 2px solid #fff;
  animation: dot-pulse 1.8s ease-in-out infinite;
}
@keyframes dot-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.35); opacity: .7; }
}

/* ── Tooltip 气泡 ── */
.chat-tooltip {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--c-bg-card, #fff);
  border: 1px solid rgba(91,141,238,.25);
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(0,0,0,.12);
  font-size: .8125rem;
  color: var(--c-text, #1a2035);
  max-width: 220px;
  line-height: 1.45;
}
.chat-tooltip::after {
  content: '';
  position: absolute;
  bottom: -7px; right: 24px;
  width: 12px; height: 12px;
  background: var(--c-bg-card, #fff);
  border-right: 1px solid rgba(91,141,238,.25);
  border-bottom: 1px solid rgba(91,141,238,.25);
  transform: rotate(45deg);
}
.tooltip-close {
  background: none; border: none;
  color: var(--c-text-muted, #8899b0);
  cursor: pointer; font-size: 12px;
  padding: 0; flex-shrink: 0; line-height: 1;
  transition: color .15s;
}
.tooltip-close:hover { color: var(--c-text, #1a2035); }

/* Tooltip 动画 */
.tooltip-fade-enter-active { transition: all .25s ease; }
.tooltip-fade-leave-active { transition: all .18s ease; }
.tooltip-fade-enter-from,
.tooltip-fade-leave-to { opacity: 0; transform: translateY(8px); }

@media (max-width: 480px) {
  .visitor-chat-root { right: 16px; bottom: 18px; }
  .fab-label { display: none; }
  .chat-fab { padding: 14px; border-radius: 50%; }
  .fab-glow { border-radius: 50%; }
}

/* ── 聊天面板 ── */
.chat-panel {
  width: 360px;
  max-height: 560px;
  background: var(--c-bg-card, #fff);
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--c-border, rgba(0,0,0,.08));
}

/* ── Header ── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  color: #fff;
  flex-shrink: 0;
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar { font-size: 28px; line-height: 1; }
.chat-name { font-weight: 700; font-size: 15px; }
.chat-status { font-size: 12px; opacity: .85; display: flex; align-items: center; gap: 5px; }
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #4ade80;
  display: inline-block;
}
.status-dot.thinking {
  background: #fbbf24;
  animation: dotBlink .8s ease-in-out infinite alternate;
}
@keyframes dotBlink { from { opacity: 1; } to { opacity: .3; } }
.chat-close {
  background: rgba(255,255,255,.2);
  border: none;
  color: #fff;
  width: 28px; height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.chat-close:hover { background: rgba(255,255,255,.35); }

/* ── 消息列表 ── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: var(--c-border, #ddd); border-radius: 2px; }

.msg {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  max-width: 100%;
}
.msg-ai { flex-direction: row; }
.msg-user { flex-direction: row-reverse; }

.msg-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.user-avatar {
  background: linear-gradient(135deg, #f97316, #ef4444);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

.msg-bubble {
  padding: 9px 13px;
  border-radius: 16px;
  font-size: 13.5px;
  line-height: 1.55;
  max-width: calc(100% - 46px);
  word-break: break-word;
}
.msg-ai .msg-bubble {
  background: var(--c-bg-2, #f0f4ff);
  color: var(--c-text, #1a2150);
  border-bottom-left-radius: 4px;
}
.msg-user .msg-bubble {
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-error .msg-bubble {
  background: rgba(239,68,68,.08);
  border: 1px solid rgba(239,68,68,.25);
  color: var(--c-text, #1a2150);
}
.retry-btn {
  margin-top: 8px;
  padding: 5px 12px;
  background: rgba(59,130,246,.12);
  border: 1px solid rgba(59,130,246,.3);
  border-radius: 7px;
  color: #3b82f6;
  font-size: .8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all .12s;
}
.retry-btn:hover:not(:disabled) {
  background: rgba(59,130,246,.2);
  transform: translateY(-1px);
}
.retry-btn:disabled {
  opacity: .4;
  cursor: not-allowed;
}
.msg-bubble :deep(code) {
  background: rgba(0,0,0,.08);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  font-family: monospace;
}
.msg-bubble :deep(strong) { font-weight: 700; }

.streaming { opacity: .9; }

/* 快捷问题 */
.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 10px;
}
.quick-btn {
  padding: 5px 10px;
  background: rgba(91,141,238,.12);
  border: 1px solid rgba(91,141,238,.25);
  border-radius: 20px;
  color: var(--c-primary, #5b8dee);
  font-size: 12px;
  cursor: pointer;
  text-align: left;
  transition: background .15s;
}
.quick-btn:hover:not(:disabled) { background: rgba(91,141,238,.22); }
.quick-btn:disabled { opacity: .5; cursor: not-allowed; }

/* 打字动画 */
.typing-dots { display: inline-flex; gap: 4px; align-items: center; }
.typing-dots span {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--c-text-muted, #888);
  animation: typingDot 1.2s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: .2s; }
.typing-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes typingDot {
  0%, 60%, 100% { transform: translateY(0); opacity: .4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* ── 输入区 ── */
.chat-input-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--c-border, rgba(0,0,0,.08));
  flex-shrink: 0;
  background: var(--c-bg-card, #fff);
}
.chat-input {
  flex: 1;
  resize: none;
  border: 1px solid var(--c-border, #ddd);
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 13.5px;
  line-height: 1.5;
  background: var(--c-bg, #f5f7ff);
  color: var(--c-text, #1a2150);
  outline: none;
  transition: border-color .2s;
  min-height: 38px;
  max-height: 120px;
  overflow-y: auto;
}
.chat-input:focus { border-color: var(--c-primary, #5b8dee); }
.chat-input:disabled { opacity: .6; }

.send-btn {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: opacity .2s, transform .15s;
}
.send-btn:hover:not(:disabled) { transform: scale(1.08); }
.send-btn:disabled { opacity: .4; cursor: not-allowed; }

.chat-footer {
  text-align: center;
  font-size: 11px;
  color: var(--c-text-muted, #888);
  padding: 5px 12px 8px;
  flex-shrink: 0;
}

/* ── 动画 ── */
.chat-bounce-enter-active { animation: fabIn .3s cubic-bezier(.34,1.56,.64,1); }
.chat-bounce-leave-active { animation: fabIn .2s ease reverse; }
@keyframes fabIn {
  from { transform: scale(0); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}

.chat-slide-enter-active {
  animation: slideUp .3s cubic-bezier(.34,1.56,.64,1);
  transform-origin: bottom right;
}
.chat-slide-leave-active {
  animation: slideUp .2s ease reverse;
  transform-origin: bottom right;
}
@keyframes slideUp {
  from { transform: scale(.85) translateY(20px); opacity: 0; }
  to   { transform: scale(1) translateY(0); opacity: 1; }
}

/* ── 移动端适配 ── */
@media (max-width: 480px) {
  .visitor-chat-root { bottom: 16px; right: 16px; }
  .chat-panel { width: calc(100vw - 32px); max-height: 70vh; }
}
</style>
