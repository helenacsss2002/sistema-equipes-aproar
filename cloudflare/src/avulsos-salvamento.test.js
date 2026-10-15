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
