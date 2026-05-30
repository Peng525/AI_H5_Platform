<template>
  <div class="min-h-screen bg-background flex flex-col">
    <AppShell />
    <div class="max-w-2xl mx-auto px-4 py-8 md:py-12 flex-1 w-full">
      <h1 class="text-2xl font-bold mb-2">使用帮助</h1>
      <p class="text-sm text-on-surface-variant mb-8">常见问题与编辑器要点</p>

      <section class="space-y-6 text-sm">
        <article v-for="item in faq" :key="item.q" class="bg-white rounded-xl border border-outline-variant p-5">
          <h2 class="font-semibold text-on-surface">{{ item.q }}</h2>
          <p class="mt-2 text-on-surface-variant leading-relaxed">{{ item.a }}</p>
        </article>
      </section>

      <section class="mt-10 bg-white rounded-xl border border-outline-variant p-5 text-sm">
        <h2 class="font-semibold mb-2">编辑器快捷键</h2>
        <ul class="space-y-1 text-on-surface-variant">
          <li>撤回 / 重做：Ctrl+Z / Ctrl+Y</li>
          <li>复制 / 粘贴：Ctrl+C / Ctrl+V</li>
          <li>多选：Ctrl / Shift + 点击</li>
          <li>帮助面板：F1（在编辑器内）</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import AppShell from '../components/AppShell.vue'

const faq = [
  {
    q: 'AI 生图失败怎么办？',
    a: '请确认服务器 .env 中已配置 LLM_RELAY_* 或 LLM_OFFICIAL_*，且容器能访问外网。管理员可在系统设置页测试生图连通性。',
  },
  {
    q: '背景音乐列表为空？',
    a: '将 MP3 文件放入 backend/static/bgm/ 目录后重启服务，或在编辑器「工具箱 → 音乐」中启用 BGM。',
  },
  {
    q: '分享链接打不开？',
    a: '确认项目已发布且 share_slug 有效；检查服务器 8080 端口与安全组是否放行；HTTPS 需配置反向代理。',
  },
  {
    q: '如何添加 AI 配图？',
    a: '右侧 AI 助手 → 选择生图分辨率 → 填写描述 → AI 生图 → 预览后选择适应宽度/填充/原图添加到画布。',
  },
  {
    q: '升级支付后未到账？',
    a: '微信个人码支付需手动输入金额；支付后等待轮询或联系管理员在控制台确认订单。',
  },
]
</script>
