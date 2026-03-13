<template>
  <div>
    <h2 class="page-h2">🧑 个人资料</h2>
    <el-form :model="form" label-position="top" v-loading="loading" class="profile-form">

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="显示名称">
            <el-input v-model="form.full_name" placeholder="Your Name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="职位头衔">
            <el-input v-model="form.title" placeholder="Senior Backend Engineer" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="个人简介">
        <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="介绍一下自己..." />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="所在地">
            <el-input v-model="form.location" placeholder="深圳，中国" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="公开邮箱">
            <el-input v-model="form.email_public" placeholder="hello@example.com" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="GitHub 链接">
            <el-input v-model="form.github_url" placeholder="https://github.com/xxx" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="LinkedIn 链接">
            <el-input v-model="form.linkedin_url" placeholder="https://linkedin.com/in/xxx" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="头像 URL">
            <el-input v-model="form.avatar_url" placeholder="https://..." />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="简历数据（JSON）">
        <el-input
          v-model="form.resume_data"
          type="textarea"
          :rows="14"
          placeholder='{"experience":[],"education":[],"skills":[]}'
          style="font-family:monospace;font-size:13px"
        />
        <div style="font-size:.75rem;color:#64748b;margin-top:4px">
          格式参考 README，包含 experience / education / skills / certifications
        </div>
      </el-form-item>

      <el-button type="primary" :loading="saving" @click="save">
        💾 保存
      </el-button>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { profileApi } from '@/api/endpoints.js'

const loading = ref(false)
const saving  = ref(false)
const form    = ref({
  full_name: '', title: '', bio: '', location: '', email_public: '',
  github_url: '', linkedin_url: '', avatar_url: '', resume_data: '',
})

onMounted(async () => {
  loading.value = true
  try {
    const data = await profileApi.get()
    Object.assign(form.value, data)
  } catch { /* first run, no profile yet */ }
  finally { loading.value = false }
})

async function save() {
  // 简单校验 JSON
  if (form.value.resume_data) {
    try { JSON.parse(form.value.resume_data) }
    catch { ElMessage.error('简历 JSON 格式不正确'); return }
  }
  saving.value = true
  try {
    await profileApi.update(form.value)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error(e?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-h2       { font-size: 1.375rem; font-weight: 700; color: #f1f5f9; margin-bottom: 24px; }
.profile-form  { max-width: 900px; }
</style>
