/**
 * PDF 報告生成工具
 * 使用 jsPDF 生成優化結果的 PDF 報告
 * 使用 Canvas 處理中文顯示問題
 */
import jsPDF from 'jspdf'

/**
 * 將文字轉換為 Canvas 圖片（解決中文顯示問題）
 */
function textToImage(text, fontSize = 12, fontColor = '#000000') {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  // 設定字體
  const fontFamily = '"Microsoft JhengHei", "Noto Sans TC", "PingFang TC", "Heiti TC", sans-serif'
  ctx.font = `${fontSize}px ${fontFamily}`
  ctx.fillStyle = fontColor
  ctx.textBaseline = 'top'
  
  // 測量文字寬度（考慮中文字符）
  const metrics = ctx.measureText(text)
  const padding = 20
  const width = Math.max(Math.ceil(metrics.width) + padding, text.length * fontSize * 0.6)
  const height = Math.ceil(fontSize * 1.5) + padding
  
  canvas.width = width
  canvas.height = height
  
  // 重新設定（canvas 尺寸改變後需要重新設定）
  ctx.font = `${fontSize}px ${fontFamily}`
  ctx.fillStyle = fontColor
  ctx.textBaseline = 'top'
  
  // 繪製文字
  ctx.fillText(text, padding / 2, padding / 2)
  
  return canvas.toDataURL('image/png')
}

/**
 * 在 PDF 中添加中文文字（使用 Canvas 轉換）
 */
function addChineseText(doc, text, x, y, options = {}) {
  const fontSize = options.fontSize || 12
  const fontColor = options.color || '#000000'
  const align = options.align || 'left'
  
  // 創建臨時 canvas 用於測量
  const measureCanvas = document.createElement('canvas')
  const measureCtx = measureCanvas.getContext('2d')
  const fontFamily = '"Microsoft JhengHei", "Noto Sans TC", "PingFang TC", "Heiti TC", sans-serif'
  measureCtx.font = `${fontSize}px ${fontFamily}`
  const textWidth = measureCtx.measureText(text).width
  
  // 計算對齊位置
  let actualX = x
  if (align === 'center') {
    // PDF 單位是 mm，需要將像素轉換為 mm (1mm ≈ 3.779527559px)
    const widthInMm = textWidth / 3.779527559
    actualX = x - widthInMm / 2
  } else if (align === 'right') {
    const widthInMm = textWidth / 3.779527559
    actualX = x - widthInMm
  }
  
  // 將文字轉換為圖片
  const imgData = textToImage(text, fontSize, fontColor)
  
  // 計算圖片尺寸（PDF 單位是 mm）
  // 像素轉 mm: 1mm = 3.779527559px
  const imgWidthMm = textWidth / 3.779527559 + 5 // 加上一些邊距
  const imgHeightMm = (fontSize * 1.5) / 3.779527559 + 5
  
  // 添加圖片到 PDF
  doc.addImage(imgData, 'PNG', actualX, y, imgWidthMm, imgHeightMm)
}

/**
 * 匯出優化結果為 PDF
 * @param {Object} result - 優化結果物件
 */
export async function exportToPDF(result) {
  const doc = new jsPDF()
  
  let yPos = 20
  
  // 標題（使用 Canvas 轉換）
  addChineseText(doc, '進度成本最佳化決策報告', 105, yPos, { 
    fontSize: 18, 
    align: 'center' 
  })
  yPos += 15
  
  // 結果摘要標題
  addChineseText(doc, '結果摘要', 20, yPos, { fontSize: 14 })
  yPos += 10
  
  // 結果摘要內容
  addChineseText(doc, `最優工期：${result.optimal_duration} 天`, 20, yPos, { fontSize: 12 })
  yPos += 7
  
  const optimalCost = formatCurrency(result.optimal_cost)
  addChineseText(doc, `最優成本：${optimalCost}`, 20, yPos, { fontSize: 12 })
  yPos += 7
  
  const penalty = formatCurrency(result.penalty_amount)
  addChineseText(doc, `違約金：${penalty}`, 20, yPos, { fontSize: 12 })
  yPos += 7
  
  const bonus = formatCurrency(result.bonus_amount)
  addChineseText(doc, `獎金：${bonus}`, 20, yPos, { fontSize: 12 })
  yPos += 7
  
  const totalCost = formatCurrency(result.total_cost)
  addChineseText(doc, `總成本（含獎懲）：${totalCost}`, 20, yPos, { 
    fontSize: 12,
    color: '#EF4444'
  })
  yPos += 15
  
  // 作業排程表
  if (result.schedules && result.schedules.length > 0) {
    addChineseText(doc, '作業排程明細', 20, yPos, { fontSize: 14 })
    yPos += 10
    
    // 表頭
    const tableHeaders = ['作業名稱', '開始', '結束', '工期', '趕工', '成本']
    const colWidths = [60, 20, 20, 20, 20, 40]
    let xPos = 20
    
    tableHeaders.forEach((header, index) => {
      addChineseText(doc, header, xPos, yPos, { fontSize: 10 })
      xPos += colWidths[index]
    })
    yPos += 10
    
    // 表格資料
    result.schedules.forEach((schedule) => {
      // 檢查是否需要換頁
      if (yPos > 270) {
        doc.addPage()
        yPos = 20
      }
      
      xPos = 20
      const rowData = [
        schedule.activity_name,
        schedule.start_time.toString(),
        schedule.end_time.toString(),
        schedule.duration.toString(),
        schedule.is_crashed ? '是' : '否',
        formatCurrency(schedule.cost)
      ]
      
      rowData.forEach((data, index) => {
        addChineseText(doc, String(data), xPos, yPos, { fontSize: 10 })
        xPos += colWidths[index]
      })
      yPos += 10
    })
  }
  
  // 儲存 PDF
  const fileName = `進度成本最佳化報告_${new Date().toISOString().split('T')[0]}.pdf`
  doc.save(fileName)
}

/**
 * 格式化貨幣
 */
function formatCurrency(value) {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(value)
}

