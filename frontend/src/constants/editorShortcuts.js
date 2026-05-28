/** 编辑器快捷键说明（帮助面板与文档共用） */
export const EDITOR_SHORTCUT_GROUPS = [
  {
    title: '编辑',
    items: [
      { label: '撤回', keys: ['Ctrl', 'Z'] },
      { label: '重做', keys: ['Ctrl', 'Y'] },
      { label: '重做（备选）', keys: ['Ctrl', 'Shift', 'Z'] },
      { label: '删除选中元素', keys: ['Delete'] },
    ],
  },
  {
    title: '画布',
    items: [
      { label: '手型工具（拖动画布）', keys: ['H'] },
      { label: '按住拖动画布', keys: ['Space', '拖动'] },
      { label: '放大 / 缩小', keys: ['滚轮'] },
      { label: '重置视图', keys: ['双击', '100%'] },
      { label: '编辑文本', keys: ['双击', '文本框'] },
      { label: '编辑表格单元格', keys: ['双击', '单元格'] },
    ],
  },
  {
    title: '帮助',
    items: [
      { label: '打开快捷键说明', keys: ['F1'] },
      { label: '打开快捷键说明', keys: ['Ctrl', '/'] },
    ],
  },
]

export const EDITOR_SHORTCUT_HINT = '按 F1 或 Ctrl+/ 查看快捷键'
