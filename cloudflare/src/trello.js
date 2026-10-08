const URL_TRELLO='https://trello.com/b/TX8hGvmI.json';
const norm=x=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim().replace(/\s+/g,' ');
const UNITS=[
['MARACANAÚ',['APRL005','MARACANAU']],['PARTICULAR',['APARTAMENTO 701','PARTICULAR']],['SEBRAE',['SEBRAE']],['UNIFOR',['UNIFOR']],
['IDALYA E MATHEUS',['IDALYA E MATHEUS','IDALYA','MATHEUS']],['COLISEU',['COLISEU']],['BARRA DO CEARÁ',['BARRA DO CEARA']],
['MUSEU',['MUSEU']],['HORIZONTE',['HORIZONTE']],['ESCRITÓRIO',['ESCRITORIO']],['PARANGABA',['PARANGABA']],['CENTRO',['CENTRO']],
['FIEC',['CASA DA INDUSTRIA','FIEC','SESI DR','CONDOMINIO']]
];
const tokens=text=>{
 const t=norm(text),found=[];for(const [unit,names] of UNITS)for(const name of names){let i=t.indexOf(norm(name));while(i>=0){if(!/[A-Z0-9]/.test(t[i-1]||'')&&!/[A-Z0-9]/.test(t[i+norm(name).length]||''))found.push({unit,i});i=t.indexOf(norm(name),i+norm(name).length)}}
 return found.sort((a,b)=>a.i-b.i);
};
const unique=values=>[...new Set(values)];
function detect(text){
 const t=norm(text);if(!t)return null;
 for(const m of t.matchAll(/(?:UNIDADE(?:\s+DA\s+OBRA)?|UNID\.?|LOCAL|SITE)\s*(?:DA\s+OBRA\s*)?[:=\-]?\s*/g)){const ts=tokens(t.slice(m.index+m[0].length,m.index+m[0].length+160));if(ts.length)return (ts.find(x=>x.unit!=='FIEC')||ts[0]).unit;}
 for(const part of t.split('|')){const physical=tokens(part).filter(x=>x.unit!=='FIEC');if(physical.length)return physical[0].unit;}
 const all=unique(tokens(t).map(x=>x.unit)),physical=all.filter(x=>x!=='FIEC');if(physical.length===1)return physical[0];if(all.length===1&&all[0]==='FIEC')return 'FIEC';return null;
}
export const unidadeCard=card=>detect(card.name)||detect(card.desc)||'NÃO IDENTIFICADA';
const URL_TRELLO_API='https://api.trello.com/1/boards/TX8hGvmI?fields=id,name&lists=all&cards=all&card_fields=id,idList,name,desc,closed&list_fields=id,name,closed';
async function lerJSONTrello(url,fetcher){
 const ctrl=new AbortController();
 const timer=setTimeout(()=>ctrl.abort(),16000);
 try {
  let res;
  try{res=await fetcher(url,{signal:ctrl.signal,headers:{accept:'application/json'}});}
  catch(e){throw Error(e?.name==='AbortError'?'O Trello demorou mais de 16 segundos para responder.':'Não foi possível estabelecer a conexão entre a Cloudflare e o Trello.');}
  if(!res.ok)throw Error('O Trello retornou HTTP '+res.status+'.');
  const size=Number(res.headers.get('content-length')||0);
  if(size>14_000_000)throw Error('Quadro Trello muito grande.');
  const mime=res.headers.get('content-type')||'';
  if(/text\/html/i.test(mime))throw Error('O Trello retornou HTML em vez de JSON.');
  let body;
  try{body=await res.json();}catch{throw Error('O Trello respondeu, mas não enviou um JSON válido.');}
  if(!body||!Array.isArray(body.lists)||!Array.isArray(body.cards)||body.cards.length>10000)throw Error('O Trello respondeu com listas/cards inválidos ou excessivos.');
  return body;
 }finally{clearTimeout(timer);}
}
export async function consultarTrello(fetcher=fetch){
 // API oficial primeiro: endpoint de dados, em vez da pagina do quadro.
 // O endereco publico .json fica como contingencia quando o Trello permite seu acesso.
 const candidates=[{url:URL_TRELLO_API,source:'api.trello.com'},{url:URL_TRELLO,source:'trello.com'}];
 const errors=[];
 for(const c of candidates){
  try{
   const data=await lerJSONTrello(c.url,fetcher);
   return {
    origem:c.source,
    lists:data.lists.filter(x=>!x.closed).map(x=>({id:String(x.id),name:String(x.name||'')})),
    cards:data.cards.filter(x=>!x.closed).map(x=>({id:String(x.id),idList:String(x.idList),name:String(x.name||'').slice(0,480),desc:String(x.desc||'').slice(0,6000)}))
   };
  }catch(e){
   console.warn('APROAR Trello read fallback:',c.source,String(e?.message||'').slice(0,180));
   errors.push(c.source+': '+String(e?.message||'falha desconhecida'));
  }
 }
 throw Object.assign(Error('Falha ao consultar o Trello. '+errors.join(' | ').slice(0,480)),{status:502});
}

