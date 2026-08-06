/**
 * PPTX / PDF 导出工具
 * 纯前端方案：html2canvas 截图 + pptxgenjs 生成 PPTX / jspdf 生成 PDF
 */

/**
 * 导出为 PPTX（每页一张全屏图片）
 * @param {object} project - 项目对象 { title, slides, settings }
 */
export async function exportPptx(project) {
  const PptxGenJS = (await import('pptxgenjs')).default
  const html2canvas = (await import('html2canvas')).default

  const pres = new PptxGenJS()
  pres.layout = 'LAYOUT_WIDE' // 16:9
  pres.title = project.title || '演示文稿'

  const slides = project.slides || []
  for (let i = 0; i < slides.length; i++) {
    const el = document.querySelector(`[data-slide-id="${slides[i].id}"] canvas`)
              || document.querySelector(`[data-slide-index="${i}"] canvas`)
    if (!el) continue

    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
    })

    const slide = pres.addSlide()
    slide.addImage({
      data: canvas.toDataURL('image/png'),
      x: 0, y: 0,
      w: pres.presLayout.width,
      h: pres.presLayout.height,
    })
  }

  const fileName = `${project.title || '演示文稿'}.pptx`
  await pres.writeFile({ fileName })
}

/**
 * 导出为 PDF（每页一张全屏图片，A4 横版）
 * @param {object} project - 项目对象 { title, slides, settings }
 */
export async function exportPdf(project) {
  const { jsPDF } = await import('jspdf')
  const html2canvas = (await import('html2canvas')).default

  // A4 横版尺寸 (mm)
  const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = pdf.internal.pageSize.getWidth()
  const pageH = pdf.internal.pageSize.getHeight()

  const slides = project.slides || []
  for (let i = 0; i < slides.length; i++) {
    const el = document.querySelector(`[data-slide-id="${slides[i].id}"] canvas`)
              || document.querySelector(`[data-slide-index="${i}"] canvas`)
    if (!el) continue

    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
    })

    if (i > 0) pdf.addPage()
    pdf.addImage(
      canvas.toDataURL('image/jpeg', 0.92),
      'JPEG',
      0, 0, pageW, pageH,
    )
  }

  const fileName = `${project.title || '演示文稿'}.pdf`
  pdf.save(fileName)
}
