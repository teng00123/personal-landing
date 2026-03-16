<template>
  <div class="activities-page">
    <div class="page-header">
      <h1>{{ $t('community.activities') }}</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + {{ $t('community.create_activity') }}
      </button>
    </div>

    <!-- 活动列表 -->
    <div class="activity-list" v-if="activities.length">
      <div
        v-for="act in activities"
        :key="act.id"
        class="activity-card"
        @click="openActivity(act)"
      >
        <div class="act-header">
          <h3>{{ act.title }}</h3>
          <span class="act-badge" :class="actStatus(act)">{{ actStatusLabel(act) }}</span>
        </div>
        <div class="act-meta">
          <span>👤 {{ act.organizer }}</span>
          <span>📅 {{ formatDate(act.start_time) }}</span>
          <span v-if="act.location">📍 {{ act.location }}</span>
          <span>👥 {{ act.registered }}{{ act.max_seats ? '/' + act.max_seats : '' }} {{ $t('community.registered') }}</span>
        </div>
      </div>
    </div>
    <el-empty v-else :description="$t('community.no_activities')" />

    <!-- 创建活动弹窗 -->
    <el-dialog v-model="showCreateModal" :title="$t('community.create_activity')" width="480px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item :label="$t('community.act_title')">
          <el-input v-model="createForm.title" />
        </el-form-item>
        <el-form-item :label="$t('community.act_organizer')">
          <el-input v-model="createForm.organizer" />
        </el-form-item>
        <el-form-item :label="$t('community.act_start')">
          <el-date-picker v-model="createForm.start_time" type="datetime" />
        </el-form-item>
        <el-form-item :label="$t('community.act_location')">
          <el-input v-model="createForm.location" />
        </el-form-item>
        <el-form-item :label="$t('community.act_seats')">
          <el-input-number v-model="createForm.max_seats" :min="0" />
          <span class="hint">0 = {{ $t('community.unlimited') }}</span>
        </el-form-item>
        <el-form-item :label="$t('community.act_desc')">
          <el-input v-model="createForm.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateModal = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="createActivity">{{ $t('common.submit') }}</el-button>
      </template>
    </el-dialog>

    <!-- 活动详情/报名弹窗 -->
    <el-dialog v-model="showDetailModal" :title="selectedActivity?.title" width="520px">
      <div v-if="selectedActivity">
        <p>{{ selectedActivity.description }}</p>
        <div class="detail-meta">
          <div><strong>主办方：</strong>{{ selectedActivity.organizer }}</div>
          <div><strong>时间：</strong>{{ formatDate(selectedActivity.start_time) }}</div>
          <div v-if="selectedActivity.location"><strong>地点：</strong>{{ selectedActivity.location }}</div>
          <div><strong>已报名：</strong>{{ selectedActivity.registered }}{{ selectedActivity.max_seats ? '/' + selectedActivity.max_seats : '' }}</div>
        </div>
        <el-divider />
        <h4>{{ $t('community.register') }}</h4>
        <el-form :model="registerForm" label-width="70px">
          <el-form-item :label="$t('community.nickname')">
            <el-input v-model="registerForm.nickname" />
          </el-form-item>
          <el-form-item :label="$t('community.email')">
            <el-input v-model="registerForm.user_identifier" />
          </el-form-item>
        </el-form>
        <div class="register-actions">
          <el-button type="primary" @click="registerActivity">
            {{ $t('community.register_now') }}
          </el-button>
          <el-button @click="checkinActivity">
            {{ $t('community.checkin') }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const activities       = ref([])
const showCreateModal  = ref(false)
const showDetailModal  = ref(false)
const selectedActivity = ref(null)

const createForm = ref({
  title: '', organizer: '', start_time: null,
  location: '', max_seats: 0, description: '',
})
const registerForm = ref({ nickname: '', user_identifier: '' })

onMounted(fetchActivities)

async function fetchActivities() {
  const res = await fetch('/api/v1/community/activities')
  const data = await res.json()
  activities.value = data.items
}

function openActivity(act) {
  selectedActivity.value = act
  showDetailModal.value  = true
}

async function createActivity() {
  const res = await fetch('/api/v1/community/activities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(createForm.value),
  })
  if (res.ok) {
    ElMessage.success(t('community.created'))
    showCreateModal.value = false
    fetchActivities()
  } else {
    ElMessage.error(t('community.create_failed'))
  }
}

async function registerActivity() {
  const id = selectedActivity.value?.id
  const res = await fetch(`/api/v1/community/activities/${id}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registerForm.value),
  })
  const data = await res.json()
  if (res.ok) {
    ElMessage.success(t('community.register_success'))
    fetchActivities()
  } else {
    ElMessage.error(data.detail || t('community.register_failed'))
  }
}

async function checkinActivity() {
  const id = selectedActivity.value?.id
  const res = await fetch(`/api/v1/community/activities/${id}/checkin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registerForm.value),
  })
  const data = await res.json()
  if (res.ok) {
    ElMessage.success(t('community.checkin_success'))
  } else {
    ElMessage.error(data.detail || t('community.checkin_failed'))
  }
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('zh-CN')
}

function actStatus(act) {
  const now = Date.now()
  const start = new Date(act.start_time).getTime()
  if (now < start) return 'upcoming'
  return 'ended'
}

function actStatusLabel(act) {
  return actStatus(act) === 'upcoming' ? t('community.upcoming') : t('community.ended')
}
</script>

<style scoped>
.activities-page { padding: 24px; max-width: 800px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }

.activity-list { display: flex; flex-direction: column; gap: 12px; }
.activity-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.activity-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); }

.act-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.act-header h3 { margin: 0; font-size: 16px; }
.act-badge { padding: 2px 10px; border-radius: 10px; font-size: 12px; }
.act-badge.upcoming { background: #d4edda; color: #155724; }
.act-badge.ended    { background: #e2e3e5; color: #383d41; }

.act-meta { display: flex; gap: 16px; font-size: 13px; color: var(--text-secondary); flex-wrap: wrap; }

.detail-meta { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
.register-actions { margin-top: 12px; display: flex; gap: 10px; }
.hint { font-size: 12px; color: var(--text-secondary); margin-left: 8px; }

.btn { padding: 6px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.btn-primary { background: var(--primary); color: #fff; }
</style>
