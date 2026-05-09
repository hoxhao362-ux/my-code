import { manuscriptApi } from '../utils/api'

/**
 * 导出稿件列表为 Excel（后端生成）
 * @param {Object} params - 导出参数
 * @param {string} params.status - 状态筛选
 * @param {string} params.date_from - 起始日期
 * @param {string} params.date_to - 结束日期
 * @param {string} params.subject - 学科筛选
 */
export async function exportManuscripts(params = {}) {
  try {
    const response = await manuscriptApi.exportManuscripts(params)
    
    // 创建 Blob 对象
    const blob = new Blob([response], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    
    // 生成文件名
    const dateStr = new Date().toISOString().slice(0, 10)
    const filename = `manuscripts_${dateStr}.xlsx`
    
    // 触发下载
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    return { success: true }
  } catch (error) {
    console.error('导出失败:', error)
    return { 
      success: false, 
      error: error.response?.data?.detail || error.message || '导出失败' 
    }
  }
}

/**
 * 导出操作日志为 Excel
 * TODO: 后端暂未实现日志导出接口，当前保留前端逻辑
 */
export function exportLogsToExcel(logs) {
  // TODO: 等待后端实现后替换为 API 调用
  console.warn('日志导出功能：后端接口尚未实现，当前为前端本地导出')
  // 可在此处添加 xlsx 本地导出逻辑作为 fallback
}

/**
 * 检查用户是否有导出权限
 * @param {string} userRole - 用户角色
 * @param {string} exportType - 导出类型
 * @returns {boolean}
 */
export function checkExportPermission(userRole, exportType) {
  if (exportType === 'manuscripts') {
    return ['admin', 'editor', 'associate_editor', 'ea_ae'].includes(userRole)
  }
  
  if (exportType === 'logs') {
    return userRole === 'admin'
  }
  
  return false
}
