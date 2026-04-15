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
  
  // 确保内容不为空
  let safeContent = content || '暂无内容';
  
  // 移除HTML标签，只保留纯文本
  safeContent = safeContent.replace(/<[^>]*>/g, '');
  
  // 确保标题不含特殊字符，用于文件名
  const safeFilename = title.replace(/[^a-zA-Z0-9一-龥_-]/g, '') || 'journal';
  
  // 处理长文本，自动换行 - 使用jsPDF内置的自动换行机制
  const splitText = doc.splitTextToSize(safeContent, 180);
  doc.text(splitText, 14, yPosition);
  
  // 导出文件 - 使用blob方式确保浏览器能正确处理中文文件名和触发保存对话框
  const blob = doc.output('blob');
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${safeFilename}.pdf`;
  document.body.appendChild(link);
  link.click();
  // 清理创建的元素和URL
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// 直接使用jsPDF和html2canvas，不使用html2pdf.js封装
import html2canvas from 'html2canvas';

// 导出期刊内容为PDF（支持富文本）
export async function exportJournalToPDF(journal) {
  if (!journal) {
    return { success: false, error: '期刊数据无效，无法导出PDF' };
  }
  
  try {
    // 创建一个可见的临时元素，用于渲染
    const tempContainer = document.createElement('div');
    tempContainer.style.position = 'fixed';
    tempContainer.style.top = '0';
    tempContainer.style.left = '0';
    tempContainer.style.width = '800px'; // 固定宽度，确保内容完整
    tempContainer.style.height = 'auto';
    tempContainer.style.background = 'white';
    tempContainer.style.color = 'black';
    tempContainer.style.padding = '20px';
    tempContainer.style.zIndex = '-1'; // 放在最底层，不影响用户操作
    tempContainer.style.opacity = '0.99'; // 接近透明但可渲染
    tempContainer.style.boxShadow = 'none';
    
    // 设置HTML内容
    tempContainer.innerHTML = `
      <div id="pdf-content" style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h1 style="text-align: center; font-size: 24px; margin-bottom: 20px;">${journal.title || 'Untitled Journal'}</h1>
        
        <div style="background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
          <p><strong>Journal ID:</strong> ${journal.id || 'Unknown'}</p>
          <p><strong>Author:</strong> ${journal.author || 'Unknown'}</p>
          <p><strong>Date:</strong> ${journal.date || 'Unknown'}</p>
          <p><strong>Status:</strong> ${journal.status || 'Unknown'}</p>
        </div>
        
        <h2 style="font-size: 18px; margin: 20px 0 10px 0; color: #333;">Abstract</h2>
        <div style="margin: 10px 0;">${journal.abstract || 'No abstract available'}</div>
        
        <h2 style="font-size: 18px; margin: 20px 0 10px 0; color: #333;">Keywords</h2>
        <div style="color: #0066cc; margin: 10px 0;">${Array.isArray(journal.keywords) ? journal.keywords.join(', ') : journal.keywords || 'No keywords'}</div>
        
        <h2 style="font-size: 18px; margin: 20px 0 10px 0; color: #333;">Content</h2>
        <div style="margin: 10px 0;">${journal.content || 'No content available'}</div>
      </div>
    `;
    
    // 添加到文档
    document.body.appendChild(tempContainer);
    
    // 等待DOM渲染完成
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 获取要导出的元素
    const element = tempContainer.querySelector('#pdf-content');
    
    // 使用html2canvas捕获元素
    const canvas = await html2canvas(element, {
      scale: 2, // 提高清晰度
      backgroundColor: '#ffffff',
      useCORS: true,
      logging: false
    });
    
    // 将canvas转换为图片数据
    const imgData = canvas.toDataURL('image/png');
    
    // 创建PDF文档
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    // 计算PDF尺寸和图片尺寸
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = canvas.width;
    const imgHeight = canvas.height;
    const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
    const imgX = (pdfWidth - imgWidth * ratio) / 2;
    const imgY = 10;
    
    // 添加图片到PDF
    pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
    
    // 保存PDF
    pdf.save(`${journal.title || 'journal'}.pdf`);
    
    setTimeout(() => {
      document.body.removeChild(tempContainer);
    }, 500);
    
    return { success: true };
  } catch (error) {
    console.error('PDF导出错误:', error);
    const tempElements = document.querySelectorAll('div[style*="z-index: -1"]');
    tempElements.forEach(el => el.remove());
    return { success: false, error: 'PDF导出失败: ' + error.message };
  }
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