import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {randomUUID} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';
import {metadata} from './neon-adapter.js';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const works=[
  {id:'1',unidade:'CENTRO',nome:'OBRA 123 - Reforma'},
  {id:'2',unidade:'CENTRO',nome:'Instalação elétrica'},
  {id:'3',unidade:'MUSEU',nome:'OBRA 123 - Reforma'},
  {id:'4',unidade:'SEBRAE',nome:'OBRA 999 - Adequação'}
];
const plain=value=>JSON.parse(JSON.stringify(value));
const roundMoney=value=>Math.round((Number(value)+Number.EPSILON)*100)/100;
function section(start,end){
  const a=app.indexOf(start),b=app.indexOf(end,a+start.length);
  assert(a>=0&&b>a,'Helper de serviços não encontrado: '+start);
  return app.slice(a,b);
}
function uiFixture(){
  const messages=[],suggestions=[];
  const ctx={OBRAS:structuredClone(works),
    field:(label,markup)=>'<label>'+label+'</label>'+markup,
    escapeHtml:value=>String(value).replace(/[&<>"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[char])),
    clean:value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim(),
    presence:status=>!['Falta','Atestado'].includes(status),
    obraById:id=>works.find(work=>String(work.id)===String(id)),
    toast:message=>messages.push(message),roundMoney,
    $$:()=>[],bindExtraWorkSearch(){},
    wireLiveSuggestions:(input,provider)=>suggestions.push({input,provider}),
    Event:class{constructor(type){this.type=type;}}
  };
  vm.createContext(ctx);
  vm.runInContext('let serviceListSeq=0;'+
    section('  function allocationRow(','  function itemServices(')+
    section('  function bindServiceRows(){','  function validateAgreementObservations(')+
    section('  function readPersonRows(','  function applyInlineExtras(')+
    section('  function validServices(','  function renderApontamentoRetroativo()')+
    '\nglobalThis.helpers={allocationRow,bindServiceRows,readPersonRows,validServices};',ctx);
  return {ctx,messages,suggestions};
}

test('Principal mantém nomes reais da origem; adicionais exibem unidade e nome, inclusive nomes iguais',()=>{
  const {ctx}=uiFixture(),{allocationRow}=ctx.helpers;
  const principal=allocationRow('CENTRO',{obraId:'1',periodo:'Manhã'});
  assert.match(principal,/value="OBRA 123 - Reforma"/);
  assert.doesNotMatch(principal,/MUSEU|SEBRAE/);
  const additional=allocationRow('CENTRO',{obraId:'3',periodo:'Tarde'},1);
  assert.match(additional,/value="MUSEU · OBRA 123 - Reforma"/);
  for(const work of works)assert(additional.includes(work.unidade+' · '+work.nome));
  assert.deepEqual(plain(ctx.OBRAS),works,'Montar a lista não reordena o cadastro compartilhado.');
});

test('Buscas existentes e botão de adicionar oferecem todas as unidades somente para serviços adicionais',()=>{
  const {ctx,suggestions}=uiFixture();
  const primaryInput={closest:selector=>selector==='.person-card'?{dataset:{unit:'CENTRO'}}:null};
  const additionalInput={closest:selector=>selector==='.additional-services'?{}:{dataset:{unit:'CENTRO'}}};
  const addedInput={};
  const add={},remove={},status={value:'Presente (Integral)'},counter={};
  let inserted='';
  const additional={insertAdjacentHTML(_position,markup){inserted=markup;}};
  const controls={'.add-service':add,'.remove-last-service':remove,'.row-status':status,
    '.additional-services':additional,'.service-count':counter,
    '.additional-services .allocation-row:last-child .service-work':addedInput};
  const card={dataset:{unit:'CENTRO'},querySelector:selector=>controls[selector]||null,
    querySelectorAll:()=>[{},{}],dispatchEvent(){}};
  ctx.$$=selector=>selector==='.person-card .service-work'?[primaryInput,additionalInput]:[card];
  ctx.helpers.bindServiceRows();
  assert.deepEqual(plain(suggestions[0].provider().map(work=>work.id)),['1','2']);
  assert.deepEqual(plain(suggestions[1].provider().map(work=>work.label)),works.map(work=>work.unidade+' · '+work.nome));
  add.onclick();
  assert.match(inserted,/MUSEU · OBRA 123 - Reforma/);
  assert.equal(suggestions[2].input,addedInput);
  assert.deepEqual(plain(suggestions[2].provider().map(work=>work.id)),['1','2','3','4']);
});

test('Leitura da ficha resolve IDs por unidade/nome e valida principal, adicionais e duplicidade',()=>{
  const {ctx,messages}=uiFixture();
  const rows=[{name:'OBRA 123 - Reforma',period:'Manhã'},{name:'MUSEU · OBRA 123 - Reforma',period:'Tarde'}];
  const controls={'.row-status':{value:'Presente (Integral)'},'.row-extra':{value:'Não'},
    '.row-obs':{value:''},'.row-noturno':{value:'0'},'.row-acordo':{value:'0'}};
  const row={dataset:{unit:'CENTRO'},querySelector:selector=>controls[selector]||null,
    querySelectorAll:()=>rows.map(item=>({querySelector:selector=>({value:selector==='.service-work'?item.name:item.period})}))};
  const items=plain(ctx.helpers.readPersonRows(['1'],{querySelector:()=>row}));
  assert.deepEqual(items[0].servicos,[{obraId:'1',periodo:'Manhã'},{obraId:'3',periodo:'Tarde'}]);
  assert.equal(ctx.helpers.validServices(items,'CENTRO'),true);
  const validate=services=>ctx.helpers.validServices([{status:'Presente (Integral)',servicos:services}],'CENTRO');
  assert.equal(validate([{obraId:'3',periodo:'Manhã'}]),false);
  assert.match(messages.at(-1),/principal/);
  assert.equal(validate([{obraId:'1',periodo:'Manhã'},{obraId:'missing',periodo:'Tarde'}]),false);
  assert.match(messages.at(-1),/adicional válido/);
  assert.equal(validate([{obraId:'1',periodo:'Manhã'},{obraId:'1',periodo:'Manhã'}]),false);
  rows[1].name='OBRA 123 - Reforma';
  assert.equal(ctx.helpers.readPersonRows(['1'],{querySelector:()=>row})[0].servicos[1].obraId,'',
    'Um nome sem a unidade não confirma um adicional ambíguo.');
});

function driver(pg){
  const sql=(strings,...values)=>{
    const text=strings.reduce((out,part,index)=>out+(index?'$'+index:'')+part,'');
    return {text,values,then(resolve,reject){return pg.query(text,values).then(result=>result.rows).then(resolve,reject);}};
  };
  sql.transaction=queries=>pg.transaction(async tx=>{
    const rows=[];for(const query of queries)rows.push((await tx.query(query.text,query.values)).rows);return rows;
  });
  return sql;
}

test('PGlite aceita adicional de outra unidade, preserva custos/autoria/histórico e mantém validações',async t=>{
  const pg=new PGlite(),session={role:'SUPERVISOR',user:'DJOUNE XAVIER'},time='2026-11-16T18:00:00Z';
  try{
    await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
    await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
    await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('PESSOA TESTE','Pintor',200),('COLEGA PRESERVADO','Servente',180)");
    for(const work of works)await pg.query('INSERT INTO obras(unidade,nome) VALUES($1,$2)',[work.unidade,work.nome]);
    await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,criado_por)
      VALUES(1,2,'2026-11-16','EDUARDO','Integral','EDUARDO');
      INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,apontado_por,custo_pago)
      VALUES('1','2026-11-16','2','EDUARDO','Presente (Integral)','EDUARDO',80);
      INSERT INTO servicos_apontamento(convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal)
      VALUES('1','1','OBRA 123 - Reforma','CENTRO','Integral',true);
      INSERT INTO auditoria(entidade,entidade_id,acao,usuario,contexto)
      VALUES('apontamentos','1','HISTORICO_PRESERVADO','EDUARDO','{"teste":true}');`);
    const sql=driver(pg),db=await readDatabase(sql),next=structuredClone(visibleState(db,session));
    next.convocacoes.push({id:'draft-cross-unit',supervisor:session.user,dataServico:'2026-11-16',unidade:'CENTRO',
      obraId:'',turno:'Integral',colaboradores:['1']});
    next.apontamentos.push({id:'draft-attendance',convocacaoId:'draft-cross-unit',supervisor:session.user,
      dataServico:'2026-11-16',retroativo:false,itens:[{colaboradorId:'1',status:'Presente (Integral)',
        extra:'Não',financeiro:120,noturno:0,acordo:20,ajudaCusto:11,observacao:'Serviços em duas unidades',
        servicos:[{obraId:'1',periodo:'Manhã'},{obraId:'3',periodo:'Tarde'}]}]});
    const item=next.apontamentos[0].itens[0];
    await t.test('Mantém principal na origem, IDs cadastrados, períodos válidos, unicidade e autoria',()=>{
      const attempt=services=>{const changed=structuredClone(next);changed.apontamentos[0].itens[0].servicos=services;return buildOperations(db,changed,session,time);};
      assert.throws(()=>attempt([{obraId:'3',periodo:'Manhã'}]),/principal precisa ser da unidade/);
      assert.throws(()=>attempt([{obraId:'1',periodo:'Manhã'},{obraId:'99999',periodo:'Tarde'}]),/serviços adicionais cadastrados/);
      assert.throws(()=>attempt([{obraId:'1',periodo:'Manhã'},{obraId:'3',periodo:'Outro'}]),/turno válido/);
      assert.throws(()=>attempt([{obraId:'1',periodo:'Manhã'},{obraId:'1',periodo:'Manhã'}]),/Serviço repetido/);
      const forged=structuredClone(next);forged.convocacoes.at(-1).supervisor='JOEL';
      assert.throws(()=>buildOperations(db,forged,session,time),/própria equipe/);
    });

    await t.test('Roundtrip grava snapshots corretos e replay não duplica o apontamento',async()=>{
      const oldConv=(await pg.query('SELECT * FROM convocacoes WHERE id=1')).rows[0];
      const oldPoint=(await pg.query('SELECT * FROM apontamentos WHERE id=1')).rows[0];
      const oldService=(await pg.query('SELECT * FROM servicos_apontamento WHERE id=1')).rows[0];
      const oldAudit=(await pg.query('SELECT * FROM auditoria WHERE id=1')).rows[0];
      const operations=buildOperations(db,next,session,time),requestId=randomUUID();
      const params=[db.version,requestId,session.user,'cross-unit-test',JSON.stringify(operations)];
      await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
      await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
      const after=await readDatabase(sql),conv=after.raw.convocacoes.find(row=>row.engenheiro===session.user);
      const point=after.raw.apontamentos.find(row=>row.engenheiro===session.user);
      const services=after.raw.servicos_apontamento.filter(row=>String(row.convocacao_id)===String(conv.id));
      assert.equal(after.raw.convocacoes.length,2);
      assert.equal(after.raw.apontamentos.length,2);
      assert.equal(services.length,2);
      assert.deepEqual(services.map(row=>[String(row.obra_id),row.unidade_snapshot,row.principal]),
        [['1','CENTRO',true],['3','MUSEU',false]]);
      assert.equal(String(conv.obra_id),'1');
      assert.equal(point.apontado_por,session.user);
      assert.equal(Number(point.custo_encargos_base),200);
      assert.equal(Number(point.custo_pago),120);
      assert.equal(Number(point.valor_acordo),20);
      assert.equal(Number(point.valor_extra),0);
      const meta=metadata(conv.observacao).meta;
      assert.equal(meta.valor_ajuda_custo,11);
      assert.equal(meta.servicos_adicionais[0].obra_id,'3');
      assert.equal(meta.servicos_adicionais[0].servico,'OBRA 123 - Reforma');
      const readConv=after.state.convocacoes.find(row=>row.supervisor===session.user);
      const readItem=after.state.apontamentos.find(row=>row.supervisor===session.user).itens[0];
      assert.equal(readConv.unidade,'CENTRO');
      assert.deepEqual(readItem.servicos,item.servicos);
      assert.equal(readItem.ajudaCusto,11);
      assert.deepEqual((await pg.query('SELECT * FROM convocacoes WHERE id=1')).rows[0],oldConv);
      assert.deepEqual((await pg.query('SELECT * FROM apontamentos WHERE id=1')).rows[0],oldPoint);
      assert.deepEqual((await pg.query('SELECT * FROM servicos_apontamento WHERE id=1')).rows[0],oldService);
      assert.deepEqual((await pg.query('SELECT * FROM auditoria WHERE id=1')).rows[0],oldAudit);
      assert.equal((await pg.query('SELECT count(*)::int n FROM aproar_web_requests')).rows[0].n,1);
    });
  }finally{await pg.close();}
});

test('Relatórios atribuem cada serviço à unidade real e conservam os centavos dos valores',()=>{
  const person={id:'1',nome:'PESSOA TESTE',valorDiaria:200};
  const item={colaboradorId:'1',status:'Presente (Integral)',ajudaCusto:11,acordo:20,noturno:0,financeiro:120,extra:'Não',valorExtraDisponivel:0};
  const conv={id:'new',dataServico:'2026-11-16',supervisor:'DJOUNE XAVIER',obraId:'1',unidade:'CENTRO',turno:'Integral'};
  const services=[{obraId:'1',periodo:'Manhã'},{obraId:'3',periodo:'Tarde'}];
  const ctx={state:{convocacoes:[conv],extras:[],apontamentos:[{dataServico:conv.dataServico,supervisor:conv.supervisor,itens:[item]}]},
    reportFilters:{inicio:'2026-11-16',fim:'2026-11-16',supervisor:'Todos',obra:'Todas'},selectedCycle:'custom',
    roundMoney,clean:value=>String(value).toUpperCase(),apForConv:()=>({itens:[item]}),colaboradorById:()=>person,
    serviceList:()=>services,obraById:id=>works.find(work=>work.id===id),presence:()=>true,
    nocturnal:()=>0,dayCost:()=>200,extraMultiplier:()=>0,dangerEligible:()=>false};
  vm.createContext(ctx);
  vm.runInContext(section('  function periodBlocks(','  // Distribui valores monetários')+
    section('  function splitMoneyExactly(','  function financialSummaryRows(')+'\nglobalThis.rows=entries;',ctx);
  const rows=Array.from(ctx.rows());
  assert.deepEqual(rows.map(row=>row.c.unidade),['CENTRO','MUSEU']);
  for(const [field,total] of [['daily',200],['finance',120],['bonus',20],['ajudaCusto',11]])
    assert.equal(roundMoney(rows.reduce((sum,row)=>sum+row[field],0)),total,field);
});
