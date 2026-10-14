import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';

const supervisor={role:'SUPERVISOR',user:'EDUARDO'},finance={role:'FINANCEIRO',user:'FINANCEIRO'};
const now='2026-10-14T12:00:00Z';

function driver(pg){
 const sql=(parts,...values)=>{
  const text=parts.reduce((acc,part,i)=>acc+(i?'$'+i:'')+part,'');
  return {text,values,then(ok,err){return pg.query(text,values).then(x=>x.rows).then(ok,err);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{const out=[];for(const query of queries)out.push((await tx.query(query.text,query.values)).rows);return out;});
 return sql;
}
async function fixture(){
 const pg=new PGlite();
 await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('Colaborador QA','Pedreiro',180); INSERT INTO obras(unidade,nome) VALUES('FIEC','Obra de teste');");
 return {pg,sql:driver(pg)};
}
async function save(sql,state,role){
 const before=await readDatabase(sql),ops=buildOperations(before,state,role,now),requestId=crypto.randomUUID();
 await sql`SELECT aproar_web_apply(${before.version},${requestId},${role.user},${'test-'+requestId},${JSON.stringify(ops)}::jsonb)`;
 return readDatabase(sql);
}

for(const retroativo of [false,true]){
 test(`Supervisor informa e revisa passagem em apontamento ${retroativo?'retroativo':'normal'} e Financeiro preserva ajuste`,async()=>{
  const {pg,sql}=await fixture();
  try{
   let db=await readDatabase(sql),state=structuredClone(db.state);
   state.convocacoes.push({id:'temporary-conv',supervisor:'EDUARDO',dataServico:'2026-10-13',unidade:'FIEC',obraId:'1',turno:'Integral',colaboradores:['1']});
   state.apontamentos.push({id:'temporary-ap',convocacaoId:'temporary-conv',supervisor:'EDUARDO',dataServico:'2026-10-13',retroativo,itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Não',financeiro:180,noturno:0,acordo:0,ajudaCusto:11,observacao:'Primeiro apontamento',servicos:[{obraId:'1',periodo:'Integral'}]}]});
   db=await save(sql,state,supervisor);
   assert.equal(db.state.apontamentos[0].itens[0].ajudaCusto,11);
   assert.match(db.raw.convocacoes[0].observacao,/"valor_ajuda_custo":11/);
   assert.equal(db.state.apontamentos[0].retroativo,retroativo);

   state=structuredClone(db.state);
   state.apontamentos[0].itens[0].ajudaCusto=12;
   db=await save(sql,state,supervisor);
   assert.equal(db.state.apontamentos[0].itens[0].ajudaCusto,12,'O supervisor pode corrigir antes do ajuste financeiro');

   state=structuredClone(db.state);
   state.apontamentos[0].itens[0].ajudaCusto=25;
   db=await save(sql,state,finance);
   assert.equal(db.state.apontamentos[0].itens[0].ajudaCusto,25);
   assert.equal(db.state.apontamentos[0].itens[0].financeAdjusted,true);

   state=structuredClone(db.state);
   state.apontamentos[0].itens[0].ajudaCusto=10;
   assert.throws(()=>buildOperations(db,state,supervisor,now),/Somente o Financeiro/);
   assert.throws(()=>buildOperations(db,state,{role:'CONTROLADORIA',user:'CONTROLADORIA'},now),/Somente o Financeiro/);

   state=structuredClone(db.state);
   state.apontamentos[0].itens[0].observacao='Observação revisada sem alterar a passagem';
   db=await save(sql,state,supervisor);
   assert.equal(db.state.apontamentos[0].itens[0].ajudaCusto,25,'O valor validado pelo Financeiro permanece intacto');
  }finally{await pg.close();}
 });
}
test('Supervisor não pode editar passagem da equipe de outro supervisor',async()=>{
 const {pg,sql}=await fixture();
 try{
  let db=await readDatabase(sql),state=structuredClone(db.state);
  state.convocacoes.push({id:'test-conv',supervisor:'EDUARDO',dataServico:'2026-10-13',unidade:'FIEC',obraId:'1',turno:'Integral',colaboradores:['1']});
  state.apontamentos.push({id:'test-ap',convocacaoId:'test-conv',supervisor:'EDUARDO',dataServico:'2026-10-13',itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Não',financeiro:100,noturno:0,acordo:0,ajudaCusto:11,servicos:[{obraId:'1',periodo:'Integral'}]}]});
  db=await save(sql,state,supervisor);
  state=structuredClone(db.state);state.apontamentos[0].itens[0].ajudaCusto=25;
  assert.throws(()=>buildOperations(db,state,{role:'SUPERVISOR',user:'FELIPE'},now),/própria equipe/);
 }finally{await pg.close();}
});

test('Interface: detalhamento diario ordenado por data e nome e espacado do consolidado',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(js,/const e=financialEntries\(\)\.filter[\s\S]*?\.sort\(\(a,b\)=>a\.c\.dataServico\.localeCompare\(b\.c\.dataServico\)[\s\S]*?localeCompare\(b\.p\?\.nome\|\|'',\s*'pt-BR'/);
 assert.match(js,/pay-detail-section/);
 assert.match(html,/#pay-body \.pay-detail-section\s*\{[^}]*margin-top:\s*38px/);
 assert.match(js,/class="control row-ajuda-custo"/);
 assert.match(js,/row\.querySelector\('\.row-ajuda-custo'\)\?\.value/);
 assert.match(js,/item\?\.financeAdjusted\?'readonly/);
 assert.match(js,/value="11" label="Fortaleza/);
 assert.match(js,/retroDrafts\.get\(id\)\|\|previousItem\(id\)/);
});
