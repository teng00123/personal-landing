<template>
  <div class="page section">
    <div class="container">
      <h1 class="section-title fade-in-up">文章</h1>
      <p class="text-muted fade-in-up" style="margin-bottom:36px;font-size:1.05rem">
        技术思考 · 工程实践
      </p>

      <!-- 标签筛选 -->
      <div class="tag-filter fade-in-up">
        <el-tag :type="!activeTag ? '' : 'info'" @click="filterBy(null)" style="cursor:pointer">全部</el-tag>
        <el-tag
          v-for="t in allTags" :key="t"
          :type="activeTag === t ? '' : 'info'"
          @click="filterBy(t)"
          style="cursor:pointer"
        >{{ t }}</el-tag>
      </div>

      <!-- 列表 -->
      <div v-loading="loading" class="art-grid">
        <router-link
          v-for="a in articles" :key="a.id"
          :to="`/articles/${a.slug}`"
          class="card art-card"
        >
          <img v-if="a.cover_image" :src="a.cover_image" class="art-cover" />
          <div class="art-body">
            <div class="tag-row">
              <el-tag v-for="t in parseTags(a.tags)" :key="t" size="small">{{ t }}</el-tag>
            </div>
            <h2 class="art-title">{{ a.title }}</h2>
            <p class="art-sum text-muted">{{ a.summary }}</p>
            <div class="art-foot">
              <span>{{ fmtDate(a.published_at) }}</span>
              <span>👁 {{ a.view_count }}</span>
            </div>
          </div>
        </router-link>
      </div>

      <el-empty v-if="!loading && !articles.length" description="暂无文章" style="padding:80px 0" />

      <div class="pager" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          background
          layout="prev,pager,next"
          @current-change="load"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { articlesApi } from '@/api/endpoints.js'
import dayjs from 'dayjs'

const articles  = ref([])
const total     = ref(0)
const page      = ref(1)
const pageSize  = 9
const loading   = ref(false)
const activeTag = ref(null)
const allTags   = ref([])

const parseTags = (t) => (t || '').split(',').map(s => s.trim()).filter(Boolean)
const fmtDate   = (d) => d ? dayjs(d).format('YYYY-MM-DD') : ''

async function load() {
  loading.value = true
  try {
    const res = await articlesApi.list({
      page: page.value,
      page_size: pageSize,
      tag: activeTag.value || undefined,
    })
    articles.value = res.items ?? []
    total.value    = res.total
    if (!allTags.value.length) {
      const s = new Set()
      articles.value.forEach(a => parseTags(a.tags).forEach(t => s.add(t)))
      allTags.value = [...s]
    }
  } finally { loading.value = false }
}

function filterBy(tag) {
  activeTag.value = tag
  page.value = 1
  load()
}

onMounted(load)
</script>

<style scoped>
.page { padding-top: 60px; }
.tag-filter { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 36px; }
.art-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(300px,1fr)); gap: 24px; }
.art-card { display: flex; flex-direction: column; text-decoration: none; color: inherit; overflow: hidden; padding: 0; }
.art-cover { width: 100%; height: 170px; object-fit: cover; }
.art-body { padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 10px; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; }
.art-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; line-height: 1.4; }
.art-sum { font-size: .875rem; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.art-foot { display: flex; justify-content: space-between; font-size: .8125rem; color: #64748b; padding-top: 8px; border-top: 1px solid #1e293b; }
.pager { display: flex; justify-content: center; margin-top: 48px; }
</style>
