// 过滤HTML标签，只保留纯文本内容
export const stripHtmlTags = (html) => {
  if (!html || typeof html !== 'string') {
    return html
  }
  // 创建临时DOM元素，利用浏览器解析HTML并提取纯文本
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  return tempDiv.textContent || tempDiv.innerText || ''
}

// 截断纯文本，添加省略号
export const truncateText = (text, maxLength = 150) => {
  if (!text || typeof text !== 'string') {
    return text
  }
  if (text.length <= maxLength) {
    return text
  }
  return text.slice(0, maxLength) + '...'
}

// 截断HTML文本，保留标签完整性
export const truncateHtml = (html, maxLength = 150) => {
  if (!html || typeof html !== 'string') {
    return html
  }
  
  // 先获取纯文本长度
  const plainText = stripHtmlTags(html)
  if (plainText.length <= maxLength) {
    return html
  }
  
  // 创建临时DOM元素
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  
  let currentLength = 0
  let result = ''
  
  // 遍历所有子节点
  const processNode = (node) => {
    if (currentLength >= maxLength) return
    
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent
      if (currentLength + text.length <= maxLength) {
        result += text
        currentLength += text.length
      } else {
        result += text.slice(0, maxLength - currentLength) + '...'
        currentLength = maxLength
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const tagName = node.tagName.toLowerCase()
      result += `<${tagName}>`
      
      // 处理子节点
      for (const child of node.childNodes) {
        processNode(child)
        if (currentLength >= maxLength) break
      }
      
      result += `</${tagName}>`
    }
  }
  
  // 处理所有根节点
  for (const child of tempDiv.childNodes) {
    processNode(child)
    if (currentLength >= maxLength) break
  }
  
  return result
}

// 在文本中插入换行符，确保每行不超过指定长度
export const wrapText = (text, lineLength = 30) => {
  if (!text || typeof text !== 'string') {
    return text
  }
  if (text.length <= lineLength) {
    return text
  }
  
  let result = ''
  let currentLine = ''
  
  for (let i = 0; i < text.length; i++) {
    currentLine += text[i]
    
    if (currentLine.length >= lineLength) {
      result += currentLine + '\n'
      currentLine = ''
    }
  }
  
  if (currentLine) {
    result += currentLine
  }
  
  return result
}