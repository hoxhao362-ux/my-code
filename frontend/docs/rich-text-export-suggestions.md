# 富文本导出功能建议

## 当前问题分析

目前系统的PDF导出功能仅支持纯文本导出，无法保留富文本格式（如粗体、斜体、标题、列表等）。这是因为当前实现中使用了简单的HTML标签过滤，将所有标签移除后只保留纯文本内容。

## 解决方案建议

### 1. 使用 html2pdf.js 库（推荐）

**优势**：
- 基于 jsPDF 和 html2canvas，易于集成
- 支持完整的HTML/CSS渲染，保留富文本格式
- 自动处理页面分页
- 支持中文和特殊字符
- 无需服务器支持，纯客户端实现

**实现步骤**：

1. **安装依赖**：
   ```bash
   npm install html2pdf.js
   ```

2. **修改导出函数**：
   ```javascript
   // 导入库
   import html2pdf from 'html2pdf.js';
   
   // 导出期刊内容为PDF（支持富文本）
   export function exportJournalToPDF(journal) {
     // 创建临时DOM元素
     const tempDiv = document.createElement('div');
     tempDiv.style.position = 'absolute';
     tempDiv.style.left = '-9999px';
     tempDiv.style.width = '210mm';
     tempDiv.style.padding = '20mm';
     tempDiv.style.boxSizing = 'border-box';
     
     // 构建HTML内容
     tempDiv.innerHTML = `
       <div class="pdf-content">
         <h1>${journal.title || 'Untitled Journal'}</h1>
         <div class="pdf-meta">
           <p><strong>Journal ID:</strong> ${journal.id || 'Unknown'}</p>
           <p><strong>Author:</strong> ${journal.author || 'Unknown'}</p>
           <p><strong>Submission Date:</strong> ${journal.date || 'Unknown'}</p>
         </div>
         
         <h2>Abstract</h2>
         <div class="pdf-abstract">${journal.abstract || 'No abstract available'}</div>
         
         <h2>Keywords</h2>
         <div class="pdf-keywords">${Array.isArray(journal.keywords) ? journal.keywords.join(', ') : journal.keywords || 'No keywords'}</div>
         
         <h2>Content</h2>
         <div class="pdf-body">${journal.content || 'No content available'}</div>
       </div>
     `;
     
     // 添加到文档
     document.body.appendChild(tempDiv);
     
     // 配置导出选项
     const options = {
       margin: 10,
       filename: `${journal.title || 'journal'}.pdf`,
       image: { type: 'jpeg', quality: 0.98 },
       html2canvas: { scale: 2 },
       jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
     };
     
     // 执行导出
     html2pdf().set(options).from(tempDiv).save();
     
     // 清理临时元素
     setTimeout(() => {
       document.body.removeChild(tempDiv);
     }, 100);
   }
   ```

### 2. 使用 jsPDF 的 HTML 插件

**优势**：
- 基于现有jsPDF库，无需额外依赖
- 支持基本HTML渲染

**实现步骤**：

1. **安装HTML插件**：
   ```bash
   npm install jspdf-html2canvas
   ```

2. **修改导出函数**：
   ```javascript
   import { jsPDF } from 'jspdf';
   import html2canvas from 'html2canvas';
   
   export async function exportJournalToPDF(journal) {
     // 创建临时DOM元素
     const tempDiv = document.createElement('div');
     // 构建HTML内容...
     
     // 使用html2canvas将HTML转换为图片
     const canvas = await html2canvas(tempDiv);
     const imgData = canvas.toDataURL('image/png');
     
     // 创建PDF并添加图片
     const doc = new jsPDF('p', 'mm', 'a4');
     const imgProps = doc.getImageProperties(imgData);
     const pdfWidth = doc.internal.pageSize.getWidth();
     const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
     
     doc.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
     doc.save(`${journal.title || 'journal'}.pdf`);
     
     // 清理临时元素
     document.body.removeChild(tempDiv);
   }
   ```

### 3. 手动解析HTML标签（复杂但灵活）

**优势**：
- 完全控制PDF生成过程
- 可定制性高

**实现步骤**：

1. **解析HTML标签**：
   ```javascript
   // 示例：解析粗体标签
   function applyRichText(doc, text, x, y) {
     let currentX = x;
     let currentY = y;
     
     // 简单的HTML解析（仅示例）
     const parts = text.split(/(<\/?\w+>)/g);
     let isBold = false;
     let isItalic = false;
     
     for (const part of parts) {
       if (part === '<b>' || part === '<strong>') {
         isBold = true;
         doc.setFont('helvetica', 'bold');
       } else if (part === '</b>' || part === '</strong>') {
         isBold = false;
         doc.setFont('helvetica', isItalic ? 'italic' : 'normal');
       } else if (part === '<i>' || part === '<em>') {
         isItalic = true;
         doc.setFont('helvetica', isBold ? 'bolditalic' : 'italic');
       } else if (part === '</i>' || part === '</em>') {
         isItalic = false;
         doc.setFont('helvetica', isBold ? 'bold' : 'normal');
       } else if (part.trim()) {
         // 绘制文本
         const splitText = doc.splitTextToSize(part, 180);
         doc.text(splitText, currentX, currentY);
         currentY += splitText.length * 8;
       }
     }
     
     return currentY;
   }
   ```

2. **在导出函数中使用**：
   ```javascript
   // 使用applyRichText函数替代简单的text函数
   // doc.text(abstractLines, 14, yPosition);
   yPosition = applyRichText(doc, journal.abstract, 14, yPosition);
   ```

## 其他导出格式建议

### 1. Word 文档导出

**使用 mammoth.js 库**：
- 支持将HTML转换为Word文档
- 保留富文本格式
- 易于集成

### 2. 富文本编辑器原生格式导出

**优势**：
- 直接使用富文本编辑器的导出功能
- 格式保留完整

**实现**：
- 检查当前使用的Quill编辑器是否支持导出功能
- 配置编辑器支持Word、PDF等格式导出

## 集成建议

1. **逐步升级**：
   - 先实现PDF富文本导出
   - 再考虑其他格式
   - 保持现有纯文本导出作为备选

2. **用户体验优化**：
   - 添加导出格式选择
   - 显示导出进度
   - 提供导出成功提示

3. **性能考虑**：
   - 大文档导出时添加加载提示
   - 考虑使用Web Worker处理复杂导出
   - 优化HTML结构，提高渲染速度

## 总结

推荐使用 **html2pdf.js** 库实现富文本PDF导出，它是目前最成熟、易用的前端HTML到PDF解决方案。该方案可以快速集成，并且能很好地保留富文本格式，提升用户体验。

如需进一步定制或支持更多格式，可以考虑结合其他库或服务，构建更完善的富文本导出系统。