<template>
  <div class="relative group bg-white rounded-xl border shadow-card overflow-hidden hover:border-primary/40 transition">
    <router-link
      :to="`/create/generate/resume/${item.public_id}`"
      class="block"
    >
      <div class="aspect-[3/4] bg-surface-container-low flex items-center justify-center overflow-hidden">
        <img
          v-if="thumbSrc"
          :src="thumbSrc"
          :alt="item.title"
          class="w-full h-full object-cover object-top"
        />
        <span v-else class="material-symbols-outlined text-4xl text-on-surface-variant/40">description</span>
      </div>
      <div class="p-3">
        <p class="font-medium text-sm truncate">{{ item.title }}</p>
        <p class="text-xs text-on-surface-variant mt-1">{{ formatDate(item.updated_at) }}</p>
      </div>
    </router-link>
    <button
      type="button"
      class="absolute top-2 right-2 p-1.5 rounded-lg bg-white/90 border border-outline-variant/60 opacity-0 group-hover:opacity-100 transition text-on-surface-variant hover:text-red-600 hover:border-red-200"
      title="删除"
      @click.stop.prevent="emit('delete')"
    >
      <span class="material-symbols-outlined text-[18px]">delete</span>
    </button>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { api } from '../../api/client.js'

const props = defineProps({
  item: { type: Object, required: true },
})

const emit = defineEmits(['delete'])

const thumbSrc = ref('')
let objectUrl = ''

async function loadThumbnail() {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
    objectUrl = ''
  }
  thumbSrc.value = ''
  if (!props.item.thumbnail_url) return
  try {
    objectUrl = await api.fetchResumeThumbnail(props.item.public_id)
    thumbSrc.value = objectUrl
  } catch {
    thumbSrc.value = ''
  }
}

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('zh-CN')
  } catch {
    return ''
  }
}

onMounted(loadThumbnail)
watch(() => props.item.public_id, loadThumbnail)

onBeforeUnmount(() => {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>
