import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('  function unidadesSemServicoConfirmadas(');
const end=app.indexOf('  function renderWhatsApp(){',start);
assert(start>=0&&end>start,'Painel de unidades sem serviço não encontrado');
const panel=app.slice(start,end);
const ctx={
 state:{semConvocacoesUnidade:[
  {supervisor:'EDUARDO',unidade:'BARRA DO CEARÁ',dataServico:'2026-10-17'},
  {supervisor:'JOEL',unidade:'FIEC',dataServico:'2026-10-17'},
  {supervisor:'NETO',unidade:'MARACANAÚ',dataServico:'2026-10-16'},
  {supervisor:'MALICIOUS',unidade:'<script>alert(1)</script>',dataServico:'2026-10-17'}
 ]},
 clean:v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase(),
 unitTitle:v=>String(v).split(' ').map(x=>x.charAt(0).toUpperCase()+x.slice(1).toLowerCase()).join(' '),
 formatDate:v=>v.split('-').reverse().join('/'),
 escapeHtml:v=>String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')
};
ctx.globalThis=ctx;
vm.createContext(ctx);
vm.runInContext(panel+'\nglobalThis.buildPanel=painelWhatsAppSemServico;',ctx);

test('WhatsApp lists only supervisor-confirmed no-service units for selected date',()=>{
 const html=ctx.buildPanel('2026-10-17');
 assert.match(html,/Unidades que não funcionarão · 3/);
 assert.match(html,/Barra Do Ceará/);
 assert.match(html,/sinalizado por <strong>EDUARDO<\/strong>/);
 assert.match(html,/Fiec/);
 assert.match(html,/JOEL/);
 assert.doesNotMatch(html,/MARACANAÚ|NETO/);
 assert.match(html,/17\/10\/2026/);
 assert(!html.includes('<script>'),'Untrusted unit names must be escaped');
 assert(html.includes('&lt;script&gt;'));
});

test('WhatsApp no-service panel updates with date and shows an empty state',()=>{
 const html=ctx.buildPanel('2026-10-18');
 assert.match(html,/Unidades que não funcionarão · 0/);
 assert.match(html,/Nenhuma unidade foi sinalizada sem serviço nesta data/);
 const whatsApp=app.slice(app.indexOf('  function renderWhatsApp(){'),app.indexOf('  let indicatorUnit=',app.indexOf('  function renderWhatsApp(){')));
 assert.match(whatsApp,/id="wp-no-service"/);
 assert.match(whatsApp,/\$\('#wp-no-service'\)\.innerHTML=painelWhatsAppSemServico\(date\)/);
 assert.match(whatsApp,/\['wp-data','wp-func','wp-pend'\]\.forEach/);
 assert.ok(whatsApp.indexOf('id="wp-no-service"')>whatsApp.indexOf('id="wp-units"'));
});
