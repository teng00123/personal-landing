<template>
  <!-- 浮动触发按钮 -->
  <div class="visitor-chat-root">
    <transition name="chat-bounce">
      <button
        v-if="!isOpen"
        class="chat-fab"
        :class="{ pulse: !hasOpened }"
        @click="openChat"
        aria-label="和 AI 聊聊"
      >
        <span class="fab-icon">🤖</span>
        <span class="fab-badge" v-if="!hasOpened">👋</span>
      </button>
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
              👋 你好！我是这个主页的 AI 助手，可以回答关于博主的技能、项目和文章的问题。
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
            :class="msg.role === 'user' ? 'msg-user' : 'msg-ai'"
          >
            <div class="msg-avatar" v-if="msg.role === 'ai'">🤖</div>
            <div class="msg-bubble" v-html="renderContent(msg.content)"></div>
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
import { ref, nextTick } from 'vue'

const isOpen = ref(false)
const hasOpened = ref(false)
const isStreaming = ref(false)
const inputText = ref('')
const streamingText = ref('')
const messages = ref([])
const messagesEl = ref(null)
const inputEl = ref(null)

const quickQuestions = [
  '你擅长哪些技术？',
  '做过哪些项目？',
  '有推荐的文章吗？',
]

function openChat() {
  isOpen.value = true
  hasOpened.value = true
  nextTick(() => inputEl.value?.focus())
}

function closeChat() {
  isOpen.value = false
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

  try {
    const res = await fetch('/api/v1/ai/chat/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })

    if (!res.ok) {
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
          streamingText.value = data.slice(7).trim() || 'AI 服务暂时不可用，请稍后重试'
          break
        }
        // 反转义换行
        streamingText.value += data.replace(/\\n/g, '\n')
        await scrollBottom()
      }
    }

    // 流结束，把 streaming 内容固化为消息
    if (streamingText.value) {
      messages.value.push({ role: 'ai', content: streamingText.value })
    }
  } catch (err) {
    messages.value.push({
      role: 'ai',
      content: '抱歉，请求失败了。请检查网络或稍后重试。',
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
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: var(--font-sans, system-ui, sans-serif);
}

/* ── FAB 按钮 ── */
.chat-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--c-primary, #5b8dee), #8b6cf7);
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(91,141,238,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: transform .2s ease, box-shadow .2s ease;
}
.chat-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 28px rgba(91,141,238,.6);
}
.fab-icon { font-size: 24px; line-height: 1; }
.fab-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  font-size: 16px;
  animation: wave 1.5s ease-in-out infinite;
}
@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}
.pulse::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: rgba(91,141,238,.3);
  animation: pulseRing 2s ease-out infinite;
}
@keyframes pulseRing {
  0% { transform: scale(1); opacity: .8; }
  100% { transform: scale(1.6); opacity: 0; }
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
