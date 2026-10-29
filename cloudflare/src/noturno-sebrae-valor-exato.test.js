import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const actor={role:'CONTROLADORIA',user:'CONTROLADORIA'};
function driver(pg){
 const sql=(strings,...values)=>{const text=strings.reduce((out,s,i)=>out+(i?'$'+i:'')+s,'');return {text,values,then(ok,fail){return pg.query(text,values).then(r=>r.rows).then(ok,fail);}};};
 sql.transaction=queries=>pg.transaction(async tx=>{const result=[];for(const q of queries)result.push((await tx.query(q.text,q.values)).rows);return result;});
 return sql;
}
async function fixture(){
 const pg=new PGlite();
 await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('ANTONIO FERNANDO DA SILVA','PEDREIRO',241.74)");
 await pg.exec("INSERT INTO obras(unidade,nome) VALUES('SEBRAE','APRL009 - REFORMA DO 6° ANDAR - SEBRAE')");
 await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,status,valor_adicional_noturno,observacao) VALUES(1,1,'2026-09-12','SOARES','Integral','Presente (Integral)',90,'Turno: Integral ||APROAR_META|| {\"valor_adicional_noturno\":90}')");
 await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_adicional_noturno,apontado_por,custo_encargos_base,custos_separados) VALUES('1','2026-09-12','1','SOARES','Presente (Integral)',90,'SOARES',241.74,true)");
 await pg.exec("INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal) VALUES('1','1','SEBRAE','APRL009 - REFORMA DO 6° ANDAR - SEBRAE','Integral',true)");
 return {pg,sql:driver(pg)};
}
test('Alterar 90 → 0 → 50 → 90 → 0 grava e lê o valor exato no Neon, sem reverter para 90',async()=>{
 const {pg,sql}=await fixture();
 try{
  let db=await readDatabase(sql);
  assert.equal(db.state.apontamentos[0].itens[0].noturno,90);
  for(const [idx,value] of [0,50,90,0].entries()){
   const next=structuredClone(db.state);
   next.apontamentos[0].itens[0].noturno=value;
   const ops=buildOperations(db,next,actor,new Date(Date.UTC(2026,9,29,14,45,idx)).toISOString());
   assert.equal(Number(ops.find(op=>op.table==='apontamentos'&&op.action==='update')?.data.valor_adicional_noturno),value);
   assert.equal(Number(ops.find(op=>op.table==='convocacoes'&&op.action==='update')?.data.valor_adicional_noturno),value);
   const id=crypto.randomUUID();
   await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[db.version,id,actor.user,'night-qa',JSON.stringify(ops)]);
   db=await readDatabase(sql);
   assert.equal(db.state.apontamentos[0].itens[0].noturno,value,'Retorno lido do banco deve manter '+value);
   assert.equal(Number(db.raw.apontamentos[0].valor_adicional_noturno),value);
   assert.equal(Number(db.raw.convocacoes[0].valor_adicional_noturno),value);
   const meta=JSON.parse(String(db.raw.convocacoes[0].observacao).split(' ||APROAR_META|| ')[1]);
   assert.equal(meta.valor_adicional_noturno,value,'Metadados não podem reintroduzir 90');
  }
  assert.equal((await pg.query("SELECT count(*)::int n FROM apontamentos")).rows[0].n,1);
 }finally{await pg.close();}
});
test('Ficha do SEBRAE seleciona precisamente 0, 50 ou 90; sem apontamento o padrão é 0 e nunca 90',()=>{
 const a=app.indexOf('  function personRow('),b=app.indexOf('  // Busca viva independente',a);
 assert(a>0&&b>a);
 const ctx={
  colaboradorById:()=>({id:'131',nome:'ANTONIO FERNANDO DA SILVA',funcao:'PEDREIRO',avulso:'Não'}),
  itemServices:(item,id)=>item?.servicos?.length?item.servicos:[{obraId:id,periodo:'Integral'}],
  extraRecordFor:()=>null,
  STATUS_OPTIONS:['Presente (Integral)','Presente (Só Manhã)','Presente (Só Tarde)','Falta','Atestado'],
  EXTRA_OPTIONS:['Não','Diária'],
  APONTAMENTO_EXTRA_OPTIONS:[['Não','Não'],['Diária','Diária']],
  OBRAS:[{id:'1',nome:'APRL009 - REFORMA DO 6° ANDAR - SEBRAE',unidade:'SEBRAE'}],
  obraById:()=>({id:'1',nome:'APRL009 - REFORMA DO 6° ANDAR - SEBRAE',unidade:'SEBRAE'}),
  field:(label,html)=>'<label>'+label+html+'</label>',
  allocationRow:()=>'<div class="allocation-row"></div>',
  extraWorkSearchMarkup:()=>'<input class="row-extra-work">',
  presence:status=>String(status).startsWith('Presente'),
  escapeHtml:value=>String(value??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;'),
  roundMoney:n=>Math.round(n*100)/100,
  isApprovedFinancial:()=>false,
  perfilAtual:'CONTROLADORIA',
  portalDate:'2026-09-12',
  supervisorAtual:'SOARES'
 };
 vm.createContext(ctx);
 vm.runInContext(app.slice(a,b)+'\nglobalThis.row=personRow;',ctx);
 for(const value of [0,50,90]){
  const item={status:'Presente (Integral)',noturno:value,servicos:[{obraId:'1',periodo:'Integral'}]};
  const html=ctx.row('131',item,'SEBRAE','1','2026-09-12','SOARES');
  assert.match(html,new RegExp('<option value="'+value+'" selected>'),'Deve selecionar o valor que foi salvo: '+value);
  for(const other of [0,50,90].filter(v=>v!==value))
   assert.doesNotMatch(html,new RegExp('<option value="'+other+'" selected>'),'Não deve selecionar '+other);
 }
 const blank=ctx.row('131',null,'SEBRAE','1','2026-09-12','SOARES');
 assert.match(blank,/<option value="0" selected>/);
 assert.doesNotMatch(blank,/<option value="90" selected>/);
});
test('Tela da Controladoria espera o salvamento confirmado antes de atualizar e limpa o rascunho antigo',()=>{
 const begin=app.indexOf('  function renderApontamentoNormal()'),end=app.indexOf('  let serviceListSeq=',begin);
 assert(begin>0&&end>begin);
 const section=app.slice(begin,end);
 assert.match(section,/captureAdminApDrafts\(\);if\(!saveData\(\(\)=>\{adminApDrafts\.delete\(String\(conv\.id\)\);renderApontamentoNormal\(\);\}\)\)return/);
 assert.doesNotMatch(section,/toast\('Apontamento salvo\.'\);refreshTeam\(\);/);
 assert.match(app,/noturno:Number\(row\.querySelector\('\.row-noturno'\)\.value\)\|\|0/);
});
