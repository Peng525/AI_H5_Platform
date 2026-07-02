import { describe, expect, it } from 'vitest'
import { getBindValue, setBindValue, defaultStructured } from './resumeBind.js'

describe('resumeBind', () => {
  it('reads and writes basics.name', () => {
    let s = defaultStructured()
    s = setBindValue(s, 'basics.name', '王五')
    expect(getBindValue(s, 'basics.name')).toBe('王五')
  })

  it('reads honors index', () => {
    let s = defaultStructured()
    s = setBindValue(s, 'honors[0]', '国家奖学金')
    expect(getBindValue(s, 'honors[0]')).toBe('国家奖学金')
  })
})
