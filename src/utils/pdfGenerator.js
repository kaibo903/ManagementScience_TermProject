/**
 * PDF 報告生成工具
 * 使用 jsPDF 生成優化結果的 PDF 報告
 */
import jsPDF from 'jspdf'

/**
 * 匯出優化結果為 PDF
 * @param {Object} result - 優化結果物件
 */
export async function exportToPDF(result) {
  const doc = new jsPDF()
  
  // 設定字體（jsPDF 預設不支援中文，需要額外設定）
  // 這裡使用簡化版本，實際使用時可能需要引入中文字體
  doc.setFont('helvetica')
  
  let yPos = 20
  
  // 標題
  doc.setFontSize(18)
  doc.text('投標最佳化決策報告', 105, yPos, { align: 'center' })
  yPos += 15
  
  // 結果摘要
  doc.setFontSize(14)
  doc.text('結果摘要', 20, yPos)
  yPos += 10
  
  doc.setFontSize(12)
  doc.text(`最優工期：${result.optimal_duration} 天`, 20, yPos)
  yPos += 7
  doc.text(`最優成本：${formatCurrency(result.optimal_cost)}`, 20, yPos)
  yPos += 7
  doc.text(`違約金：${formatCurrency(result.penalty_amount)}`, 20, yPos)
  yPos += 7
  doc.text(`獎金：${formatCurrency(result.bonus_amount)}`, 20, yPos)
  yPos += 7
  doc.text(`總成本（含獎懲）：${formatCurrency(result.total_cost)}`, 20, yPos)
  yPos += 10
  
  // 作業排程表
  if (result.schedules && result.schedules.length > 0) {
    doc.setFontSize(14)
    doc.text('作業排程明細', 20, yPos)
    yPos += 10
    
    // 表頭
    doc.setFontSize(10)
    const tableHeaders = ['作業名稱', '開始', '結束', '工期', '趕工', '成本']
    const colWidths = [60, 20, 20, 20, 20, 40]
    let xPos = 20
    
    tableHeaders.forEach((header, index) => {
      doc.text(header, xPos, yPos)
      xPos += colWidths[index]
    })
    yPos += 7
    
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
        doc.text(String(data), xPos, yPos)
        xPos += colWidths[index]
      })
      yPos += 7
    })
  }
  
  // 儲存 PDF
  const fileName = `投標優化報告_${new Date().toISOString().split('T')[0]}.pdf`
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

