import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const app=readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../public/index.html',import.meta.url),'utf8');

test('Só a seção Já convocados do Portal do Supervisor recebe o destaque amarelo',()=>{
  const label='<details class="card card-pad section convocados-destaque"><summary>Já convocados · ${total}</summary>';
  assert.ok(app.includes(label),'A classe de destaque deve estar no painel Já convocados');
  assert.equal((app.match(/convocados-destaque/g)||[]).length,1,'Não destacar outros blocos por acidente');
  assert.match(html,/details\.convocados-destaque\s*\{[^}]*background:#fff3bf;[^}]*border:1px solid #e6b84c;/);
  assert.match(html,/details\.convocados-destaque\s*>\s*summary\s*\{[^}]*color:#835307;/);
  assert.match(html,/app\.js\?v=aproar-whatsapp-sem-servico-20261016-1/);
});
