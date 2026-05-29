import { slideBackgroundCSSValue } from './slideBackground.js'
import { resolveMessageItem } from './chatScript.js'

export function dialogueBackgroundStyle(style) {
  const bg = style?.background || '#ededed'
  return { background: slideBackgroundCSSValue(bg) }
}

export function avatarInitial(name, side) {
  const n = (name || (side === 'right' ? '我' : 'TA')).trim()
  return n.slice(0, 1).toUpperCase()
}

export function bubbleInlineStyle(isOwner, style) {
  const s = style || {}
  const radius = Number(s.bubbleRadius ?? 4)
  return {
    background: isOwner ? s.ownerBgColor || '#95EC69' : s.otherBgColor || '#ffffff',
    color: isOwner ? s.ownerTextColor || '#111' : s.otherTextColor || '#111',
    borderRadius: `${radius}px`,
  }
}

export function avatarInlineStyle(style) {
  const radius = Number(style?.avatarRadius ?? 4)
  return { borderRadius: `${radius}px` }
}

export function timestampStyle(style) {
  return { color: style?.dateTextColor || '#999999' }
}

export function enrichTimelineItem(item, participants) {
  if (item.type === 'timestamp') return item
  return resolveMessageItem(item, participants)
}

export function buildRenderableTimeline(script) {
  const participants = script?.participants || []
  return (script?.timeline || []).map((item) => enrichTimelineItem(item, participants))
}
