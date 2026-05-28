<template>
  <div class="min-h-screen bg-surface-container-low flex items-center justify-center p-6">
    <div class="max-w-3xl w-full bg-white rounded-2xl shadow-card p-10 border border-outline-variant text-center">
      <div class="w-16 h-16 mx-auto rounded-full bg-secondary/20 flex items-center justify-center mb-4">
        <span class="material-symbols-outlined text-secondary text-4xl">check_circle</span>
      </div>
      <h1 class="text-2xl font-bold">H5 发布成功！</h1>
      <p class="text-on-surface-variant mt-2 mb-8">您的演示已上线，可通过链接或二维码分享</p>

      <div class="grid md:grid-cols-2 gap-6 text-left">
        <div class="border border-outline-variant rounded-xl p-5">
          <h3 class="font-semibold flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">link</span>
            分享链接
          </h3>
          <p class="text-xs text-on-surface-variant mt-1">持有链接即可查看</p>
          <input :value="shareUrl" readonly class="w-full mt-3 border rounded-lg px-3 py-2 text-sm bg-surface-container-low" />
          <button class="mt-3 w-full py-2 border rounded-lg text-sm" @click="copy">复制链接</button>
        </div>
        <div class="border border-outline-variant rounded-xl p-5 flex flex-col items-center">
          <h3 class="font-semibold self-start flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">qr_code_2</span>
            二维码
          </h3>
          <p class="text-xs text-on-surface-variant self-start mt-1">手机扫码即时预览</p>
          <div class="w-28 h-28 mt-4 bg-surface-container-low border flex items-center justify-center text-xs text-on-surface-variant">
            QR 演示
          </div>
        </div>
      </div>

      <div class="flex justify-between mt-8 pt-6 border-t text-sm">
        <router-link :to="`/editor/${$route.params.id}`" class="text-primary flex items-center gap-1">
          <span class="material-symbols-outlined text-lg">arrow_back</span>
          返回编辑器
        </router-link>
        <router-link to="/templates" class="text-primary flex items-center gap-1">
          前往工作台
          <span class="material-symbols-outlined text-lg">dashboard</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const route = useRoute()
const slug = ref('')

onMounted(async () => {
  const p = await api.getProject(Number(route.params.id))
  slug.value = p.share_slug
})

const shareUrl = computed(() => `${window.location.origin}/s/${slug.value}`)
function copy() {
  navigator.clipboard.writeText(shareUrl.value).then(() => alert('已复制'))
}
</script>
