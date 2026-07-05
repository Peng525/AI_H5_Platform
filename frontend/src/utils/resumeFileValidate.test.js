import { describe, expect, it } from 'vitest'
import { formatResumeFileLabel, validateResumeFile, RESUME_FILE_MAX_BYTES } from './resumeFileValidate.js'

describe('resumeFileValidate', () => {
  it('rejects files over 5MB', () => {
    const file = { size: RESUME_FILE_MAX_BYTES + 1, name: 'big.pdf' }
    expect(validateResumeFile(file)).toEqual({ ok: false, error: '文件超过 5MB 限制' })
  })

  it('accepts valid files', () => {
    const file = { size: 1024, name: 'resume.pdf' }
    expect(validateResumeFile(file)).toEqual({ ok: true, file })
  })

  it('maps file extensions to labels', () => {
    expect(formatResumeFileLabel('a.pdf')).toBe('PDF')
    expect(formatResumeFileLabel('b.png')).toBe('PNG')
    expect(formatResumeFileLabel('c.docx')).toBe('DOC')
  })
})
