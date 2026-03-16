<template>
  <div id="app">
    <LanguageSwitcher />
    <router-view />
  </div>
</template>

<script setup>
import LanguageSwitcher from './components/LanguageSwitcher.vue'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>