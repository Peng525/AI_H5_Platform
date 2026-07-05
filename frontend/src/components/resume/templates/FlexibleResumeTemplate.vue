<template>
  <article
    class="bg-white shadow-lg mx-auto w-full max-w-[794px] min-h-[1123px] text-slate-800"
    :class="rootClass"
  >
    <header :class="headerClass">
      <h1 class="font-bold tracking-wide" :class="titleClass">{{ theme.header }}</h1>
      <ResumeEditableCell
        class="mt-2"
        bind="basics.motto"
        :model-value="cellValue('basics.motto')"
        :style-patch="cellStyle('basics.motto')"
        :selected="selectedBind === 'basics.motto'"
        :editing="editingBind === 'basics.motto'"
        placeholder="一句话简介"
        @select="$emit('select', $event)"
        @edit="$emit('edit', $event)"
        @update:model-value="$emit('update-value', 'basics.motto', $event)"
        @blur="$emit('blur')"
      />
    </header>

    <div :class="bodyGridClass">
      <aside v-if="layout === 'sidebar'" class="space-y-4 bg-slate-50 p-4 rounded-lg">
        <div
          class="w-24 h-28 mx-auto border border-dashed border-slate-300 flex items-center justify-center text-xs text-slate-400 cursor-pointer"
          @click="$emit('photo-click')"
        >
          {{ photoUrl ? '照片' : '上传照片' }}
        </div>
        <ResumeEditableCell
          bind="basics.phone"
          label="电话"
          :model-value="cellValue('basics.phone')"
          :style-patch="cellStyle('basics.phone')"
          :selected="selectedBind === 'basics.phone'"
          :editing="editingBind === 'basics.phone'"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'basics.phone', $event)"
          @blur="$emit('blur')"
        />
        <ResumeEditableCell
          bind="basics.email"
          label="邮箱"
          :model-value="cellValue('basics.email')"
          :style-patch="cellStyle('basics.email')"
          :selected="selectedBind === 'basics.email'"
          :editing="editingBind === 'basics.email'"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'basics.email', $event)"
          @blur="$emit('blur')"
        />
      </aside>

      <div class="min-w-0 space-y-1">
        <section :class="sectionClass(layout, 'basics')">
          <ResumeSectionHeader title="基本信息" :accent="theme.accent" :variant="headerVariant" />
          <div class="mt-2 space-y-2" :class="layout === 'two-column' ? 'grid grid-cols-2 gap-3' : ''">
            <ResumeRow :cols="layout === 'single' ? 1 : 2">
              <ResumeEditableCell
                bind="basics.name"
                label="姓名"
                :model-value="cellValue('basics.name')"
                :style-patch="cellStyle('basics.name')"
                :selected="selectedBind === 'basics.name'"
                :editing="editingBind === 'basics.name'"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', 'basics.name', $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                v-if="layout !== 'sidebar'"
                bind="basics.phone"
                label="电话"
                :model-value="cellValue('basics.phone')"
                :style-patch="cellStyle('basics.phone')"
                :selected="selectedBind === 'basics.phone'"
                :editing="editingBind === 'basics.phone'"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', 'basics.phone', $event)"
                @blur="$emit('blur')"
              />
            </ResumeRow>
            <ResumeRow :cols="2">
              <ResumeEditableCell
                bind="basics.email"
                label="邮箱"
                :model-value="cellValue('basics.email')"
                :style-patch="cellStyle('basics.email')"
                :selected="selectedBind === 'basics.email'"
                :editing="editingBind === 'basics.email'"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', 'basics.email', $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                bind="basics.gender"
                label="性别"
                :model-value="cellValue('basics.gender')"
                :style-patch="cellStyle('basics.gender')"
                :selected="selectedBind === 'basics.gender'"
                :editing="editingBind === 'basics.gender'"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', 'basics.gender', $event)"
                @blur="$emit('blur')"
              />
            </ResumeRow>
          </div>
        </section>

        <section :class="sectionClass(layout, 'job')">
          <ResumeSectionHeader title="求职意向" :accent="theme.accent" :variant="headerVariant" />
          <ResumeRow :cols="layout === 'tech' ? 1 : 2" class="mt-2">
            <ResumeEditableCell
              bind="job_intention.position"
              label="岗位"
              :model-value="cellValue('job_intention.position')"
              :style-patch="cellStyle('job_intention.position')"
              :selected="selectedBind === 'job_intention.position'"
              :editing="editingBind === 'job_intention.position'"
              @select="$emit('select', $event)"
              @edit="$emit('edit', $event)"
              @update:model-value="$emit('update-value', 'job_intention.position', $event)"
              @blur="$emit('blur')"
            />
            <ResumeEditableCell
              bind="job_intention.city"
              label="城市"
              :model-value="cellValue('job_intention.city')"
              :style-patch="cellStyle('job_intention.city')"
              :selected="selectedBind === 'job_intention.city'"
              :editing="editingBind === 'job_intention.city'"
              @select="$emit('select', $event)"
              @edit="$emit('edit', $event)"
              @update:model-value="$emit('update-value', 'job_intention.city', $event)"
              @blur="$emit('blur')"
            />
          </ResumeRow>
        </section>

        <section :class="sectionClass(layout, 'education')">
          <ResumeSectionHeader title="教育背景" :accent="theme.accent" :variant="headerVariant" />
          <div v-for="(edu, i) in educationRows" :key="`edu-${i}`" class="mt-2 space-y-1">
            <ResumeRow :cols="3">
              <ResumeEditableCell
                :bind="`education[${i}].period`"
                label="时间"
                :model-value="cellValue(`education[${i}].period`)"
                :style-patch="cellStyle(`education[${i}].period`)"
                :selected="selectedBind === `education[${i}].period`"
                :editing="editingBind === `education[${i}].period`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `education[${i}].period`, $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                :bind="`education[${i}].school`"
                label="学校"
                :model-value="cellValue(`education[${i}].school`)"
                :style-patch="cellStyle(`education[${i}].school`)"
                :selected="selectedBind === `education[${i}].school`"
                :editing="editingBind === `education[${i}].school`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `education[${i}].school`, $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                :bind="`education[${i}].degree`"
                label="学历"
                :model-value="cellValue(`education[${i}].degree`)"
                :style-patch="cellStyle(`education[${i}].degree`)"
                :selected="selectedBind === `education[${i}].degree`"
                :editing="editingBind === `education[${i}].degree`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `education[${i}].degree`, $event)"
                @blur="$emit('blur')"
              />
            </ResumeRow>
          </div>
        </section>

        <section :class="sectionClass(layout, 'experience')">
          <ResumeSectionHeader title="工作经历" :accent="theme.accent" :variant="headerVariant" />
          <div v-for="(job, i) in experienceRows" :key="`exp-${i}`" class="mt-3 space-y-1">
            <ResumeRow :cols="3">
              <ResumeEditableCell
                :bind="`experience[${i}].period`"
                label="时间"
                :model-value="cellValue(`experience[${i}].period`)"
                :style-patch="cellStyle(`experience[${i}].period`)"
                :selected="selectedBind === `experience[${i}].period`"
                :editing="editingBind === `experience[${i}].period`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `experience[${i}].period`, $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                :bind="`experience[${i}].company`"
                label="公司"
                :model-value="cellValue(`experience[${i}].company`)"
                :style-patch="cellStyle(`experience[${i}].company`)"
                :selected="selectedBind === `experience[${i}].company`"
                :editing="editingBind === `experience[${i}].company`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `experience[${i}].company`, $event)"
                @blur="$emit('blur')"
              />
              <ResumeEditableCell
                :bind="`experience[${i}].title`"
                label="职位"
                :model-value="cellValue(`experience[${i}].title`)"
                :style-patch="cellStyle(`experience[${i}].title`)"
                :selected="selectedBind === `experience[${i}].title`"
                :editing="editingBind === `experience[${i}].title`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `experience[${i}].title`, $event)"
                @blur="$emit('blur')"
              />
            </ResumeRow>
            <div v-for="bi in bulletRows(job)" :key="`exp-${i}-b-${bi}`" class="pl-2">
              <ResumeEditableCell
                :bind="`experience[${i}].bullets[${bi}]`"
                :model-value="cellValue(`experience[${i}].bullets[${bi}]`)"
                :style-patch="cellStyle(`experience[${i}].bullets[${bi}]`)"
                :selected="selectedBind === `experience[${i}].bullets[${bi}]`"
                :editing="editingBind === `experience[${i}].bullets[${bi}]`"
                placeholder="• 工作成果"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `experience[${i}].bullets[${bi}]`, $event)"
                @blur="$emit('blur')"
              />
            </div>
          </div>
        </section>

        <section v-if="skillBars.length" :class="sectionClass(layout, 'skills')">
          <ResumeSectionHeader title="技能特长" :accent="theme.accent" :variant="headerVariant" />
          <div class="mt-2 space-y-2">
            <div v-for="(bar, i) in skillBars" :key="`skill-${i}`" class="flex items-center gap-3">
              <ResumeEditableCell
                class="w-24 shrink-0"
                :bind="`skill_bars[${i}].name`"
                :model-value="cellValue(`skill_bars[${i}].name`)"
                :style-patch="cellStyle(`skill_bars[${i}].name`)"
                :selected="selectedBind === `skill_bars[${i}].name`"
                :editing="editingBind === `skill_bars[${i}].name`"
                @select="$emit('select', $event)"
                @edit="$emit('edit', $event)"
                @update:model-value="$emit('update-value', `skill_bars[${i}].name`, $event)"
                @blur="$emit('blur')"
              />
              <div class="flex-1 h-2 bg-slate-200 rounded">
                <div class="h-full rounded" :style="{ width: `${bar.level || 70}%`, backgroundColor: theme.accent }" />
              </div>
            </div>
          </div>
        </section>

        <section :class="sectionClass(layout, 'self')">
          <ResumeSectionHeader title="自我评价" :accent="theme.accent" :variant="headerVariant" />
          <ResumeEditableCell
            class="mt-2"
            bind="self_evaluation"
            :model-value="cellValue('self_evaluation')"
            :style-patch="cellStyle('self_evaluation')"
            :selected="selectedBind === 'self_evaluation'"
            :editing="editingBind === 'self_evaluation'"
            multiline
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', 'self_evaluation', $event)"
            @blur="$emit('blur')"
          />
        </section>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import ResumeEditableCell from '../ResumeEditableCell.vue'
