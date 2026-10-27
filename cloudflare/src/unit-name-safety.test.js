import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {isSafeUnitName} from './unit-label.js';
import {planejar} from './trello.js';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const data=fs.readFileSync(new URL('./data.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const migration=fs.readFileSync(new URL('../migracao_corrigir_unidades_links_20261027.sql',import.meta.url),'utf8');

test('Unidades validas continuam disponiveis; links e textos extensos sao bloqueados',()=>{
  for(const unit of ['CENTRO','BARRA DO CEARÁ','SÃO GONÇALO DO AMARANTE','NÃO IDENTIFICADA','IDALYA E MATHEUS','SESI EUSÉBIO']) {
    assert.equal(isSafeUnitName(unit),true,unit);
  }
  for(const invalid of [
    'LINK PARA ACESSO AO DRIVE: [OBRA](HTTPS://APROARENG-MY.SHAREPOINT.COM/ARQUIVO)',
    '- LINK PARA ACESSO AO DRIVE: OBRA 08',
    'https://trello.com/c/example',
    'www.example.com',
    'UNIDADE '.repeat(15),
    '',
    null
  ])assert.equal(isSafeUnitName(invalid),false,String(invalid));
});

test('API, bootstrap e listas dos dois perfis nao exibem nomes de unidade invalidos',()=>{
  assert.match(worker,/import \{isSafeUnitName\} from '\.\/unit-label\.js'/);
  assert.match(worker,/!isSafeUnitName\(name\)/);
  assert.match(worker,/!isSafeUnitName\(unit\)/);
  assert.match(data,/filter\(isSafeUnitName\)/);
  assert.match(app,/function unitLabelIsSafe\(label\)/);
  assert.match(app,/function adminUnits\(\)\{return .*\.filter\(unitLabelIsSafe\)\.sort\(\)/);
  assert.match(app,/const currentUnits=\(\)=>.*filter\(unitLabelIsSafe\)/);
  assert.match(html,/select\.control\s*\{[^}]*max-width:100%;[^}]*min-width:0;/);
});

test('Trello nao reintroduz a unidade com link nem sobrescreve escolha manual',()=>{
  const invalid='LINK PARA ACESSO AO DRIVE: [OBRA 08](HTTPS://SHAREPOINT.COM/arquivo)';
  const base=[
    {id:'271',nome:'OBRA APR4C008 - ALMOXARFIADO GERAL - HOSPITAL SÃO CARLOS',unidade:invalid,
      trello_card_id:'card1',trello_unidade_manual:true,trello_list_id:'lista'}
  ];
  const cards=[{id:'card1',idList:'lista',name:base[0].nome,desc:'UNIDADE: CENTRO'}];
  const rejected=planejar(base.map(x=>({...x})),cards);
  assert.equal(rejected.updates.length,0);
  assert.equal(rejected.skipped.length,1);
  const corrected=planejar([{...base[0],unidade:'NÃO IDENTIFICADA'}],cards);
  assert.equal(corrected.updates.length,1);
  assert.equal(corrected.updates[0].unit,'NÃO IDENTIFICADA');
});

test('Migração protege os tres cadastros e audita antes/depois sem apagar nenhuma obra',()=>{
  for(const id of [271,290,291])assert.match(migration,new RegExp('WHEN '+id+' THEN'));
  assert.match(migration,/FROM public\.convocacoes WHERE obra_id=item\.id/);
  assert.match(migration,/FROM public\.servicos_apontamento WHERE obra_id=item\.id::text/);
  assert.match(migration,/antes,depois,contexto/);
  assert.match(migration,/unidade='NÃO IDENTIFICADA',trello_unidade_manual=true/);
  assert.match(migration,/ADD CONSTRAINT aproar_obras_unidade_legivel_chk/);
  assert.doesNotMatch(migration,/\bDELETE\b/i);
  assert.doesNotMatch(migration,/\bDROP\b/i);
});
