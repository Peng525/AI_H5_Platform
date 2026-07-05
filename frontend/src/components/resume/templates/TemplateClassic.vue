<template>
  <ClassicBlueTemplate v-bind="$attrs" />
</template>

<script setup>
import ClassicBlueTemplate from '../ClassicBlueTemplate.vue'

defineOptions({ inheritAttrs: false })
</script>
