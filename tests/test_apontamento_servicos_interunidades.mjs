import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
import vm from 'node:vm';

const source = readFileSync(new URL('../cloudflare-production/public/app.js', import.meta.url), 'utf8');
const works = [
  { id: '1', nome: '2100 - Escritório', unidade: 'ESCRITORIO' },
  { id: '2', nome: '2139 - FIEC', unidade: 'FIEC' },
  { id: '3', nome: '2150 - Centro', unidade: 'CENTRO' },
  { id: '4', nome: '2139 - FIEC', unidade: 'CENTRO' }
];
const ctx = vm.createContext({
  OBRAS: works,
  escapeHtml: value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('"', '&quot;'),
  field: (_label, markup) => markup,
  clean: v => String(v ?? '').toLocaleLowerCase('pt-BR').trim(),
  presence: status => status.startsWith('Presente'),
  obraById: id => works.find(w => String(w.id) === String(id)),
  toast: () => {},
  document: {}
});
function extract(start, end) {
  const a = source.indexOf(start);
  const b = source.indexOf(end, a + start.length);
  assert(a >= 0 && b > a, 'função não encontrada: ' + start);
  return source.slice(a, b);
}
vm.runInContext(extract('  let serviceListSeq=0;', '  function itemServices('), ctx);
vm.runInContext(extract('  function readPersonRows(', '  function applyInlineExtras('), ctx);
vm.runInContext(extract('  function validServices(', '  function renderApontamentoRetroativo('), ctx);
vm.runInContext(extract('  function splitMoneyExactly(', '  function entries('), ctx);

const principal = ctx.allocationRow('ESCRITORIO', { obraId: '1', periodo: 'Integral' }, 0);
assert(principal.includes('2100 - Escritório'));
assert(!principal.includes('2139 - FIEC'), 'obra principal deve continuar restrita à unidade');
const adicional = ctx.allocationRow('ESCRITORIO', { obraId: '2', periodo: 'Integral' }, 1);
assert(adicional.includes('2139 - FIEC'));
assert(adicional.includes('FIEC · 2139 - FIEC'));
assert(adicional.includes('CENTRO · 2139 - FIEC'));
assert(adicional.includes('data-work-id="2"'), 'obra adicional deve conservar o ID real');

const services = [
  ['1', '2100 - Escritório', false],
  ['2', 'FIEC · 2139 - FIEC', true],
  ['3', 'CENTRO · 2150 - Centro', true]
];
const serviceRows = services.map(([id, label, isAdditional]) => ({
  closest: selector => selector === '.additional-services' ? (isAdditional ? {} : null) : null,
  querySelector: selector => selector === '.service-work'
    ? { dataset: { workId: id }, value: label }
    : selector === '.service-period' ? { value: 'Integral' } : null
}));
const card = {
  dataset: { unit: 'ESCRITORIO', financeAdjusted: 'false', financeiroOriginal: '0', ajudaCusto: '0' },
  querySelectorAll: selector => selector === '.allocation-row' ? serviceRows : [],
  querySelector: selector => ({
    '.row-status': { value: 'Presente (Integral)' },
    '.row-extra': { value: 'Não' },
    '.row-extra-value': { value: '0' },
    '.row-extra-work': { value: '' },
    '.row-extra-obs': { value: '' },
    '.row-obs': { value: '' },
    '.row-financeiro': { value: '0' },
    '.row-noturno': { value: '0' },
    '.row-acordo': { value: '0' },
    '.row-ajuda-custo': { value: '0' }
  })[selector] || null
};
const scope = { querySelector: selector => selector === '[data-person="fabiano"]' ? card : null };
const [item] = ctx.readPersonRows(['fabiano'], scope);
assert.deepEqual(Array.from(item.servicos, x => x.obraId), ['1', '2', '3']);
assert.equal(ctx.validServices([item], 'ESCRITORIO'), true);
assert.equal(ctx.validServices([{ ...item, servicos: [{ obraId: '2', periodo: 'Integral' }] }], 'ESCRITORIO'), false);
assert.equal(ctx.validServices([{ ...item, servicos: [{ obraId: '1', periodo: 'Integral' }, { obraId: '999', periodo: 'Integral' }] }], 'ESCRITORIO'), false);
assert(source.includes("const additional=Boolean(input.closest('.additional-services'));"));
assert(source.includes("$$('.person-card .service-work').forEach(bindServiceWork);"));
assert(source.includes("bindServiceWork(added);"));
assert.deepEqual(Array.from(ctx.splitMoneyExactly(125,3)),[41.67,41.67,41.66]);
assert.deepEqual(Array.from(ctx.splitMoneyExactly(11,3)),[3.67,3.67,3.66]);
assert.equal(ctx.splitMoneyExactly(125,3).reduce((a,b)=>a+b,0),125);
assert(source.includes("if(regs.length===1&&services.size>1)"), 'rateio de um apontamento deve dividir pelo total de obras');
assert(source.includes("const expectedPoints=items.map("), 'apontamento normal deve capturar vínculos esperados');
assert(source.includes("},verifyDayServices))return;"), 'salvar deve verificar os vínculos após o POST');
assert(source.includes("typeof verifyPersisted==='function'"), 'verificação deve consultar o estado confirmado');
const worker = readFileSync(new URL('../cloudflare-production/worker.js', import.meta.url), 'utf8');
assert(worker.includes('const samePersistedServices = previousServices.length === ss.length'));
assert(worker.includes('|| !samePersistedServices'), 'worker deve corrigir vínculos faltantes mesmo quando metadados coincidirem');
console.log('OK: interface real, serviços entre unidades, confirmação pós-Neon e divisão exata entre obras.');
