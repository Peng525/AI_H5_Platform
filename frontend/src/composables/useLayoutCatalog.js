import { ref } from 'vue'
import { api } from '../api/client'
import {
  BUSINESS_LAYOUT_BLOCKS,
  getMoreLayoutBlocks,
  PRIMARY_LAYOUT_SHORTCUTS,
  STORY_LAYOUT_BLOCKS,
} from '../constants/layoutBlocks.js'

const loaded = ref(false)
const blocks = ref([])
let loadPromise = null

function mapMeta(block) {
  return { id: block.id, label: block.label, icon: block.icon || 'dashboard' }
}

export function useLayoutCatalog() {
  async function load() {
    if (loaded.value) return blocks.value
    if (loadPromise) return loadPromise
    loadPromise = api
      .listLayoutBlocks()
      .then((rows) => {
        blocks.value = Array.isArray(rows) ? rows : []
        loaded.value = true
        return blocks.value
      })
      .catch(() => {
        blocks.value = []
        loaded.value = true
        return []
      })
    return loadPromise
  }

  function reload() {
    loaded.value = false
    loadPromise = null
    return load()
  }

  function getCatalogBlock(id) {
    return blocks.value.find((b) => b.id === id) || null
  }

  function getPrimaryLayoutItems() {
    const custom = blocks.value.filter((b) => b.placement === 'primary').map(mapMeta)
    const builtins = PRIMARY_LAYOUT_SHORTCUTS.filter((x) => x.id !== '__table__')
    const table = PRIMARY_LAYOUT_SHORTCUTS.find((x) => x.addType === 'table')
    return [...builtins, ...custom, table].filter(Boolean)
  }

  function getMoreLayoutItems() {
    const builtin = getMoreLayoutBlocks()
    const custom = blocks.value.filter((b) => b.placement === 'more').map(mapMeta)
    return [...builtin, ...custom]
  }

  function getPickerLayoutItems() {
    const builtin = [...BUSINESS_LAYOUT_BLOCKS, ...STORY_LAYOUT_BLOCKS]
    const custom = blocks.value.map(mapMeta)
    const seen = new Set()
    return [...builtin, ...custom].filter((item) => {
      if (seen.has(item.id)) return false
      seen.add(item.id)
      return true
    })
  }

  return {
    loaded,
    blocks,
    load,
    reload,
    getCatalogBlock,
    getPrimaryLayoutItems,
    getMoreLayoutItems,
    getPickerLayoutItems,
  }
}