export function selecionar(board,filter={}){
 if(filter.cardId){const found=board.cards.filter(c=>c.id===filter.cardId);if(!found.length)throw Object.assign(Error('Card não encontrado.'),{status:404});return {cards:found,origem:'Card: '+found[0].name};}
 const list=filter.listId?board.lists.find(l=>l.id===filter.listId):board.lists.find(l=>norm(l.name)==='EM EXECUCAO')||board.lists.find(l=>norm(l.name).includes('EM EXECUCAO'));
 if(!list)throw Object.assign(Error('Lista EM EXECUÇÃO não encontrada.'),{status:404});
 return {cards:board.cards.filter(c=>c.idList===list.id&&c.name),origem:'Lista: '+list.name};
}
export function planejar(works,cards){
 const updates=[],inserts=[],skipped=[],unchanged=[];
 for(const card of cards){
  const name=card.name.trim(),unit=unidadeCard(card);
  let item=works.find(w=>w.trello_card_id===card.id);
  if(!item){
   let matches=works.filter(w=>!w.trello_card_id&&norm(w.nome)===norm(name)&&norm(w.unidade)===norm(unit));
   if(matches.length===1)item=matches[0];
   else if(matches.length>1){skipped.push({nome:name,motivo:'Obra legada ambígua'});continue;}
  }
  if(!item){
   const matches=works.filter(w=>!w.trello_card_id&&norm(w.nome)===norm(name));
   if(matches.length===1)item=matches[0];
   else if(matches.length>1){skipped.push({nome:name,motivo:'Nome duplicado sem identificação Trello'});continue;}
  }
  if(item){
   const target=item.trello_unidade_manual?item.unidade:unit;
   if(item.nome===name&&norm(item.unidade)===norm(target)&&item.trello_card_id===card.id&&item.trello_list_id===card.idList){unchanged.push(card);continue;}
   updates.push({card,id:String(item.id),unit:target});Object.assign(item,{nome:name,unidade:target,trello_card_id:card.id,trello_list_id:card.idList});
  }else{
   if(works.some(w=>norm(w.nome)===norm(name)&&w.trello_card_id&&w.trello_card_id!==card.id)){skipped.push({nome:name,motivo:'Nome associado a outro card'});continue;}
   inserts.push({card,unit});works.push({nome:name,unidade:unit,trello_card_id:card.id,trello_list_id:card.idList});
  }
 }
 return {updates,inserts,skipped,unchanged};
}

export async function sincronizarTrello(sql,filter={},fetcher=fetch){
 const board=await consultarTrello(fetcher),selected=selecionar(board,filter);
 if(selected.cards.length>450)throw Object.assign(Error('Lista extensa demais para uma gravação única.'),{status:413});
 const current=await sql`SELECT id,nome,unidade,trello_card_id,trello_list_id,trello_unidade_manual FROM obras`;
 const p=planejar(current.map(x=>({...x})),selected.cards);
 const sqls=[sql`SELECT pg_advisory_xact_lock(hashtext('aproar-trello-obras'))`,sql`LOCK TABLE obras IN SHARE ROW EXCLUSIVE MODE`];
 for(const x of p.updates)sqls.push(sql`UPDATE obras SET nome=${x.card.name},unidade=${x.unit},trello_card_id=${x.card.id},trello_list_id=${x.card.idList},trello_sync_em=NOW() WHERE id=${x.id}::bigint RETURNING id`);
 for(const x of p.inserts)sqls.push(sql`INSERT INTO obras(nome,unidade,trello_card_id,trello_list_id,trello_sync_em) VALUES (${x.card.name},${x.unit},${x.card.id},${x.card.idList},NOW()) ON CONFLICT DO NOTHING RETURNING id`);
 const report={origem:selected.origem,recebidos:selected.cards.length,atualizadas:p.updates.length,novas:0,jaExistentes:p.unchanged.length,ignoradas:p.skipped};
 sqls.push(sql`INSERT INTO trello_snapshot(snapshot_id,listas,cards,atualizado_em,sincronizado_obras_em,ultima_tentativa_obras_em,ultimo_resultado_obras) VALUES (1,${JSON.stringify(board.lists)}::jsonb,${JSON.stringify(board.cards)}::jsonb,NOW(),NOW(),NOW(),${JSON.stringify(report)}::jsonb) ON CONFLICT(snapshot_id) DO UPDATE SET listas=excluded.listas,cards=excluded.cards,atualizado_em=NOW(),sincronizado_obras_em=NOW(),ultima_tentativa_obras_em=NOW(),ultimo_resultado_obras=excluded.ultimo_resultado_obras`);
 const rows=await sql.transaction(sqls,{isolationLevel:'ReadCommitted'});
 report.novas=p.inserts.reduce((n,x,i)=>n+Number((rows[2+p.updates.length+i]||[]).length>0),0);
 p.inserts.forEach((x,i)=>{if(!(rows[2+p.updates.length+i]||[]).length)report.ignoradas.push({nome:x.card.name,motivo:'Conflito com obra existente; não alterada'});});
 return report;
}
