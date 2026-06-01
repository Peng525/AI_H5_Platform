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

function dbMetaFor(id) {
  const db = blocks.value.find((b) => b.id === id)
  return db ? mapMeta(db) : null
}

function mergeMetaList(builtinList) {
  return builtinList.map((item) => dbMetaFor(item.id) || item)
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
    const builtins = mergeMetaList(PRIMARY_LAYOUT_SHORTCUTS.filter((x) => x.id !== '__table__'))
    const table = PRIMARY_LAYOUT_SHORTCUTS.find((x) => x.addType === 'table')
    const seen = new Set(builtins.map((b) => b.id))
    const extraCustom = custom.filter((c) => !seen.has(c.id))
    return [...builtins, ...extraCustom, table].filter(Boolean)
  }

  function getMoreLayoutItems() {
    const builtin = mergeMetaList(getMoreLayoutBlocks())
    const custom = blocks.value.filter((b) => b.placement === 'more').map(mapMeta)
    const seen = new Set(builtin.map((b) => b.id))
    const extraCustom = custom.filter((c) => !seen.has(c.id))
    return [...builtin, ...extraCustom]
  }

  function getPickerLayoutItems() {
    const builtin = mergeMetaList([...BUSINESS_LAYOUT_BLOCKS, ...STORY_LAYOUT_BLOCKS])
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
