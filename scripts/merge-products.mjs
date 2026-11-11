import { readFileSync, writeFileSync } from 'node:fs';
const current=JSON.parse(readFileSync('products.json','utf8'));
const incoming=JSON.parse(readFileSync('incoming-products.json','utf8'));
if(!Array.isArray(current)||!Array.isArray(incoming))throw Error('Os catálogos devem ser listas');
const map=new Map();
for(const p of current){if(p?.url)map.set(p.url,p)}
let added=0,updated=0,skipped=0;
for(const p of incoming){
 if(!p||typeof p.name!=='string'||typeof p.url!=='string'||!/^https:\/\//i.test(p.url)||!p.store){skipped++;continue}
 const host=new URL(p.url).hostname.toLowerCase();
 if(!['meli.la','mercadolivre.com.br','www.mercadolivre.com.br','produto.mercadolivre.com.br'].includes(host)){skipped++;continue}
 if(p.affiliate!==true){skipped++;continue}
 const prior=map.get(p.url);
 const next={...prior,...p,source:p.source||prior?.source||'recomendacoes'};
 if(prior){map.set(p.url,next);updated++}else{map.set(p.url,next);added++}
}
const out=[...map.values()];
if(out.length>5000)throw Error('Limite de segurança de 5000 produtos');
writeFileSync('products.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({added,updated,skipped,total:out.length}));
