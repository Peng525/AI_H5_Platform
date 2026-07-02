<template>
  <article class="bg-white shadow-lg mx-auto w-full max-w-[794px] min-h-[1123px] px-8 py-6 text-slate-800">
    <header class="text-center mb-4">
      <h1 class="text-2xl font-bold tracking-wide">个人简历</h1>
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

    <section class="mb-4">
      <ResumeSectionHeader title="基本信息" />
      <div class="mt-2 grid grid-cols-[1fr_120px] gap-4">
        <div class="space-y-2">
          <ResumeRow :cols="2">
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
          <ResumeRow :cols="2">
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
          </ResumeRow>
          <ResumeRow :cols="2">
            <ResumeEditableCell
              bind="basics.age"
              label="年龄"
              :model-value="cellValue('basics.age')"
              :style-patch="cellStyle('basics.age')"
              :selected="selectedBind === 'basics.age'"
              :editing="editingBind === 'basics.age'"
              @select="$emit('select', $event)"
              @edit="$emit('edit', $event)"
              @update:model-value="$emit('update-value', 'basics.age', $event)"
              @blur="$emit('blur')"
            />
            <ResumeEditableCell
              bind="basics.native_place"
              label="籍贯"
              :model-value="cellValue('basics.native_place')"
              :style-patch="cellStyle('basics.native_place')"
              :selected="selectedBind === 'basics.native_place'"
              :editing="editingBind === 'basics.native_place'"
              @select="$emit('select', $event)"
              @edit="$emit('edit', $event)"
              @update:model-value="$emit('update-value', 'basics.native_place', $event)"
              @blur="$emit('blur')"
            />
          </ResumeRow>
        </div>
        <div
          class="border border-dashed border-slate-300 rounded flex flex-col items-center justify-center bg-slate-50 cursor-pointer overflow-hidden min-h-[140px]"
          @click="$emit('photo-click')"
        >
          <img v-if="photoUrl" :src="photoUrl" alt="证件照" class="w-full h-full object-cover" />
          <template v-else>
            <span class="material-symbols-outlined text-3xl text-slate-400">person</span>
            <span class="text-xs text-slate-500 mt-1">上传照片</span>
          </template>
        </div>
      </div>
    </section>

    <section class="mb-4">
      <ResumeSectionHeader title="求职意向" />
      <ResumeRow :cols="2" class="mt-2">
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
      <ResumeRow :cols="2" class="mt-2">
        <ResumeEditableCell
          bind="job_intention.salary"
          label="期望薪资"
          :model-value="cellValue('job_intention.salary')"
          :style-patch="cellStyle('job_intention.salary')"
          :selected="selectedBind === 'job_intention.salary'"
          :editing="editingBind === 'job_intention.salary'"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'job_intention.salary', $event)"
          @blur="$emit('blur')"
        />
        <ResumeEditableCell
          bind="job_intention.availability"
          label="到岗时间"
          :model-value="cellValue('job_intention.availability')"
          :style-patch="cellStyle('job_intention.availability')"
          :selected="selectedBind === 'job_intention.availability'"
          :editing="editingBind === 'job_intention.availability'"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'job_intention.availability', $event)"
          @blur="$emit('blur')"
        />
      </ResumeRow>
    </section>

    <section class="mb-4">
      <ResumeSectionHeader title="教育背景" />
      <div v-for="(ed, i) in educationRows" :key="'ed-' + i" class="mt-2 space-y-1">
        <ResumeRow :cols="3">
          <ResumeEditableCell
            :bind="`education[${i}].period`"
            :model-value="cellValue(`education[${i}].period`)"
            :style-patch="cellStyle(`education[${i}].period`)"
            :selected="selectedBind === `education[${i}].period`"
            :editing="editingBind === `education[${i}].period`"
            placeholder="时间"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `education[${i}].period`, $event)"
            @blur="$emit('blur')"
          />
          <ResumeEditableCell
            :bind="`education[${i}].school`"
            :model-value="cellValue(`education[${i}].school`)"
            :style-patch="cellStyle(`education[${i}].school`)"
            :selected="selectedBind === `education[${i}].school`"
            :editing="editingBind === `education[${i}].school`"
            placeholder="学校"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `education[${i}].school`, $event)"
            @blur="$emit('blur')"
          />
          <ResumeEditableCell
            :bind="`education[${i}].degree`"
            :model-value="cellValue(`education[${i}].degree`)"
            :style-patch="cellStyle(`education[${i}].degree`)"
            :selected="selectedBind === `education[${i}].degree`"
            :editing="editingBind === `education[${i}].degree`"
            placeholder="专业/学历"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `education[${i}].degree`, $event)"
            @blur="$emit('blur')"
          />
        </ResumeRow>
        <ResumeRow :cols="1">
          <ResumeEditableCell
            :bind="`education[${i}].details`"
            :model-value="cellValue(`education[${i}].details`)"
            :style-patch="cellStyle(`education[${i}].details`)"
            :selected="selectedBind === `education[${i}].details`"
            :editing="editingBind === `education[${i}].details`"
            placeholder="主修课程、荣誉等"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `education[${i}].details`, $event)"
            @blur="$emit('blur')"
          />
        </ResumeRow>
      </div>
    </section>

    <section class="mb-4">
      <ResumeSectionHeader title="工作经历" />
      <div v-for="(job, i) in experienceRows" :key="'exp-' + i" class="mt-2 space-y-1">
        <ResumeRow :cols="3">
          <ResumeEditableCell
            :bind="`experience[${i}].period`"
            :model-value="cellValue(`experience[${i}].period`)"
            :style-patch="cellStyle(`experience[${i}].period`)"
            :selected="selectedBind === `experience[${i}].period`"
            :editing="editingBind === `experience[${i}].period`"
            placeholder="时间"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `experience[${i}].period`, $event)"
            @blur="$emit('blur')"
          />
          <ResumeEditableCell
            :bind="`experience[${i}].company`"
            :model-value="cellValue(`experience[${i}].company`)"
            :style-patch="cellStyle(`experience[${i}].company`)"
            :selected="selectedBind === `experience[${i}].company`"
            :editing="editingBind === `experience[${i}].company`"
            placeholder="公司"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `experience[${i}].company`, $event)"
            @blur="$emit('blur')"
          />
          <ResumeEditableCell
            :bind="`experience[${i}].title`"
            :model-value="cellValue(`experience[${i}].title`)"
            :style-patch="cellStyle(`experience[${i}].title`)"
            :selected="selectedBind === `experience[${i}].title`"
            :editing="editingBind === `experience[${i}].title`"
            placeholder="职位"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `experience[${i}].title`, $event)"
            @blur="$emit('blur')"
          />
        </ResumeRow>
        <ResumeRow v-for="(b, j) in bulletRows(job)" :key="'b-' + i + '-' + j" :cols="1">
          <ResumeEditableCell
            :bind="`experience[${i}].bullets[${j}]`"
            :model-value="cellValue(`experience[${i}].bullets[${j}]`)"
            :style-patch="cellStyle(`experience[${i}].bullets[${j}]`)"
            :selected="selectedBind === `experience[${i}].bullets[${j}]`"
            :editing="editingBind === `experience[${i}].bullets[${j}]`"
            :placeholder="`工作内容 ${j + 1}`"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `experience[${i}].bullets[${j}]`, $event)"
            @blur="$emit('blur')"
          />
        </ResumeRow>
      </div>
    </section>

    <section class="mb-4">
      <ResumeSectionHeader title="技能特长" />
      <div v-for="(bar, i) in skillBars" :key="'skill-' + i" class="mt-3">
        <ResumeRow :cols="2">
          <ResumeEditableCell
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
          <ResumeEditableCell
            :bind="`skill_bars[${i}].label`"
            :model-value="cellValue(`skill_bars[${i}].label`)"
            :style-patch="cellStyle(`skill_bars[${i}].label`)"
            :selected="selectedBind === `skill_bars[${i}].label`"
            :editing="editingBind === `skill_bars[${i}].label`"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @update:model-value="$emit('update-value', `skill_bars[${i}].label`, $event)"
            @blur="$emit('blur')"
          />
        </ResumeRow>
        <div class="mt-1 h-2 bg-slate-200 rounded overflow-hidden">
          <div
            class="h-full bg-[#2563eb] rounded transition-all"
            :style="{ width: `${bar.level || 70}%` }"
          />
        </div>
      </div>
    </section>

    <section class="mb-4">
      <ResumeSectionHeader title="荣誉证书" />
      <ResumeRow :cols="1" class="mt-2">
        <ResumeEditableCell
          bind="honors[0]"
          :model-value="cellValue('honors[0]')"
          :style-patch="cellStyle('honors[0]')"
          :selected="selectedBind === 'honors[0]'"
          :editing="editingBind === 'honors[0]'"
          placeholder="每行一项荣誉"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'honors[0]', $event)"
          @blur="$emit('blur')"
        />
      </ResumeRow>
    </section>

    <section>
      <ResumeSectionHeader title="自我评价" />
      <ResumeRow :cols="1" class="mt-2">
        <ResumeEditableCell
          bind="self_evaluation"
          :model-value="cellValue('self_evaluation')"
          :style-patch="cellStyle('self_evaluation')"
          :selected="selectedBind === 'self_evaluation'"
          :editing="editingBind === 'self_evaluation'"
          placeholder="自我评价"
          @select="$emit('select', $event)"
          @edit="$emit('edit', $event)"
          @update:model-value="$emit('update-value', 'self_evaluation', $event)"
          @blur="$emit('blur')"
        />
      </ResumeRow>
    </section>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import ResumeEditableCell from './ResumeEditableCell.vue'
import ResumeRow from './ResumeRow.vue'
import ResumeSectionHeader from './ResumeSectionHeader.vue'

const props = defineProps({
  structured: { type: Object, required: true },
  selectedBind: { type: String, default: '' },
  editingBind: { type: String, default: '' },
  photoUrl: { type: String, default: '' },
  cellValue: { type: Function, required: true },
  cellStyle: { type: Function, required: true },
})

defineEmits(['select', 'edit', 'blur', 'update-value', 'photo-click'])

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
