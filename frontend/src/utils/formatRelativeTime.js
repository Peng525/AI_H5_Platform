export function formatRelativeTime(iso) {
  if (!iso) return ''
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return ''
  const sec = Math.floor((Date.now() - then) / 1000)
  if (sec < 60) return '刚刚编辑'
  const min = Math.floor(sec / 60)
  if (min < 60) return `${min} 分钟前编辑`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr} 小时前编辑`
  const day = Math.floor(hr / 24)
  if (day < 30) return `${day} 天前编辑`
  const month = Math.floor(day / 30)
  if (month < 12) return `${month} 个月前编辑`
  return `${Math.floor(month / 12)} 年前编辑`
}
