<template>
  <div class="language-switcher">
    <el-dropdown @command="changeLanguage">
      <el-button type="text" size="small">
        <el-icon><Setting /></el-icon>
        {{ currentLanguage === 'zh-CN' ? '🇨🇳' : '🇺🇸' }}
        {{ currentLanguage === 'zh-CN' ? '中文' : 'English' }}
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="zh-CN">🇨🇳 中文</el-dropdown-item>
          <el-dropdown-item command="en-US">🇺🇸 English</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Setting } from '@element-plus/icons-vue'

const { locale } = useI18n()

const currentLanguage = computed(() => locale.value)

const changeLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem('language', lang)
}
</script>

<style scoped>
.language-switcher {
  margin-right: 10px;
}
</style>