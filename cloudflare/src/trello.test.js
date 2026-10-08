import test from 'node:test';
import assert from 'node:assert/strict';
import {unidadeCard,selecionar,planejar,consultarTrello} from './trello.js';
test('Trello: unidade fisica do titulo prevalece sobre FIEC',()=>{
 assert.equal(unidadeCard({name:'FIEC | SENAI CENTRO | 11936.76667'}),'CENTRO');
 assert.equal(unidadeCard({name:'Obra sem unidade',desc:'UNIDADE: MARACANAÚ'}),'MARACANAÚ');
 assert.equal(unidadeCard({name:'FIEC - manutenção'}),'FIEC');
 assert.equal(unidadeCard({name:'Sem detalhes'}),'NÃO IDENTIFICADA');
});
test('Trello: seleciona somente cards ativos da lista EM EXECUÇÃO',()=>{
 const board={lists:[{id:'x',name:'EM EXECUÇÃO'},{id:'y',name:'CONCLUÍDOS'}],cards:[{id:'a',idList:'x',name:'Teste ativo'},{id:'b',idList:'y',name:'Teste encerrado'}]};
 const r=selecionar(board);assert.equal(r.cards.length,1);assert.equal(r.cards[0].id,'a');
 assert.equal(selecionar(board,{cardId:'b'}).cards[0].id,'b');
 assert.throws(()=>selecionar(board,{listId:'inexistente'}),/Lista/);
});
test('Trello: preserva obra existente e identifica novos cards',()=>{
 const works=[{id:'1',nome:'Serviço 1',unidade:'CENTRO',trello_card_id:'a',trello_list_id:'old',trello_unidade_manual:false}];
 const cards=[{id:'a',idList:'now',name:'Serviço 1',desc:'CENTRO'},{id:'b',idList:'now',name:'Serviço 2',desc:'UNIDADE: SEBRAE'}];
 const r=planejar(works,cards);
 assert.equal(r.updates.length,1);assert.equal(r.updates[0].id,'1');
 assert.equal(r.inserts.length,1);assert.equal(r.inserts[0].unit,'SEBRAE');
 assert.equal(r.skipped.length,0);
});
test('Trello: unidade manual permanece e nunca exclui obra local',()=>{
 const works=[{id:'2',nome:'Antiga',unidade:'UNIFOR',trello_card_id:'abc',trello_list_id:'x',trello_unidade_manual:true},{id:'3',nome:'Histórica',unidade:'CENTRO',trello_card_id:null}];
 const r=planejar(works,[{id:'abc',idList:'y',name:'Antiga atualizada',desc:'LOCAL: SEBRAE'}]);
 assert.equal(r.updates[0].unit,'UNIFOR');
 assert.equal(works.length,2);
});
test('Trello: consulta somente os cards abertos',async()=>{
 const source={lists:[{id:'l',name:'EM EXECUÇÃO',closed:false}],cards:[{id:'a',idList:'l',name:'Obra ativa',closed:false},{id:'b',idList:'l',name:'Arquivada',closed:true}]};
 const fn=async()=>({ok:true,headers:new Headers(),json:async()=>source});
 const out=await consultarTrello(fn);assert.equal(out.cards.length,1);assert.equal(out.cards[0].id,'a');
});

test('Trello: informa erro HTTP de forma clara',async()=>{
 const response=async()=>({ok:false,status:403,headers:new Headers()});
 await assert.rejects(()=>consultarTrello(response),/HTTP 403/);
});
test('Trello: classifica resposta HTML em vez de JSON',async()=>{
 const response=async()=>({ok:true,status:200,headers:new Headers(),json:async()=>{throw new SyntaxError('Unexpected token');}});
 await assert.rejects(()=>consultarTrello(response),/JSON válido/);
});
test('Trello: classifica erro de conexão externa',async()=>{
 const response=async()=>{throw new TypeError('fetch failed');};
 await assert.rejects(()=>consultarTrello(response),/conexão entre a Cloudflare e o Trello/);
});

test('Interface: busca do Trello usa todos os cards e nao volta para cadastro local',async()=>{
 const source=(await import('node:fs')).readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const start=source.indexOf('const liveResults=()=>{');
 const end=source.indexOf("const body=$('#settings-body');",start);
 assert.ok(start>=0&&end>start,'Tela de configuracoes do Trello deve existir.');
 const handler=source.slice(start,end);
 assert.ok(handler.includes("$$('[data-trello-card]').forEach"),'Cada botao de card precisa ter evento.');
 assert.ok(!handler.includes("$('[data-trello-card]').forEach")||handler.includes("$$('[data-trello-card]').forEach"),'Selector deve retornar lista.');
 assert.ok(handler.includes('cardSearch.oninput=liveResults'),'Busca deve usar cards retornados da API.');
 assert.ok(!handler.includes("$('#trello-search').oninput="),'Busca local nao deve substituir busca do Trello.');
});
