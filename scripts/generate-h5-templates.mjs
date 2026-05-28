/**
 * 生成 H5 模板 JSON 到 backend/data/h5_templates/
 * 运行：node scripts/generate-h5-templates.mjs
 */
import { writeFileSync, mkdirSync } from 'fs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'
import {
  buildCorpIntroSlides,
  buildMinimalZjySlides,
  buildStoryVolunteerSlides,
  buildTechLaunchSlides,
  templateMeta,
} from '../frontend/src/constants/templateSeeds.js'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const outDir = join(root, 'backend', 'data', 'h5_templates')
mkdirSync(outDir, { recursive: true })

const templates = [
  templateMeta(
    'minimal-zjy-mobile',
    'ZJY 简约商务 · 移动端',
    '白底留白、青蓝点缀，9 页商务汇报结构，改字即可出片。',
    '简约商务',
    'mobile',
    'mobile-375',
    'zjy-minimal',
    buildMinimalZjySlides('mobile-375')
  ),
  templateMeta(
    'minimal-zjy-web',
    'ZJY 简约商务 · 网页版',
    '1280 宽屏商务汇报，适合投屏与网页嵌入。',
    '简约商务',
    'web',
    'web-1280',
    'zjy-minimal',
    buildMinimalZjySlides('web-1280')
  ),
  templateMeta(
    'story-volunteer-mobile',
    '志愿叙事 H5 · 移动端',
    '参照易企秀叙事结构，纵向滑动，10 页公益故事模板。',
    '叙事公益',
    'mobile',
    'mobile-375',
    'eqxiu-story',
    buildStoryVolunteerSlides('mobile-375')
  ),
  templateMeta(
    'story-volunteer-web',
    '志愿叙事 H5 · 网页版',
    '宽屏叙事模板，适合投屏展示志愿主题内容。',
    '叙事公益',
    'web',
    'web-1280',
    'eqxiu-story',
    buildStoryVolunteerSlides('web-1280')
  ),
  templateMeta(
    'tech-launch-mobile',
    '极简科技产品发布',
    '极简风格，突出产品核心卖点。',
    '产品发布',
    'mobile',
    'mobile-375',
    'zjy-minimal',
    buildTechLaunchSlides('mobile-375')
  ),
  templateMeta(
    'tech-launch-web',
    '极简科技产品发布（网页版）',
    '1280 宽屏布局，适合官网与发布会投屏。',
    '产品发布',
    'web',
    'web-1280',
    'zjy-minimal',
    buildTechLaunchSlides('web-1280')
  ),
  templateMeta(
    'corp-intro-mobile',
    '企业品牌介绍',
    '展示企业文化、业务与团队。',
    '企业介绍',
    'mobile',
    'mobile-375',
    'zjy-minimal',
    buildCorpIntroSlides('mobile-375')
  ),
  templateMeta(
    'corp-intro-web',
    '企业品牌介绍（网页版）',
    '企业官网风格宽屏介绍，适合 B 端展示。',
    '企业介绍',
    'web',
    'web-1280',
    'zjy-minimal',
    buildCorpIntroSlides('web-1280')
  ),
]

for (const t of templates) {
  const path = join(outDir, `${t.id}.json`)
  writeFileSync(path, JSON.stringify(t, null, 2), 'utf-8')
  console.log('wrote', path, `(${t.slides_json.length} slides)`)
}

console.log('done:', templates.length, 'templates')
