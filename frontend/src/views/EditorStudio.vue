<template>
  <div class="h-screen flex flex-col bg-background overflow-hidden">
    <EditorTopBar
      :project-id="projectId"
      :hide-publish="!!isAdminEditorMode"
      :nav-mode="isAdminEditorMode ? 'admin' : 'user'"
    >
      <template v-if="adminLayoutId" #actions>
        <router-link
          to="/admin/layouts"
          class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high whitespace-nowrap"
        >
          返回版式管理
        </router-link>
        <button
          type="button"
          class="hidden lg:inline-flex px-3 py-1.5 rounded-lg bg-secondary text-on-secondary text-xs sm:text-sm font-medium whitespace-nowrap"
          @click="openLayoutSave"
        >
          保存版式
        </button>
        <div ref="adminLayoutActionsRef" class="relative lg:hidden">
          <button
            type="button"
            class="px-2.5 py-1.5 rounded-lg border border-outline-variant text-xs hover:bg-surface-container-high"
            aria-label="更多操作"
            @click="adminLayoutActionsOpen = !adminLayoutActionsOpen"
          >
            <span class="material-symbols-outlined text-[20px] leading-none">more_vert</span>
          </button>
          <div
            v-if="adminLayoutActionsOpen"
            class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50 text-sm"
          >
            <router-link
              to="/admin/layouts"
              class="block px-3 py-2 hover:bg-surface-container-low"
              @click="adminLayoutActionsOpen = false"
            >
              返回版式管理
            </router-link>
            <button
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-surface-container-low"
              @click="adminLayoutActionsOpen = false; openLayoutSave()"
            >
              保存版式
            </button>
          </div>
        </div>
      </template>
      <template v-else-if="adminPresetId" #actions>
        <router-link
          to="/admin/templates"
          class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high whitespace-nowrap"
        >
          返回模板管理
        </router-link>
        <label class="hidden lg:inline-flex items-center px-3 py-1.5 rounded-lg border border-outline-variant text-xs sm:text-sm hover:bg-surface-container-high cursor-pointer whitespace-nowrap">
          从 PPT 导入
          <input type="file" accept=".pptx" class="hidden" :disabled="pptImporting" @change="onAdminPptxImport" />
        </label>
        <button
          type="button"
          class="hidden lg:inline-flex px-3 py-1.5 rounded-lg bg-primary text-on-primary text-xs sm:text-sm font-medium whitespace-nowrap disabled:opacity-50"
          :disabled="pptImporting"
          @click="openPresetSave"
        >
          保存为预设
        </button>
        <div ref="adminActionsRef" class="relative lg:hidden">
          <button
            type="button"
            class="px-2.5 py-1.5 rounded-lg border border-outline-variant text-xs hover:bg-surface-container-high"
            aria-label="更多操作"
            @click="adminActionsOpen = !adminActionsOpen"
          >
            <span class="material-symbols-outlined text-[20px] leading-none">more_vert</span>
          </button>
          <div
            v-if="adminActionsOpen"
            class="absolute right-0 top-full mt-1 w-44 bg-white border border-outline-variant rounded-lg shadow-lg py-1 z-50 text-sm"
          >
            <router-link
              to="/admin/templates"
              class="block px-3 py-2 hover:bg-surface-container-low"
              @click="adminActionsOpen = false"
            >
              返回模板管理
            </router-link>
            <label class="block px-3 py-2 hover:bg-surface-container-low cursor-pointer">
              从 PPT 导入
              <input type="file" accept=".pptx" class="hidden" :disabled="pptImporting" @change="onAdminPptxMenuImport" />
            </label>
            <button
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-surface-container-low disabled:opacity-50"
              :disabled="pptImporting"
              @click="adminActionsOpen = false; openPresetSave()"
            >
              保存为预设
            </button>
          </div>
        </div>
      </template>
    </EditorTopBar>

    <DeckEditorWorkspace
      ref="workspaceRef"
      :project-id="projectId"
      layout-mode="studio"
      :admin-preset-id="adminPresetId"
      :admin-layout-id="adminLayoutId"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import EditorTopBar from '../components/EditorTopBar.vue'
import DeckEditorWorkspace from '../components/DeckEditorWorkspace.vue'

const route = useRoute()
const workspaceRef = ref(null)

const projectId = computed(() => String(route.params.publicId || ''))
const adminPresetId = computed(() => (typeof route.query.adminPreset === 'string' ? route.query.adminPreset : ''))
const adminLayoutId = computed(() => (typeof route.query.adminLayout === 'string' ? route.query.adminLayout : ''))
const isAdminEditorMode = computed(() => !!(adminPresetId.value || adminLayoutId.value))

const adminActionsOpen = ref(false)
const adminLayoutActionsOpen = ref(false)
const adminActionsRef = ref(null)
const adminLayoutActionsRef = ref(null)

const pptImporting = computed(() => workspaceRef.value?.pptImporting ?? false)

function openLayoutSave() {
  workspaceRef.value?.openLayoutSave()
}

function openPresetSave() {
  workspaceRef.value?.openPresetSave()
}

function onAdminPptxImport(e) {
  workspaceRef.value?.onAdminPptxImport(e)
}

function onAdminPptxMenuImport(e) {
  adminActionsOpen.value = false
  onAdminPptxImport(e)
}

function onAdminActionsClickOutside(e) {
  if (adminActionsRef.value && !adminActionsRef.value.contains(e.target)) {
    adminActionsOpen.value = false
  }
  if (adminLayoutActionsRef.value && !adminLayoutActionsRef.value.contains(e.target)) {
    adminLayoutActionsOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onAdminActionsClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', onAdminActionsClickOutside)
})
</script>
