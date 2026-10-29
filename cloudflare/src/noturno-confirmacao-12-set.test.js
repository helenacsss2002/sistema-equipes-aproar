import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const source=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
const marker='  function nightChangesToVerify(previous,next){';
const start=ui.indexOf(marker),end=ui.indexOf('  function saveData(onSuccess=null){',start);
assert(start>=0&&end>start);
function verifier(){
 const ctx={};vm.createContext(ctx);
 vm.runInContext(ui.slice(start,end)+'\nglobalThis.verify={changes:nightChangesToVerify,match:nightValuesMatch}',ctx);
 return ctx.verify;
}
const snapshot=amount=>({
 apontamentos:[{convocacaoId:'1728',dataServico:'2026-09-12',
  itens:[{colaboradorId:'131',noturno:amount,status:'Presente (Integral)'}]}]
});
test('Seleção 0 ou 50 em 12/09 não pode confirmar quando Neon ainda mostra 90',()=>{
 const {changes,match}=verifier();
 for(const amount of [0,50]){
   const expected=changes(snapshot(90),snapshot(amount));
   assert.equal(expected.length,1);
   assert.equal(expected[0].key,'1728|131');
   assert.equal(expected[0].expected,amount);
   assert.equal(match(snapshot(90),expected),false,'Um registro de R$90 não pode confirmar o valor R$'+amount);
   assert.equal(match(snapshot(amount),expected),true);
 }
 assert.equal(changes(snapshot(90),snapshot(90)).length,0);
});
test('O valor 90 também permanece após ser alterado de 0 ou 50',()=>{
 const {changes,match}=verifier();
 for(const amount of [0,50]){
   assert.equal(match(snapshot(90),changes(snapshot(amount),snapshot(90))),true);
 }
 assert.equal(match({apontamentos:[]},changes(snapshot(90),snapshot(0))),false);
});
test('O app só mostra confirmação depois de recuperar o adicional noturno do Neon',()=>{
 assert.match(ui,/const pendingNightChanges=nightChangesToVerify\(onlineConfirmed,state\)/);
 assert.match(ui,/pendingNightChanges\.length\?await restoreOnlineSession/);
 assert.match(ui,/nightValuesMatch\(result\.state,pendingNightChanges\)/);
 assert.match(ui,/if\(!nightConfirmed\)/);
 assert.match(ui,/onlineWritable=false; \/\/ Precisa recarregar/);
 assert.match(ui,/const persisted=changes\.every\(change=>/);
 assert.match(ui,/if\(!persisted\)/);
 assert.match(ui,/Valores financeiros conferidos e confirmados no Neon/);
});
test('Apontamento já confirmado pelo Financeiro não volta silenciosamente para 90',()=>{
 assert.match(source,/O adicional noturno foi ajustado pelo Financeiro/);
 assert.match(source,/solicite autorização da Controladoria ou do Financeiro/);
 assert.match(source,/!\(releaseGrant\?\.data\?\.contexto\?\.fields\|\|\[\]\)\.includes\('Adicional noturno'\)/);
});
function driver(pg){
 const sql=(strings,...args)=>{
  const text=strings.reduce((out,s,i)=>out+(i?'$'+i:'')+s,'');
  return {text,values:args,then(ok,fail){return pg.query(text,args).then(r=>r.rows).then(ok,fail)}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{const rows=[];for(const query of queries)rows.push((await tx.query(query.text,query.values)).rows);return rows;});
 return sql;
}
test('Registro retroativo de 12/09 preserva exatamente 0, 50 e 90 após reabrir banco isolado',async()=>{
 const pg=new PGlite();
 try{
   await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
   await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
   await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('TESTE NOTURNO SETEMBRO','Pintor',200)");
   await pg.exec("INSERT INTO obras(nome,unidade) VALUES('SEBRAE TESTE NOTURNO','SEBRAE')");
   await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao) VALUES(1,1,'2026-09-12','SOARES','Integral','Turno: Integral')");
   await pg.exec("INSERT INTO apontamentos(convocacao_id,colaborador_id,data_servico,engenheiro,status,valor_adicional_noturno,apontado_em,apontado_por,custo_encargos_base) VALUES('1','1','2026-09-12','SOARES','Presente (Integral)',90,now(),'SOARES',200)");
   await pg.exec("INSERT INTO servicos_apontamento(convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal) VALUES('1','1','SEBRAE TESTE NOTURNO','SEBRAE','Integral',true)");
   const sql=driver(pg);
   for(const [i,night] of [0,50,90,0].entries()){
     const db=await readDatabase(sql),next=structuredClone(db.state);
     assert.equal(next.apontamentos.length,1);
     next.apontamentos[0].itens[0].noturno=night;
     const ops=buildOperations(db,next,{role:'CONTROLADORIA',user:'CONTROLADORIA'},'2026-10-29T15:00:00Z');
     if(ops.length){
       await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',
        [db.version,'bbbbb00'+i+'-b00b-4000-8000-000000000001','CONTROLADORIA','sha-'+i,JSON.stringify(ops)]);
     }
     const fresh=await readDatabase(sql);
     assert.equal(fresh.state.apontamentos[0].itens[0].noturno,night,'Banco e tela precisam concordar com o valor selecionado');
     assert.equal(Number(fresh.raw.apontamentos[0].valor_adicional_noturno),night);
     assert.equal(Number(fresh.raw.convocacoes[0].valor_adicional_noturno),night);
   }
 }finally{await pg.close();}
});
