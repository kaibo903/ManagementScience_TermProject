/**
 * Excel 報告生成工具
 * 使用 xlsx 生成優化結果的 Excel 報告
 */
import * as XLSX from 'xlsx'

/**
 * 匯出優化結果為 Excel
 * @param {Object} result - 優化結果物件
 */
export async function exportToExcel(result) {
  // 建立工作簿
  const workbook = XLSX.utils.book_new()
  
  // 1. 結果摘要工作表
  const summaryData = [
    ['投標最佳化決策報告'],
    [''],
    ['結果摘要'],
    ['最優工期（天）', result.optimal_duration],
    ['最優成本', result.optimal_cost],
    ['違約金', result.penalty_amount],
    ['獎金', result.bonus_amount],
    ['總成本（含獎懲）', result.total_cost],
    [''],
    ['計算時間（秒）', result.calculation_time?.toFixed(3) || 'N/A'],
    ['建立時間', new Date(result.created_at).toLocaleString('zh-TW')]
  ]
  
  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
  
  // 設定欄寬
  summarySheet['!cols'] = [
    { wch: 20 },
    { wch: 20 }
  ]
  
  XLSX.utils.book_append_sheet(workbook, summarySheet, '結果摘要')
  
  // 2. 作業排程工作表
  if (result.schedules && result.schedules.length > 0) {
    const scheduleHeaders = ['作業名稱', '開始時間（天）', '結束時間（天）', '工期（天）', '是否趕工', '成本']
    const scheduleData = [
      scheduleHeaders,
      ...result.schedules.map(schedule => [
        schedule.activity_name,
        schedule.start_time,
        schedule.end_time,
        schedule.duration,
        schedule.is_crashed ? '是' : '否',
        schedule.cost
      ])
    ]
    
    const scheduleSheet = XLSX.utils.aoa_to_sheet(scheduleData)
    
    // 設定欄寬
    scheduleSheet['!cols'] = [
      { wch: 30 },
      { wch: 15 },
      { wch: 15 },
      { wch: 12 },
      { wch: 12 },
      { wch: 15 }
    ]
    
    // 設定表頭樣式（粗體）
    const headerRange = XLSX.utils.decode_range(scheduleSheet['!ref'])
    for (let col = headerRange.s.c; col <= headerRange.e.c; col++) {
      const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
      if (!scheduleSheet[cellAddress]) continue
      scheduleSheet[cellAddress].s = {
        font: { bold: true },
        alignment: { horizontal: 'center' }
      }
    }
    
    XLSX.utils.book_append_sheet(workbook, scheduleSheet, '作業排程')
  }
  
  // 儲存 Excel 檔案
  const fileName = `投標優化報告_${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(workbook, fileName)
}

