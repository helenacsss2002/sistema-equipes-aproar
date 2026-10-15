import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

test('Apontamento: rascunho do supervisor e capturado antes de gravar no Neon',()=>{
 assert.match(source,/function captureSupervisorDraft\(\)/);
 assert.match(source,/const pendingSupervisorDraft=captureSupervisorDraft\(\)/);
 assert.match(source,/restoreSupervisorDraft\(pendingSupervisorDraft\)/);
});

test('Apontamento: preserva campos das pessoas e servicos em caso de falha',()=>{
 const start=source.indexOf('function captureSupervisorDraft()');
 const end=source.indexOf('function saveData(onSuccess',start);
 assert.ok(start>=0&&end>start);
 const logic=source.slice(start,end);
 assert.match(logic,/\.person-card/);
 assert.match(logic,/\.allocation-row/);
 assert.match(logic,/\.row-extra/);
 assert.match(logic,/input\[name="retro-colab"\]:checked/);
});

test('Apontamento: falha nao pode ser apresentada como confirmacao de gravacao',()=>{
 assert.match(source,/O salvamento não foi confirmado\. Seus campos foram recuperados/);
 assert.match(source,/Verifique o histórico antes de tentar novamente/);
});
