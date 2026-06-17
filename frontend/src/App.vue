<template>
  <router-view v-slot="{ Component, route }">
    <keep-alive :max="5" :include="['AiGenerateResult', 'AiGenerateReview']">
      <component
        v-if="route.meta.keepAlive"
        :is="Component"
        :key="route.meta.keepAliveKey(route)"
      />
    </keep-alive>
    <component v-if="!route.meta.keepAlive" :is="Component" :key="route.fullPath" />
  </router-view>
  <ToastHost />
</template>

<script setup>
import ToastHost from './components/ToastHost.vue'
</script>
