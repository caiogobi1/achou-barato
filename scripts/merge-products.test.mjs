import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

test('importa somente links de afiliados aprovados e evita duplicatas', () => {
 const dir=mkdtempSync(join(tmpdir(),'buscoubarato-'));
 try {
  const old={name:'Produto existente',url:'https://meli.la/abc123',store:'Mercado Livre',affiliate:true,price:'R$ 10'};
  const incoming=[
   {...old,price:'R$ 9'},
   {name:'Novo aprovado',url:'https://meli.la/novo456',store:'Mercado Livre',affiliate:true},
   {name:'Sem confirmação',url:'https://meli.la/sem789',store:'Mercado Livre',affiliate:false},
   {name:'Site externo',url:'https://exemplo.com/item',store:'Mercado Livre',affiliate:true}
  ];
  writeFileSync(join(dir,'products.json'),JSON.stringify([old]));
  writeFileSync(join(dir,'incoming-products.json'),JSON.stringify(incoming));
  const run=spawnSync(process.execPath,[resolve('scripts/merge-products.mjs')],{cwd:dir,encoding:'utf8'});
  assert.equal(run.status,0,run.stderr);
  const result=JSON.parse(readFileSync(join(dir,'products.json'),'utf8'));
  assert.equal(result.length,2);
  assert.equal(result[0].price,'R$ 9');
  assert.equal(result[1].name,'Novo aprovado');
 } finally {rmSync(dir,{recursive:true,force:true})}
});
