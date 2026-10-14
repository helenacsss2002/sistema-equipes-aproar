import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const src=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
function section(start,end){
 const a=src.indexOf(start),b=src.indexOf(end,a+start.length);
 assert.ok(a>=0&&b>a,'Trecho não encontrado: '+start);
 return src.slice(a,b);
}
function setup(){
 const downloads=[],urls=new Map();
 const record={id:'1',c:{supervisor:'EDUARDO',dataServico:'2026-10-13',unidade:'FIEC',obraId:'1'},p:{id:'1',nome:'Álvaro QA',funcao:'Pedreiro'},
   i:{status:'Presente (Integral)',observacao:'Teste financeiro'},service:{periodo:'Integral'},
   finance:100,night:0,bonus:10,ajudaCusto:11,units:new Set(['FIEC']),works:new Set(['1'])};
 const ctx={
  console,Uint8Array,DataView,TextEncoder,TextDecoder,Blob,Set,Map,Date,Math,URL:{
   createObjectURL(blob){const url='blob:test/'+urls.size;urls.set(url,blob);return url;},
   revokeObjectURL(){}
  },setTimeout(){},document:{
   createElement(name){assert.equal(name,'a');return {href:'',download:'',click(){downloads.push({filename:this.download,blob:urls.get(this.href)});}};}
  },reportFilters:{inicio:'2026-10-13',fim:'2026-10-13',supervisor:'Todos',obra:'Todas'},
  perfilAtual:'FINANCEIRO',viewAtual:'pagamentos',selectedCycle:'custom',
  onlineSession:{role:'FINANCEIRO'},reportPeriod:null,
  isoToday:()=> '2026-10-14',formatDate:s=>s,formatDateTime:s=>s,
  financialCycle:()=>({pagamento:'2026-10-14'}),
  money:n=>'R$ '+Number(n).toFixed(2).replace('.',','),roundMoney:n=>Math.round(n*100)/100,
  reportFiltersReady:true,entries:()=>[record],financialEntries:()=>[record],
  financialSummaryRows:()=>[{id:'1',nome:'Álvaro QA',funcao:'Pedreiro',supervisores:'EDUARDO',unidades:'FIEC',dias:1,finance:100,night:0,bonus:10,ajudaCusto:11,total:121}],
  presence:status=>status.startsWith('Presente'),
  obraById:id=>({id,nome:'OBRA 147 - TESTE',unidade:'FIEC'}),toast:msg=>{throw Error('Falha exibida ao usuário: '+msg);}
 };
 ctx.globalThis=ctx;ctx.self=ctx;ctx.window=ctx;
 vm.createContext(ctx);
 const fragment=[
  section('  function localDownload(', '  function bindExports()'),
  section('  const xmlSafe=', '  function controlValues('),
  section('  function financialWorkNumber(', '  function financialWorkbook('),
  section('  function financialWorkbook()', '  async function xlsxRows(')
 ].join('\n');
 vm.runInContext(fragment,ctx,{timeout:8000});
 return {ctx,downloads};
}
test('Financeiro em Pagamentos baixa relatório CSV e arquivos Excel completos',async()=>{
 const {ctx,downloads}=setup();
 ctx.exportFinancialSummaryExcel();
 ctx.exportReportsExcel();
 assert.equal(downloads.length,2);
 assert.ok(downloads.every(x=>x.blob instanceof Blob));
 assert.match(downloads[0].filename,/financeiro_consolidado_colaboradores.*\.xlsx$/);
 assert.match(downloads[1].filename,/financeiro.*\.xlsx$/);
 for(const {blob} of downloads)assert.equal(Buffer.from(await blob.arrayBuffer()).subarray(0,4).toString('hex'),'504b0304');
});
test('PDF financeiro e consolidado são gerados com a biblioteca distribuída pelo Worker',async()=>{
 const {ctx,downloads}=setup();
 const pdfSource=fs.readFileSync(new URL('../public/pdf-lib.min.js',import.meta.url),'utf8');
 vm.runInContext(pdfSource,ctx,{timeout:8000});
 assert.ok(ctx.PDFLib?.PDFDocument,'Biblioteca PDFLib deve estar disponível');
 await ctx.reportPDF('financial');
 await ctx.reportPDF('financial-consolidated');
 assert.equal(downloads.length,2);
 for(const {filename,blob} of downloads){
   assert.match(filename,/\.pdf$/);
   const bytes=Buffer.from(await blob.arrayBuffer());
   assert.equal(bytes.subarray(0,5).toString(),'%PDF-');
   assert.ok(bytes.length>200);
 }
});
