import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const existing=JSON.parse(readFileSync('products.json','utf8'));
const incoming=JSON.parse(readFileSync('incoming-products.json','utf8'));
assert(Array.isArray(existing),'products.json deve ser lista');
assert(Array.isArray(incoming),'incoming-products.json deve ser lista');
assert(existing.length>0,'O catálogo atual não pode estar vazio');
for(const p of existing) {
 assert.equal(typeof p.name,'string');
 assert.equal(typeof p.url,'string');
 assert.equal(typeof p.store,'string');
 assert(/^https:\/\//.test(p.url),'Link inválido: '+p.name);
}
console.log('Catálogo válido:',existing.length,'produtos;',incoming.length,'na fila');
