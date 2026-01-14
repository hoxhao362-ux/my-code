import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, resolve } from 'node:path';
import { existsSync } from 'node:fs';

const PORT = 3001;
const PUBLIC_DIR = join(process.cwd(), 'public');
const DIST_DIR = join(process.cwd(), 'dist');

// 检查dist目录是否存在，如果不存在则使用public目录
const STATIC_DIR = existsSync(DIST_DIR) ? DIST_DIR : PUBLIC_DIR;

// MIME类型映射
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = createServer(async (req, res) => {
  console.log(`${req.method} ${req.url}`);
  
  // 处理根路径
  let filePath = join(STATIC_DIR, req.url === '/' ? 'index.html' : req.url);
  
  // 处理路径扩展名
  const fileExtname = extname(filePath);
  const contentType = mimeTypes[fileExtname] || 'text/html';
  
  try {
    // 读取文件
    const content = await readFile(filePath);
    // 文件存在，返回文件内容
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  } catch (err) {
    if (err.code === 'ENOENT') {
      // 文件不存在，返回404
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>');
    } else {
      // 服务器错误
      res.writeHead(500);
      res.end(`Server Error: ${err.code}`);
    }
  }
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log(`Serving files from ${STATIC_DIR}`);
});

console.log('Starting simple HTTP server...');