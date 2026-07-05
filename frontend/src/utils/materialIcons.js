const ICON_ALIASES = {
  activity: 'monitoring',
  ai: 'auto_awesome',
  analytics: 'analytics',
  archive: 'inventory_2',
  award: 'workspace_premium',
  bar_chart: 'bar_chart',
  bar_chart2: 'bar_chart',
  bar_chart3: 'bar_chart',
  bar_chart_2: 'bar_chart',
  bar_chart_3: 'bar_chart',
  book: 'menu_book',
  brain: 'psychology',
  briefcase: 'business_center',
  building: 'apartment',
  calendar: 'calendar_month',
  check: 'check_circle',
  check_circle: 'check_circle',
  circle: 'circle',
  cloud: 'cloud',
  cpu: 'memory',
  database: 'database',
  dollar_sign: 'attach_money',
  file_text: 'article',
  flag: 'flag',
  gauge: 'speed',
  globe: 'public',
  graph: 'monitoring',
  group: 'group',
  groups: 'groups',
  heart: 'favorite',
  image: 'image',
  layers: 'layers',
  lightbulb: 'lightbulb',
  line_chart: 'show_chart',
  lock: 'lock',
  mail: 'mail',
  map: 'map',
  memory: 'memory',
  message: 'forum',
  monitor: 'monitor',
  monitoring: 'monitoring',
  pie_chart: 'pie_chart',
  play: 'play_arrow',
  rocket: 'rocket_launch',
  school: 'school',
  search: 'search',
  settings: 'settings',
  shield: 'shield',
  shopping_cart: 'shopping_cart',
  slideshow: 'slideshow',
  sparkles: 'auto_awesome',
  star: 'star',
  target: 'target',
  timer: 'timer',
  trending_up: 'trending_up',
  trophy: 'emoji_events',
  user: 'person',
  users: 'groups',
  wallet: 'account_balance_wallet',
  zap: 'bolt',
}

export function normalizeMaterialIconName(name, fallback = 'circle') {
  const raw = String(name || '').trim()
  if (!raw) return fallback

  const normalized = raw
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .replace(/[^a-zA-Z0-9_]/g, '')
    .toLowerCase()

  return ICON_ALIASES[normalized] || fallback
}
