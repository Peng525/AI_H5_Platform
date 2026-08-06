/** Estimated generation duration for deck create flow. */

export function estimateQuickDeckSeconds(pageCount) {
  const n = Math.max(1, Math.min(30, Number(pageCount) || 10))
  return 8 + n * 4
}

export function estimatePremiumDeckSeconds(pageCount) {
  const n = Math.max(1, Math.min(30, Number(pageCount) || 8))
  return Math.max(180, 60 + n * 90)
}

/** Conservative range for premium wait UX (5 pages ≈ 6–10 min). */
export function estimatePremiumDeckRange(pageCount) {
  const n = Math.max(1, Math.min(30, Number(pageCount) || 8))
  const typicalSeconds = estimatePremiumDeckSeconds(n)
  const minSeconds = Math.max(180, typicalSeconds - 150)
  const maxSeconds = typicalSeconds + 90
  return { minSeconds, maxSeconds, typicalSeconds }
}

export function formatDurationLabel(totalSeconds) {
  const s = Math.max(0, Math.round(Number(totalSeconds) || 0))
  if (s < 60) return `${s} 秒`
  const m = Math.floor(s / 60)
  const r = s % 60
  if (r === 0) return `${m} 分钟`
  return `${m} 分 ${r} 秒`
}

export function formatPremiumDeckRangeLabel(pageCount) {
  const { minSeconds, maxSeconds } = estimatePremiumDeckRange(pageCount)
  const minM = Math.max(1, Math.round(minSeconds / 60))
  const maxM = Math.max(minM, Math.round(maxSeconds / 60))
  if (minM === maxM) return `约 ${minM} 分钟`
  return `${minM}–${maxM} 分钟`
}

const STAGE_PRE_WEIGHT = 0.02 + 0.03 + 0.1
const STAGE_GENERATING_WEIGHT = 0.75
const STAGE_POST_WEIGHT = 0.05 + 0.03

function stageCompletedFraction(stage, currentPage, totalPages) {
  const st = String(stage || 'queued').toLowerCase()
  if (st === 'queued') return 0.01
  if (st === 'preparing') return 0.02 + 0.015
  if (st === 'strategist') return STAGE_PRE_WEIGHT * 0.85
  if (st === 'generating') {
    const tp = Math.max(1, Number(totalPages) || 1)
    const cp = Math.max(0, Math.min(Number(currentPage) || 0, tp))
    return STAGE_PRE_WEIGHT + STAGE_GENERATING_WEIGHT * (cp / tp)
  }
  if (st === 'postprocessing') {
    return STAGE_PRE_WEIGHT + STAGE_GENERATING_WEIGHT + 0.025
  }
  if (st === 'importing') {
    return STAGE_PRE_WEIGHT + STAGE_GENERATING_WEIGHT + 0.05 + 0.015
  }
  if (st === 'completed') return 1
  return 0
}

/** Stage-weighted remaining seconds for premium overlay (not linear progress extrapolation). */
export function computeStageAwareRemainingSeconds({
  elapsedSeconds,
  stage,
  currentPage = 0,
  totalPages = 0,
  typicalSeconds,
}) {
  const elapsed = Math.max(0, Number(elapsedSeconds) || 0)
  const typical = Math.max(
    60,
    Number(typicalSeconds) || estimatePremiumDeckSeconds(totalPages || 8),
  )
  const fraction = stageCompletedFraction(stage, currentPage, totalPages)
  let remaining = typical * (1 - fraction)
  const expectedElapsed = typical * fraction
  if (elapsed > expectedElapsed + 20) {
    remaining = Math.max(remaining, typical - elapsed)
  }
  return Math.max(0, Math.round(remaining))
}

export function shouldShowPremiumRemaining(stage, currentPage) {
  const st = String(stage || '').toLowerCase()
  if (st === 'generating') return Number(currentPage) >= 1
  if (st === 'postprocessing' || st === 'importing') return true
  return false
}

export function smoothEtaSeconds(prev, next, maxStep = 25) {
  if (next == null) return prev ?? null
  if (prev == null) return next
  const p = Number(prev)
  const n = Number(next)
  if (!Number.isFinite(n)) return p
  if (!Number.isFinite(p)) return n
  const delta = n - p
  if (Math.abs(delta) <= maxStep) return n
  return Math.round(p + Math.sign(delta) * maxStep)
}

/** @deprecated Prefer computeStageAwareRemainingSeconds for premium polling. */
export function computeDynamicRemainingSeconds(elapsedSeconds, progressPercent) {
  const elapsed = Math.max(0, Number(elapsedSeconds) || 0)
  const progress = Number(progressPercent)
  if (progress < 10 || elapsed < 15) return null
  const total = Math.round(elapsed / (progress / 100))
  return Math.max(0, total - elapsed)
}
