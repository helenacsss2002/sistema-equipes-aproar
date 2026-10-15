import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const ui=readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

test('avulso tem categoria fixa e custo integral de Controladoria',()=>{
 const code=ui.match(/function avulsoData\(funcao\)\{[\s\S]*?\n  \}/)?.[0];
 assert.ok(code,'Helper de categoria do avulso não encontrado');
 const avulsoData=runInNewContext('('+code+')');
 const profissional=avulsoData('Profissional'),servente=avulsoData('Servente');
 assert.equal(profissional.custo,241.74);
 assert.equal(profissional.categoria,'Profissional');
 assert.equal(profissional.avulso,'Sim');
 assert.equal(servente.custo,182.34);
 assert.equal(servente.categoria,'Ajudante');
 assert.equal(servente.funcao,'Servente');
 assert.throws(()=>avulsoData('Pedreiro'));
 assert.doesNotMatch(ui,/custo:180/);
});

test('todas as inclusões de avulso exigem Profissional ou Servente',()=>{
 for(const id of ['avulso-funcao','day-avulso-funcao','unit-avulso-function']){
  assert.match(ui,new RegExp("avulsoFuncaoSelect\\('"+id+"'\\)"));
 }
 assert.match(ui,/if\(!funcao\)return toast\('Selecione Profissional ou Servente para o avulso\.',true\)/);
 assert.doesNotMatch(ui,/unit-avulso-check/);
});

test('extra exige valor e gravacao depende da resposta do Neon',()=>{
 assert.match(ui,/function validateExtraAmounts\(items,scope=document\)/);
 assert.match(ui,/amount<=0/);
 assert.match(ui,/showSaveFeedback\(onlineMessage\|\|'Apontamento confirmado e gravado no Neon\.'/);
 assert.match(ui,/showSaveFeedback\(message,true\)/);
 assert.match(ui,/AbortController\(\)/);
 assert.match(ui,/Confira o histórico antes de tentar novamente para evitar duplicidade/);
 assert.doesNotMatch(ui,/for\(let attempt=0;attempt<2;attempt\+\+\)/);
});

test('avulso admite meia, uma, uma e meia e duas diarias sem mudar o financeiro',()=>{
 const rates={Profissional:241.74,Servente:182.34};
 const q={'Meia diária':.5,'Diária':1,'Uma e meia diária':1.5,'Duas diárias':2};
 for(const [cat,base] of Object.entries(rates)){
  for(const [kind,multiplier] of Object.entries(q)){
   const result=Math.round(base*multiplier*100)/100;
   assert.equal(result,Math.round(Number(base*multiplier.toFixed(1))*100)/100);
   assert.ok(result>0,cat+' '+kind);
  }
 }
 assert.deepEqual(Object.keys(q),['Meia diária','Diária','Uma e meia diária','Duas diárias']);
 assert.match(ui,/class="control row-avulso-diaria"/);
 assert.match(ui,/tipoDiariaAvulso:row\.querySelector\('\.row-avulso-diaria'\)/);
 assert.match(ui,/avulsoDiaria\*w\/\(weightSum\|\|1\)/);
 const op=readFileSync(new URL('./operations.js',import.meta.url),'utf8');
 const adapter=readFileSync(new URL('./neon-adapter.js',import.meta.url),'utf8');
 assert.match(op,/tipo_diaria_avulso:p\.avulso==='Sim'/);
 assert.match(op,/avulsoDailyTypes\.includes\(i\.tipoDiariaAvulso\)/);
 assert.match(adapter,/tipoDiariaAvulso:people\.get\(person\)\?\.avulso==='Sim'/);
 assert.match(op,/const finance=isPresent\?Number\(i\.financeiro\):0/);
});
