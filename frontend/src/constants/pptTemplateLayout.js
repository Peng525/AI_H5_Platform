/**
 * PPT严格模板 — 内容区域坐标常量
 * 基于「中汽研_商务」模板 1280×720 画布坐标系
 * 所有坐标单位：像素（px）
 */

/** 画布尺寸 */
export const PPT_CANVAS = {
  width: 1280,
  height: 720,
}

/** 安全区域 */
export const PPT_SAFE = {
  x: 60,
  y: 90,
  width: 1160,
  height: 580, // y:90 → y:670
  right: 1220,
  bottom: 670,
}

/** 封面页 (01_cover.svg) */
export const COVER = {
  // 左上角Logo
  logo: { x: 100, y: 80, w: 200, h: 80 },
  // 主标题
  title: { x: 100, y: 280, w: 620, h: 80 },
  // 装饰横线
  accentBar: { x: 100, y: 350, w: 120, h: 6 },
  // 副标题
  subtitle: { x: 100, y: 380, w: 620, h: 50 },
  // 汇报人/部门
  authorLabel: { x: 100, y: 580, w: 200, h: 28 },
  authorValue: { x: 100, y: 615, w: 280, h: 40 },
  // 日期
  dateLabel: { x: 400, y: 580, w: 200, h: 28 },
  dateValue: { x: 400, y: 615, w: 280, h: 40 },
  // 顶部彩条
  topBar: { x: 0, y: 0, w: 1280, h: 6 },
}

/** 目录页 (02_toc.svg) */
export const TOC = {
  // 大号背景数字
  bgNumber: { x: 100, y: 40, w: 180, h: 80 },
  // 页标题
  title: { x: 200, y: 45, w: 900, h: 50 },
  // 标题下方分隔线
  divider: { x: 100, y: 100, w: 1080, h: 1 },
  // Logo 右上
  logo: { x: 1100, y: 30, w: 120, h: 50 },
  // 目录项 — 左列
  itemLeft: { x: 100, y: 120, w: 520, h: 100 },
  // 目录项 — 右列
  itemRight: { x: 660, y: 120, w: 520, h: 100 },
  // 每行高度（左列间距）
  rowGap: 140,
  // 卡片内部坐标（相对于卡片左上角）
  card: {
    accentBar: { x: 0, y: 0, w: 8, h: 100 },
    number: { x: 40, y: 55, w: 70, h: 55 },
    title: { x: 120, y: 32, w: 380, h: 35 },
    desc: { x: 120, y: 72, w: 380, h: 25 },
  },
  // 最多显示条目数
  maxItems: 8,
}

/** 内容页 (03_content.svg) — 用于 points 和 cards 模板 */
export const CONTENT = {
  // 顶部彩条
  topBar: { x: 0, y: 0, w: 1280, h: 6 },
  // 头部背景区域
  headerBg: { x: 0, y: 6, w: 1280, h: 84 },
  // 章节徽章
  chapterBadge: { x: 60, y: 26, w: 50, h: 50 },
  chapterNum: { x: 85, y: 48, w: 30, h: 35 }, // 文字居中于徽章内
  // 页面标题
  pageTitle: { x: 130, y: 50, w: 950, h: 44 },
  // 右上Logo
  logo: { x: 1100, y: 26, w: 120, h: 50 },
  // 头部分隔线
  headerLine: { x: 0, y: 90, w: 1280, h: 1 },
  // 内容主体区域
  body: { x: 60, y: 110, w: 1160, h: 560 },
  // 底部分隔线
  footerBar: { x: 0, y: 714, w: 1280, h: 6 },
  // 页码
  pageNum: { x: 1220, y: 690, w: 40, h: 20 },
  // 右下角水印Logo
  watermark: { x: 1000, y: 600, w: 200, h: 80 },
}

/**
 * 根据 variant 数量计算卡片/要点布局参数
 * @param {number} count - 数量（1-5）
 * @param {{x: number, y: number, w: number, h: number}} body - 可用内容区域
 * @returns {{ cols: number, rows: number, cellW: number, cellH: number, gap: number, positions: Array<{x: number, y: number}> }}
 */
export function computeGridLayout(count, body = CONTENT.body) {
  const gap = 20
  let cols, rows

  if (count === 1) {
    cols = 1; rows = 1
  } else if (count === 2) {
    cols = 2; rows = 1
  } else if (count === 3) {
    cols = 3; rows = 1
  } else if (count === 4) {
    cols = 2; rows = 2
  } else {
    // 5: 上3下2
    cols = 3; rows = 2
  }

  const cellW = Math.floor((body.w - gap * (cols - 1)) / cols)
  const cellH = Math.floor((body.h - gap * (rows - 1)) / rows)
  const positions = []

  for (let r = 0; r < rows; r++) {
    const rowCount = (count === 5 && r === 1) ? 2 : cols
    const rowStartX = count === 5 && r === 1
      ? body.x + Math.floor((body.w - (cellW * 2 + gap)) / 2) // 第二行居中
      : body.x
    for (let c = 0; c < rowCount; c++) {
      if (positions.length >= count) break
      positions.push({
        x: rowStartX + c * (cellW + gap),
        y: body.y + r * (cellH + gap),
      })
    }
  }

  return { cols, rows, cellW, cellH, gap, positions }
}

/**
 * 配色常量 — 商务汇报模板
 */
export const PPT_COLORS = {
  primary: '#003366',
  accent: '#0050B3',
  accentRed: '#D32F2F',
  bgLight: '#F0F2F5',
  bgHeader: '#F3F4F6',
  text: '#1F2937',
  textMuted: '#6B7280',
  textLight: '#9CA3AF',
  white: '#FFFFFF',
  onAccent: '#FFFFFF',
  watermark: '#E5E7EB',
  headerGradientStart: '#F9FAFB',
  headerGradientEnd: '#F3F4F6',
}

/**
 * 字体栈
 */
export const PPT_FONTS = {
  display: '"Microsoft YaHei", "PingFang SC", "Heiti SC", "Segoe UI", Arial, sans-serif',
  body: '"Microsoft YaHei", "PingFang SC", "Segoe UI", Arial, sans-serif',
  number: 'Arial, sans-serif',
}
