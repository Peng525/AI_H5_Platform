<template>
  <div class="min-h-screen bg-surface-container-low flex flex-col">
    <AppShell :show-quota="false" />
    <div class="flex-1 flex items-center justify-center p-6">
      <div class="max-w-3xl w-full bg-white rounded-2xl shadow-card p-8 md:p-10 border border-outline-variant">
        <div class="text-center mb-8">
          <div class="w-16 h-16 mx-auto rounded-full bg-secondary/20 flex items-center justify-center mb-4">
            <span class="material-symbols-outlined text-secondary text-4xl">check_circle</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold">H5 发布成功！</h1>
          <p class="text-on-surface-variant mt-2">您的演示已上线，可通过链接或二维码分享</p>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <div class="border border-outline-variant rounded-xl p-5">
            <h3 class="font-semibold flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">link</span>
              分享链接
            </h3>
            <p class="text-xs text-on-surface-variant mt-1">持有链接即可查看</p>
            <input :value="shareUrl" readonly class="w-full mt-3 border border-outline-variant rounded-lg px-3 py-2 text-sm bg-surface-container-low" />
            <button class="mt-3 w-full py-2.5 border border-outline-variant rounded-lg text-sm hover:bg-surface-container-low" @click="copy">
              复制链接
            </button>
          </div>
          <div class="border border-outline-variant rounded-xl p-5 flex flex-col items-center">
            <h3 class="font-semibold self-start flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">qr_code_2</span>
              二维码
            </h3>
            <p class="text-xs text-on-surface-variant self-start mt-1">手机扫码即时预览</p>
            <canvas ref="qrCanvas" class="w-32 h-32 mt-4" />
          </div>
        </div>

        <div class="flex flex-wrap justify-between gap-4 mt-8 pt-6 border-t border-outline-variant text-sm">
          <router-link :to="`/editor/${$route.params.id}`" class="text-primary flex items-center gap-1 hover:underline">
            <span class="material-symbols-outlined text-lg">arrow_back</span>
            返回编辑器
          </router-link>
          <router-link to="/dashboard" class="text-primary flex items-center gap-1 hover:underline">
            前往工作台
            <span class="material-symbols-outlined text-lg">dashboard</span>
          </router-link>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div
        v-if="toast"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-on-surface text-white px-4 py-2 rounded-lg text-sm shadow-lg z-50"
      >
        {{ toast }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import QRCode from 'qrcode'
import { api } from '../api/client'
import AppShell from '../components/AppShell.vue'

const route = useRoute()
const slug = ref('')
const qrCanvas = ref(null)
const toast = ref('')

const shareUrl = computed(() => (slug.value ? `${window.location.origin}/s/${slug.value}` : ''))

onMounted(async () => {
  const p = await api.getProject(Number(route.params.id))
  slug.value = p.share_slug
})

watch(shareUrl, async (url) => {
  if (!url || !qrCanvas.value) return
  await nextTick()
  try {
    await QRCode.toCanvas(qrCanvas.value, url, { width: 128, margin: 1 })
  } catch (e) {
    console.warn('二维码生成失败', e)
  }
})

function copy() {
  navigator.clipboard.writeText(shareUrl.value).then(() => {
    toast.value = '链接已复制到剪贴板'
    setTimeout(() => { toast.value = '' }, 2000)
  })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
