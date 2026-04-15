const fs = require('fs');
const path = require('path');

const directories = [
  'e:/node/journal-platform/frontend/src'
];

const replacements = [
  { regex: /\bdeputy_editor\b/g, replacement: 'associate_editor' },
  { regex: /Deputy Editor/g, replacement: 'Associate Editor' },
  { regex: /副编辑/g, replacement: '副主编' }
];

function processDirectory(dir) {
  if (!fs.existsSync(dir)) return;
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      if (file !== 'node_modules' && file !== 'dist' && file !== '.git' && file !== '__pycache__' && file !== 'venv') {
        processDirectory(fullPath);
      }
    } else if (stat.isFile()) {
      const ext = path.extname(file);
      if (['.js', '.vue', '.html'].includes(ext)) {
        let content = fs.readFileSync(fullPath, 'utf8');
        let originalContent = content;
        
        for (const { regex, replacement } of replacements) {
          content = content.replace(regex, replacement);
        }
        
        if (content !== originalContent) {
          fs.writeFileSync(fullPath, content, 'utf8');
          console.log(`Updated ${fullPath}`);
        }
      }
    }
  }
}

for (const dir of directories) {
  processDirectory(dir);
}
console.log('Done.');