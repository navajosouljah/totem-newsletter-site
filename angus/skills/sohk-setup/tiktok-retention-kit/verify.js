import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'SOURCE-MANIFEST.json'),'utf8'));
for(const entry of manifest.files){
  const file=path.resolve(root,entry.path);
  if(!file.startsWith(root+path.sep))throw new Error('Invalid manifest path');
  const bytes=fs.readFileSync(file);
  if(bytes.length!==entry.bytes || createHash('sha256').update(bytes).digest('hex')!==entry.sha256)throw new Error('Checksum mismatch: '+entry.path);
}
console.log('Verified '+manifest.files.length+' supplied files.');
