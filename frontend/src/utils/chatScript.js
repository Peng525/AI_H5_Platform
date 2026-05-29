import { getChatStylePreset, DEFAULT_CHAT_STYLE } from '../constants/chatStylePresets.js'

export function genChatId(prefix = 'c') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
}

export function defaultParticipants() {
  return [
    { id: 'p_a', name: '用户A', avatar: '', useDefaultAvatar: true },
    { id: 'p_b', name: '用户B', avatar: '', useDefaultAvatar: true },
  ]
}

export function defaultTimeline() {
  return [
    { id: genChatId('ts'), type: 'timestamp', text: '15:30' },
    {
      id: genChatId('m'),
      type: 'message',
      participantId: 'p_a',
      side: 'right',
      text: '你好，易企秀。',
    },
    {
      id: genChatId('m'),
      type: 'message',
      participantId: 'p_b',
      side: 'left',
      text: '你好，海报。',
    },
  ]
}

function legacyMessageToTimeline(messages) {
  const ownerId = 'p_a'
  const guestId = 'p_b'
  const participants = [
    { id: ownerId, name: '我', avatar: '', useDefaultAvatar: true },
    { id: guestId, name: '小助手', avatar: '', useDefaultAvatar: true },
  ]
  const timeline = messages.map((m) => {
    const side = m.side === 'right' ? 'right' : 'left'
    const pid = side === 'right' ? ownerId : guestId
    const p = participants.find((x) => x.id === pid)
    if (m.name && p) p.name = m.name
    if (m.avatar && p) p.avatar = m.avatar
    return {
      id: m.id || genChatId('m'),
      type: 'message',
      participantId: pid,
      side,
      text: m.text || '',
      avatar: m.avatar || '',
      name: m.name || '',
    }
  })
  return { participants, timeline }
}

export function normalizeChatScript(raw) {
  const src = raw && typeof raw === 'object' ? raw : {}
  const enabled = !!src.enabled
  const autoAdvanceMs = Number(src.autoAdvanceMs || 0)

  let style = { ...DEFAULT_CHAT_STYLE, ...(src.style || {}) }
  if (src.style?.presetId) {
    const preset = getChatStylePreset(src.style.presetId)
    if (preset) style = { ...preset.style, ...src.style }
  }

  let participants = Array.isArray(src.participants) ? src.participants.map((p) => ({ ...p })) : null
  let timeline = Array.isArray(src.timeline) ? src.timeline.map((t) => ({ ...t })) : null

  if (!timeline?.length && Array.isArray(src.messages) && src.messages.length) {
    const legacy = legacyMessageToTimeline(src.messages)
    participants = legacy.participants
    timeline = legacy.timeline
  }

  if (!participants?.length) participants = defaultParticipants()
  if (!timeline?.length) timeline = defaultTimeline()

  participants = participants.map((p, i) => {
    const useDefault = p.useDefaultAvatar !== false && !p.avatar
    return {
      id: p.id || genChatId('p'),
      name: p.name || `用户${String.fromCharCode(65 + i)}`,
      avatar: useDefault ? '' : p.avatar || '',
      useDefaultAvatar: useDefault,
    }
  })

  timeline = timeline.map((item) => {
    if (item.type === 'timestamp') {
      return { id: item.id || genChatId('ts'), type: 'timestamp', text: item.text || '12:00' }
    }
    const side = item.side === 'right' ? 'right' : item.side === 'left' ? 'left' : getParticipantSide(item.participantId, participants)
    return {
      id: item.id || genChatId('m'),
      type: 'message',
      participantId: item.participantId || participants[0]?.id,
      side,
      text: item.text || '',
    }
  })

  return { enabled, autoAdvanceMs, style, participants, timeline }
}

export function serializeChatScript(state) {
  const n = normalizeChatScript(state)
  return {
    enabled: n.enabled,
    autoAdvanceMs: n.autoAdvanceMs,
    style: { ...n.style },
    participants: n.participants.map((p) => ({
      id: p.id,
      name: p.name,
      avatar: p.useDefaultAvatar ? '' : p.avatar || '',
      useDefaultAvatar: !!p.useDefaultAvatar,
    })),
    timeline: n.timeline.map((t) => {
      if (t.type === 'timestamp') return { id: t.id, type: 'timestamp', text: t.text }
      return {
        id: t.id,
        type: 'message',
        participantId: t.participantId,
        side: t.side,
        text: t.text || '',
      }
    }),
  }
}

export function getParticipant(participants, id) {
  return (participants || []).find((p) => p.id === id) || null
}

export function sideForParticipantIndex(index) {
  return index % 2 === 0 ? 'right' : 'left'
}

export function getParticipantSide(participantId, participants) {
  const idx = (participants || []).findIndex((p) => p.id === participantId)
  if (idx < 0) return 'left'
  return sideForParticipantIndex(idx)
}

export function parseTimeToMinutes(text) {
  const m = String(text || '').trim().match(/^(\d{1,2}):(\d{2})$/)
  if (!m) return 15 * 60 + 30
  return parseInt(m[1], 10) * 60 + parseInt(m[2], 10)
}

export function formatMinutesToTime(mins) {
  const total = ((mins % (24 * 60)) + 24 * 60) % (24 * 60)
  const h = Math.floor(total / 60)
  const m = total % 60
  return `${h}:${String(m).padStart(2, '0')}`
}

export function nextTimestampAfterTimeline(timeline, beforeIndex = timeline.length) {
  let last = 15 * 60 + 30
  for (let i = 0; i < beforeIndex; i++) {
    if (timeline[i]?.type === 'timestamp') last = parseTimeToMinutes(timeline[i].text)
  }
  return formatMinutesToTime(last + 1)
}

export function createParticipantAtIndex(index) {
  return {
    id: genChatId('p'),
    name: `用户${String.fromCharCode(65 + index)}`,
    avatar: '',
    useDefaultAvatar: true,
  }
}

export function resolveMessageItem(item, participants) {
  if (item.type === 'timestamp') return item
  const p = getParticipant(participants, item.participantId)
  const side = item.side || getParticipantSide(item.participantId, participants)
  const avatar = p?.useDefaultAvatar ? '' : p?.avatar || ''
  return {
    ...item,
    side,
    name: p?.name || '',
    avatar,
    isOwner: side === 'right',
  }
}

export function timelineToLegacyMessages(script) {
  const n = normalizeChatScript(script)
  return n.timeline
    .filter((t) => t.type === 'message')
    .map((t) => {
      const r = resolveMessageItem(t, n.participants)
      return {
        id: r.id,
        side: r.side,
        avatar: r.avatar,
        name: r.name,
        text: r.text,
      }
    })
}

export function emptyChatScript() {
  return serializeChatScript({
    enabled: true,
    autoAdvanceMs: 0,
    style: { ...DEFAULT_CHAT_STYLE },
    participants: defaultParticipants(),
    timeline: defaultTimeline(),
  })
}
