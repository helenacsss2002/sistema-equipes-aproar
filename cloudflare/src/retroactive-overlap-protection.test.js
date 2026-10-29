import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');

test('retroativo impede enviar concorrentes em turno sobreposto e preserva o rascunho',()=>{
 const start=app.indexOf("$('#form-retro').onsubmit");
 const end=app.indexOf('\n\n\n  function renderExtras()',start);
 assert.ok(start>0&&end>start);
 const submit=app.slice(start,end);
 assert.match(submit,/const conflitosRetro=ids.flatMap/);
 assert.match(submit,/c\.dataServico===dataServico/);
 assert.match(submit,/overlaps\(c\.turno,turnoRetro\)/);
 assert.match(submit,/c\.supervisor===responsavel&&c\.unidade===unidade\.value&&c\.turno===turnoRetro/);
 assert.match(submit,/if\(conflitosRetro\.length\)\{/);
 assert.match(submit,/Nenhum apontamento foi salvo ou apagado/);
 assert.ok(submit.indexOf('if(conflitosRetro.length)')<submit.indexOf('if(!applyInlineExtras('),'nao deve mutar extras antes de verificar conflito');
 assert.ok(submit.indexOf('if(conflitosRetro.length)')<submit.indexOf('state.convocacoes.push(conv)'),'nao deve criar convocacao conflitante');
 assert.match(submit,/readPersonRows\(ids\)/);
 assert.match(submit,/saveData\(/);
});

test('o servidor continua validando conflitos e impedindo registros duplicados',()=>{
 const logic=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
 assert.match(logic,/Conflito: \$\{staff\.get\(pid\)\.nome\} já está convocado/);
 assert.match(logic,/if\(pointed\.has\(key\)\)fail\('Apontamento duplicado\.'/);
 assert.match(worker,/if\(e\.code==='23505'\)/);
});
