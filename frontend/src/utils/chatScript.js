import { getChatStylePreset, DEFAULT_CHAT_STYLE } from '../constants/chatStylePresets.js'

export function genChatId(prefix = 'c') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
}

export function defaultParticipants() {
  return [
    { id: 'p_owner', name: '用户A', avatar: '', role: 'owner', defaultSide: 'right' },
    { id: 'p_guest', name: '用户B', avatar: '', role: 'guest', defaultSide: 'left' },
    { id: 'p_guest2', name: '用户C', avatar: '', role: 'guest', defaultSide: 'left' },
  ]
}

export function defaultTimeline() {
  return [
    { id: genChatId('ts'), type: 'timestamp', text: '15:30' },
    {
      id: genChatId('m'),
      type: 'message',
      participantId: 'p_owner',
      side: 'right',
      text: '你好，易企秀。',
    },
    {
      id: genChatId('m'),
      type: 'message',
      participantId: 'p_guest',
      side: 'left',
      text: '你好，海报。',
    },
  ]
}

function legacyMessageToTimeline(messages) {
  const ownerId = 'p_owner'
  const guestId = 'p_guest'
  const participants = [
    { id: ownerId, name: '我', avatar: '', role: 'owner', defaultSide: 'right' },
    { id: guestId, name: '小助手', avatar: '', role: 'guest', defaultSide: 'left' },
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

  participants = participants.map((p, i) => ({
    id: p.id || genChatId('p'),
    name: p.name || `用户${String.fromCharCode(65 + i)}`,
    avatar: p.avatar || '',
    role: p.role === 'owner' ? 'owner' : 'guest',
    defaultSide: p.defaultSide === 'right' ? 'right' : 'left',
  }))

  timeline = timeline.map((item) => {
    if (item.type === 'timestamp') {
      return { id: item.id || genChatId('ts'), type: 'timestamp', text: item.text || '12:00' }
    }
    const side = item.side === 'right' ? 'right' : 'left'
    return {
      id: item.id || genChatId('m'),
      type: 'message',
      participantId: item.participantId || (side === 'right' ? 'p_owner' : 'p_guest'),
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
      avatar: p.avatar || '',
      role: p.role,
      defaultSide: p.defaultSide,
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

export function getParticipantSide(participantId, participants) {
  const p = getParticipant(participants, participantId)
  return p?.defaultSide === 'right' ? 'right' : 'left'
}

export function resolveMessageItem(item, participants) {
  if (item.type === 'timestamp') return item
  const p = getParticipant(participants, item.participantId)
  const side = item.side || p?.defaultSide || 'left'
  return {
    ...item,
    side,
    name: p?.name || '',
    avatar: p?.avatar || '',
    isOwner: p?.role === 'owner' || side === 'right',
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