import ResumeRow from '../ResumeRow.vue'
import ResumeSectionHeader from '../ResumeSectionHeader.vue'
import { sectionClass, themeForTemplate } from '../../../utils/resumeTemplateShared.js'

const props = defineProps({
  structured: { type: Object, required: true },
  selectedBind: { type: String, default: '' },
  editingBind: { type: String, default: '' },
  photoUrl: { type: String, default: '' },
  cellValue: { type: Function, required: true },
  cellStyle: { type: Function, required: true },
  layout: { type: String, default: 'single' },
  templateId: { type: String, default: 'template2' },
})

defineEmits(['select', 'edit', 'blur', 'update-value', 'photo-click'])

const theme = computed(() => themeForTemplate(props.templateId, props.structured))

const headerVariant = computed(() => (props.layout === 'modern' ? 'underline' : 'bar'))

const rootClass = computed(() => ({
  'px-6 py-5': props.layout === 'single' || props.layout === 'modern',
  'px-8 py-6': props.layout === 'two-column' || props.layout === 'multi',
  'px-10 py-8': props.layout === 'magazine',
  'px-6 py-6 font-mono text-sm': props.layout === 'tech',
  'px-8 py-6': props.layout === 'sidebar',
}))

const headerClass = computed(() => ({
  'text-center mb-4': props.layout !== 'magazine',
  'mb-8': props.layout === 'magazine',
}))

const titleClass = computed(() => ({
  'text-2xl': props.layout !== 'magazine' && props.layout !== 'tech',
  'text-4xl uppercase tracking-widest': props.layout === 'magazine',
  'text-xl': props.layout === 'tech',
}))

const bodyGridClass = computed(() => ({
  'grid grid-cols-[180px_1fr] gap-6': props.layout === 'sidebar',
}))

const educationRows = computed(() => {
  const list = props.structured?.education || []
  return list.length ? list : [{}]
})

const experienceRows = computed(() => {
  const list = props.structured?.experience || []
  return list.length ? list : [{}]
})

const skillBars = computed(() => props.structured?.skill_bars || [])

function bulletRows(job) {
  const bullets = job?.bullets || []
  const count = Math.max(bullets.length, 2)
  return Array.from({ length: count }, (_, i) => i)
}
</script>
