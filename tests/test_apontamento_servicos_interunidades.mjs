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
  clean: v => String(v ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleUpperCase('pt-BR').trim(),
  presence: status => status.startsWith('Presente'),
  obraById: id => works.find(w => String(w.id) === String(id)),
  toast: () => {},
  document: {},
  APONTAMENTO_EXTRA_OPTIONS: [['Não','Não'],['Meia diária','Meia Diária'],['Diária','Diária'],['Uma e meia diária','1 e meia diária'],['Duas diárias','Duas diárias']],
  EXTRA_OPTIONS: ['Não','Meia diária','Diária','Uma e meia diária','Duas diárias'],
  AVULSO_DIARIA_OPTIONS: ['Meia diária','Diária','Uma e meia diária','Duas diárias'],
  category: () => 'Profissional',
  dangerEligible: () => false,
  roundMoney: value => Math.round((Number(value)||0)*100)/100,
  colaboradorById: () => ({id:'fabiano',nome:'Fabiano',funcao:'Pedreiro',custo:241.74})
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
vm.runInContext(extract('  function dayCost(', '  function brazilParts('), ctx);
vm.runInContext(extract('  function serviceList(', '  function financialEntries('), ctx);

const principal = ctx.allocationRow('ESCRITORIO', { obraId: '1', periodo: 'Integral' }, 0);
assert(principal.includes('2100 - Escritório'));
assert(!principal.includes('2139 - FIEC'), 'obra principal deve continuar restrita à unidade');
const adicional = ctx.allocationRow('ESCRITORIO', { obraId: '2', periodo: 'Integral' }, 1);
assert(adicional.includes('2139 - FIEC'));
assert(adicional.includes('FIEC · 2139 - FIEC'));
assert(adicional.includes('CENTRO · 2139 - FIEC'));
assert(adicional.includes('data-work-id="2"'), 'obra adicional deve conservar o ID real');
const independente = ctx.allocationRow('ESCRITORIO', { obraId:'2', periodo:'Integral', extra:'Diária', extraIndependente:true }, 1);
assert(independente.includes('class="control service-extra"'), 'serviço adicional deve apresentar a mesma lista de extra');
assert(independente.includes('value="Diária" selected'), 'categoria extra selecionada deve persistir na tela');
assert(independente.includes('service-extra-independent" checked'), 'serviço independente deve permanecer marcado após F5');
assert(!principal.includes('service-extra-independent'), 'não aplicar seletor de extra adicional ao serviço principal');

const services = [
  ['1', '2100 - Escritório', false],
  ['2', 'FIEC · 2139 - FIEC', true],
  ['3', 'CENTRO · 2150 - Centro', true]
];
const serviceRows = services.map(([id, label, isAdditional]) => ({
  closest: selector => selector === '.additional-services' ? (isAdditional ? {} : null) : null,
  querySelector: selector => selector === '.service-work'
    ? { dataset: { workId: id }, value: label }
    : selector === '.service-period' ? { value: 'Integral' }
    : selector === '.service-extra' ? { value: id==='2'?'Diária':id==='3'?'Meia diária':'Não' }
    : selector === '.service-extra-independent' ? { checked: id==='2' }
    : null
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
assert.equal(item.servicos[1].extra, 'Diária');
assert.equal(item.servicos[1].extraIndependente, true);
assert.equal(item.servicos[2].extra, 'Meia diária');
assert.equal(item.servicos[2].extraIndependente, false);
assert.equal(ctx.validServices([item], 'ESCRITORIO'), true);
assert.equal(ctx.validServices([{ ...item, servicos: [
  {obraId:'1',periodo:'Integral',extra:'Não'},
  {obraId:'2',periodo:'Integral',extra:'Não',extraIndependente:true}
]}], 'ESCRITORIO'), false, 'extra independente sem categoria deve falhar');
assert.equal(ctx.validServices([{ ...item, servicos: [{ obraId: '2', periodo: 'Integral' }] }], 'ESCRITORIO'), false);
assert.equal(ctx.validServices([{ ...item, servicos: [{ obraId: '1', periodo: 'Integral' }, { obraId: '999', periodo: 'Integral' }] }], 'ESCRITORIO'), false);
assert(source.includes("const additional=Boolean(input.closest('.additional-services'));"));
assert(source.includes("$$('.person-card .service-work').forEach(bindServiceWork);"));
assert(source.includes("bindServiceWork(added);"));
const share = 300 / item.servicos.length;
assert.equal(share, 100, '3 obras -> rateio igual já existente; frontend não recalcula custos');
// Verificar custos: o Serviço FIEC é apenas extra (diária SEINFRA cheia);
 // o Centro divide a diária normal com o principal e recebe a própria meia extra.
ctx.state={
  convocacoes:[{id:'c1',dataServico:'2026-11-25',supervisor:'EDUARDO',unidade:'ESCRITORIO',turno:'Integral',obraId:'1',colaboradores:['fabiano']}],
  extras:[]
};
ctx.apForConv = () => ({itens:[item]});
ctx.reportFilters={inicio:'2026-11-25',fim:'2026-11-25',supervisor:'Todos',obra:'Todas'};
const custo=Array.from(ctx.entries());
assert.equal(custo.length,3);
const porObra=Object.fromEntries(custo.map(x=>[String(x.c.obraId),x]));
assert.equal(porObra['1'].daily,120.87, 'serviço principal divide diária com terceiro serviço');
assert.equal(porObra['2'].daily,0, 'extra independente não rateia diária');
assert.equal(porObra['2'].extra,241.74, 'extra diária SEINFRA cheia no serviço FIEC');
assert.equal(porObra['3'].daily,120.87, 'terceiro serviço mantém rateio igual');
assert.equal(porObra['3'].extra,120.87, 'meia extra SEINFRA cheia no serviço Centro');
assert.equal(custo.reduce((sum,row)=>sum+row.daily,0),241.74);
assert.equal(custo.reduce((sum,row)=>sum+row.extra,0),362.61);
// Contrato de leitura/gravação no Worker: o metadado não pode sumir após F5.
const worker=readFileSync(new URL('../cloudflare-production/worker.js',import.meta.url),'utf8');
assert(worker.includes('extra_independente: s.extraIndependente'));
assert(worker.includes('extra:details?.extra||"Não"'));
assert(worker.includes('s.extraIndependente && s.extra === "Não"'));
assert(worker.includes('const samePersistedServices='), 'vínculos físicos devem ser conferidos');
assert(worker.includes('Number(b.principal)-Number(a.principal)'), 'a obra principal deve aparecer primeiro após F5');
assert(source.includes('const verifyAdminServices=confirmed=>'), 'Controladoria também deve conferir extras no Neon');
assert(source.includes('},verifyDayServices))return;'), 'Supervisor deve verificar os serviços após salvar');
assert(source.includes('typeof verifyPersisted===\'function\''), 'leitura do Neon deve validar os serviços');
console.log('OK: seleção de extras por serviço, independente sem rateio, custo SEINFRA integral, preservação no Worker.');
