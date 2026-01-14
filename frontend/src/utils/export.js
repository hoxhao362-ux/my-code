import * as XLSX from 'xlsx';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

// 导出Excel文件
export function exportToExcel(data, filename, sheetName = 'Sheet1') {
  // 创建工作簿
  const wb = XLSX.utils.book_new();
  // 将数据转换为工作表
  const ws = XLSX.utils.json_to_sheet(data);
  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, sheetName);
  // 导出文件 - 浏览器会自动弹出保存对话框
  XLSX.writeFile(wb, `${filename}.xlsx`);
}

// 导出PDF文件
export function exportToPDF(title, content, metadata = {}) {
  // 创建PDF文档
  const doc = new jsPDF();
  
  // 设置标题
  doc.setFontSize(18);
  doc.text(title, 14, 22);
  
  // 设置元数据
  let yPosition = 35;
  if (metadata) {
    doc.setFontSize(12);
    doc.setTextColor(100);
    Object.entries(metadata).forEach(([key, value]) => {
      doc.text(`${key}: ${value}`, 14, yPosition);
      yPosition += 10;
    });
    doc.setTextColor(0);
    yPosition += 5;
  }
  
  // 设置内容
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  
  // 处理长文本，自动换行
  const splitText = doc.splitTextToSize(content, 180);
  doc.text(splitText, 14, yPosition);
  
  // 导出文件 - 浏览器会自动弹出保存对话框
  doc.save(`${title}.pdf`);
}

// 导出期刊内容为PDF
export function exportJournalToPDF(journal) {
  // 准备元数据
  const metadata = {
    '期刊ID': journal.id,
    '作者': journal.author || '未知',
    '提交日期': journal.submitDate || '未知',
    '状态': journal.status || '未知',
  };
  
  // 调用PDF导出函数
  exportToPDF(journal.title, journal.content, metadata);
}

// 导出操作日志为Excel
export function exportLogsToExcel(logs) {
  // 格式化日志数据
  const formattedLogs = logs.map(log => ({
    'ID': log.id,
    '用户': log.user,
    '操作类型': log.type,
    '操作内容': log.action,
    '目标': log.target,
    '时间': log.time,
    'IP地址': log.ip,
    '状态': log.status,
  }));
  
  // 调用Excel导出函数
  exportToExcel(formattedLogs, `操作日志_${new Date().toISOString().slice(0, 10)}`);
}

// 检查用户是否有导出权限
export function checkExportPermission(userRole, exportType, journal, currentUserId) {
  // 导出类型：journal（期刊）、logs（日志）
  if (exportType === 'journal') {
    // 普通用户：无导出权限
    if (!userRole || userRole === 'user') {
      return false;
    }
    
    // 作者：仅可导出自己投稿的期刊
    if (userRole === 'author') {
      return journal && journal.authorId === currentUserId;
    }
    
    // 审核员：可导出所有期刊
    if (userRole === 'reviewer') {
      return true;
    }
    
    // 管理员：可导出所有期刊
    if (userRole === 'admin') {
      return true;
    }
  }
  
  if (exportType === 'logs') {
    // 仅管理员可导出操作日志
    return userRole === 'admin';
  }
  
  return false;
}