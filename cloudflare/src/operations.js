import {metadata} from './neon-adapter.js';
import {supervisors,visibleState} from './data.js';
const numericId=v=>/^\d+$/.test(String(v));
const clean=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
const money=v=>Math.round(Number(v)*100)/100;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const field=(o,keys)=>Object.fromEntries(keys.map(k=>[k,o?.[k]??null]));
const fail=(message,status=400,details)=>{throw Object.assign(Error(message),{status,details});};
const finite=v=>Number.isFinite(Number(v))&&Number(v)>=0&&Number(v)<=1e7;
const required=(s,label)=>{if(typeof s!=='string'||!s.trim()||s.length>2000)fail(label+' inválido.');return s.trim();};
const date=d=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(d)||new Date(d+'T12:00:00Z').toISOString().slice(0,10)!==d)fail('Data inválida.');return d;};
const period=p=>{if(!['Manhã','Tarde','Noite','Integral'].includes(p))fail('Escolha um turno válido.');return p;};
const present=s=>!['Falta','Atestado'].includes(s);
const mult=e=>({'Não':0,'Meia diária':.5,'Diária':1,'Uma e meia diária':1.5,'Duas diárias':2}[e]);
const editableAp=['status','extra','observacao','servicos','financeiro','noturno','acordo'];
const normServices=i=>(i?.servicos||[]).map(s=>({obraId:String(s.obraId||''),periodo:s.periodo||'Integral'}));
const apView=i=>({...field(i,editableAp),servicos:normServices(i)});
const overlap=(a,b)=>a==='Integral'||b==='Integral'||a===b;
const isoToday=t=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Fortaleza',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(t));
const own=(s,c)=>s.role==='CONTROLADORIA'||s.role==='SUPERVISOR'&&c.supervisor===s.user;
export function buildOperations(db,next,session,timestamp=new Date().toISOString()){
 if(session.role==='VISUALIZAR')fail('Este perfil permite somente visualização.',403);
 const base=visibleState(db,session),ops=[];const add=(table,action,id,data)=>ops.push({table,action,id:String(id),...(data?{data}: {})});
 for(const key of ['colaboradores','obras','convocacoes','apontamentos','indisponibilidades','conflitosTentados'])if(!Array.isArray(next[key]))fail('Dados incompletos. Atualize a página.');
 const staff=new Map(next.colaboradores.map(p=>[String(p.id),p])),oldStaff=new Map(base.colaboradores.map(p=>[p.id,p])),works=new Map(next.obras.map(o=>[String(o.id),o]));
 if(staff.size!==next.colaboradores.length||works.size!==next.obras.length)fail('Há identificadores repetidos.');
 const staffFields=['nome','funcao','custo','moradia','inativo','categoria','avulso'];
 for(const p of next.colaboradores){const old=oldStaff.get(String(p.id));if(old&&same(field(old,staffFields),field(p,staffFields)))continue;if(session.role!=='CONTROLADORIA'&&(old||session.role!=='SUPERVISOR'||p.avulso!=='Sim'))fail('Sem permissão para alterar colaboradores.',403);if(!old&&numericId(p.id))fail('Cadastro novo com identificador inválido.');if(!finite(p.custo)||Number(p.custo)<=0)fail('Custo diário inválido.');add('colaboradores',old?'update':'insert',p.id,{nome:required(p.nome,'Nome'),funcao:required(p.funcao,'Função'),valor_diaria:money(p.custo),local_moradia:String(p.moradia||''),ativo:!p.inativo,categoria_diaria:String(p.categoria||''),avulso:p.avulso==='Sim'?'Sim':'Não'});}
 if([...oldStaff.keys()].some(k=>!staff.has(k)))fail('Use a inativação para preservar o histórico do colaborador.');
 const oldWorks=new Map(base.obras.map(o=>[o.id,o]));for(const o of next.obras){const old=oldWorks.get(String(o.id));if(old&&same(field(old,['nome','unidade']),field(o,['nome','unidade'])))continue;if(session.role!=='CONTROLADORIA')fail('Sem permissão para alterar obras.',403);if(!old&&numericId(o.id))fail('Obra nova com identificador inválido.');add('obras',old?'update':'insert',o.id,{nome:required(o.nome,'Obra'),unidade:required(o.unidade,'Unidade')});}
 for(const o of base.obras)if(!works.has(o.id)){if(session.role!=='CONTROLADORIA')fail('Sem permissão para excluir obra.',403);if(next.convocacoes.some(c=>String(c.obraId)===o.id)||next.apontamentos.some(a=>a.itens.some(i=>normServices(i).some(s=>s.obraId===o.id))))fail('Esta obra possui registros e deve ser preservada.');add('obras','delete',o.id);}
 const oldConvs=new Map(base.convocacoes.map(c=>[c.id,c])),rawConvs=new Map(db.raw.convocacoes.map(c=>[String(c.id),c]));
 const records=new Map(),byGroup=new Map(),rawAps=new Map(db.raw.apontamentos.map(a=>[String(a.convocacao_id),a]));
 for(const c of next.convocacoes){date(c.dataServico);period(c.turno);if(!supervisors.includes(c.supervisor))fail('Supervisor inválido.');if(!Array.isArray(c.colaboradores)||!c.colaboradores.length||new Set(c.colaboradores).size!==c.colaboradores.length)fail('Equipe vazia ou duplicada.');const old=oldConvs.get(String(c.id));if(!old&&numericId(c.id))fail('Convocação nova com identificador inválido.');
  for(const pidValue of c.colaboradores){const pid=String(pidValue),person=staff.get(pid);if(!person)fail('Colaborador não encontrado.');const key=old?.colaboradores.includes(pid)?old.id:`cv:${c.id}:${pid}`,scheduling=field(c,['supervisor','dataServico','unidade','turno']),changed=!old||!old.colaboradores.includes(pid)||!same(scheduling,field(old,['supervisor','dataServico','unidade','turno']));
   if(changed&&!own(session,c))fail('Você só pode convocar sua própria equipe.',403);if(changed&&old&&!own(session,old))fail('Você não pode alterar a equipe de outro supervisor.',403);if(changed&&session.role==='SUPERVISOR'&&person.inativo)fail('Colaborador inativo.');
   if(records.has(key))fail('Convocação repetida.');records.set(key,{key,c,pid,old:old?.colaboradores.includes(pid)?old:null,changed});byGroup.set(String(c.id)+'|'+pid,key);
  }
 }
 const pointed=new Map();for(const a of next.apontamentos){if(!Array.isArray(a.itens)||!a.itens.length)fail('Apontamento vazio.');for(const i of a.itens){const key=byGroup.get(String(a.convocacaoId)+'|'+String(i.colaboradorId));if(!key)fail('Apontamento sem convocação correspondente.');if(pointed.has(key))fail('Apontamento duplicado.');pointed.set(key,{a,i});}}
 // Only changes to scheduling are checked; existing historic inconsistencies do not block unrelated edits.
 for(const record of records.values()){const {key,c,pid,changed}=record;if(!changed)continue;
  for(const other of records.values())if(other.key!==key&&other.pid===pid&&other.c.dataServico===c.dataServico&&overlap(other.c.turno,c.turno))fail(`Conflito: ${staff.get(pid).nome} já está convocado por ${other.c.supervisor}, em ${other.c.unidade}, no turno ${other.c.turno}.`,409,{colaboradorId:pid,supervisor:other.c.supervisor,unidade:other.c.unidade,turno:other.c.turno});
  const blocked=db.state.indisponibilidades.find(x=>x.colaboradorId===pid&&x.inicio<=c.dataServico&&x.fim>=c.dataServico);if(blocked&&present(pointed.get(key)?.i.status||'Presente (Integral)'))fail(`${staff.get(pid).nome} está indisponível: ${blocked.motivo}.`,409);
 }
 // Remove dependents first, explicitly and atomically.
 for(const old of base.convocacoes){if(records.has(old.id))continue;if(!own(session,old))fail('Sem permissão para excluir esta convocação.',403);for(const s of db.raw.servicos_apontamento.filter(x=>String(x.convocacao_id)===old.id))add('servicos_apontamento','delete',s.id);const ap=rawAps.get(old.id);if(ap)add('apontamentos','delete',ap.id);add('convocacoes','delete',old.id);}
 for(const {key,c,pid,old,changed} of records.values()){
  const raw=old?rawConvs.get(old.id):null,oldPoint=base.apontamentos.find(a=>a.convocacaoId===old?.id)?.itens.find(i=>i.colaboradorId===pid),ap=pointed.get(key),pointChanged=ap&&(changed||!same(apView(oldPoint),apView(ap.i)));
  if(oldPoint&&!ap){if(!own(session,c))fail('Sem permissão para remover apontamento.',403);const row=rawAps.get(key);if(row)add('apontamentos','delete',row.id);for(const s of db.raw.servicos_apontamento.filter(x=>String(x.convocacao_id)===key))add('servicos_apontamento','delete',s.id);const {text,meta}=metadata(raw.observacao);delete meta.apontado_em;delete meta.apontado_por;delete meta.apontamento_atrasado;add('convocacoes','update',key,{status:'Presente (Integral)',valor_extra:0,custo_pago:0,valor_acordo:0,valor_adicional_noturno:0,custos_separados:false,observacao:text+(Object.keys(meta).length?' ||APROAR_META|| '+JSON.stringify(meta):'')});}
  if(pointChanged){if(session.role==='FINANCEIRO'){if(!oldPoint)fail('Financeiro não cria apontamentos.',403);const ignore=(i)=>{const x=apView(i);delete x.financeiro;delete x.noturno;delete x.acordo;return x;};if(!same(ignore(oldPoint),ignore(ap.i)))fail('Financeiro só altera pagamentos, adicionais e acordos.',403);}else if(!own(session,c))fail('Você só pode apontar sua própria equipe.',403);
   if(c.dataServico>isoToday(timestamp))fail('Apontamento não aceita data futura.');if(!['Presente (Integral)','Presente (Só Manhã)','Presente (Só Tarde)','Saída Antecipada','Falta','Atestado'].includes(ap.i.status))fail('Status inválido.');if(!['Valor específico',...Object.keys({'Não':0,'Meia diária':.5,'Diária':1,'Uma e meia diária':1.5,'Duas diárias':2})].includes(ap.i.extra))fail('Extra inválido.');
   for(const k of ['financeiro','noturno','acordo'])if(!finite(ap.i[k]??0))fail('Valor financeiro inválido.');
   const ss=normServices(ap.i);if(present(ap.i.status)&&(!ss.length||ss.some(s=>!works.has(s.obraId)||works.get(s.obraId).unidade!==c.unidade)))fail('Defina os serviços do colaborador na unidade convocada.');for(const s of ss){if(!s.obraId)continue;period(s.periodo);}if(new Set(ss.map(s=>s.obraId+'|'+s.periodo)).size!==ss.length)fail('Serviço repetido no mesmo período.');
   if(ap.i.extra==='Valor específico'&&(!oldPoint||oldPoint.extra!=='Valor específico'))fail('Extra específico deve existir no registro original.');
  }
  // Convocations always retain a valid work FK for compatibility with Streamlit; metadata marks an unassigned service.
  const work=(c.obraId&&works.has(String(c.obraId))?String(c.obraId):[...works.values()].find(o=>o.unidade===c.unidade)?.id);if(!work)fail('Cadastre ao menos uma obra para esta unidade.');
  if(!raw||changed||String(old?.obraId||'')!==String(c.obraId||'')){
   if(raw&&!own(session,c)&&session.role!=='FINANCEIRO')fail('Sem permissão para alterar convocação.',403);if(raw&&session.role==='FINANCEIRO')fail('Financeiro não altera convocações.',403);
   const {meta}=metadata(raw?.observacao),created=raw?.criado_em||meta.convocado_em||timestamp;Object.assign(meta,{convocado_em:created,convocado_por:raw?.criado_por||meta.convocado_por||session.user,servico_a_definir:!c.obraId});
   const data={obra_id:work,colaborador_id:pid,data:c.dataServico,engenheiro:c.supervisor,turno:c.turno,observacao:'Turno: '+c.turno+' ||APROAR_META|| '+JSON.stringify(meta)};if(!raw)Object.assign(data,{status:'Presente (Integral)',valor_extra:0,criado_em:timestamp,criado_por:session.user});add('convocacoes',raw?'update':'insert',key,data);
  }
  if(!pointChanged)continue;
  const i={...ap.i};if(session.role==='SUPERVISOR'&&oldPoint?.financeAdjusted){for(const k of ['financeiro','noturno','acordo'])i[k]=oldPoint[k];}const p=staff.get(pid),isPresent=present(i.status),ss=normServices(i).filter(s=>s.obraId),hasSebrae=ss.some(s=>clean(works.get(s.obraId)?.unidade)==='SEBRAE'),financialAdjusted=session.role==='FINANCEIRO'||oldPoint?.financeAdjusted===true;
  const extra=isPresent?(i.extra==='Valor específico'?Number(oldPoint.valorExtraOriginal):money(Number(p.custo)*mult(i.extra))):0;
  const night=isPresent&&hasSebrae?(financialAdjusted?Number(i.noturno):Math.max(90,Number(i.noturno))):0,finance=isPresent?Number(i.financeiro):0,bonus=isPresent?Number(i.acordo):0;
  const weight=!isPresent?0:['Presente (Só Manhã)','Presente (Só Tarde)','Saída Antecipada'].includes(i.status)?.5:['Manhã','Tarde'].includes(c.turno)?.5:1;
  const oldRow=rawAps.get(key),pointTime=oldRow?.apontado_em||metadata(raw?.observacao).meta.apontado_em||timestamp,executor=oldRow?.apontado_por||metadata(raw?.observacao).meta.apontado_por||session.user;
  const values={status:i.status,valor_extra:extra,observacao:String(i.observacao||''),tipo_diaria:i.extra==='Valor específico'?(oldPoint?.tipoDiariaOriginal||'Não'):i.extra,custo_pago:money(finance),custo_pago_definido_financeiro:financialAdjusted,valor_acordo:money(bonus),valor_adicional_noturno:money(night),custo_encargos_base:money(Number(p.custo)*weight+extra),custos_separados:true,migracao_sebrae_noturno_v2:true};
  add('apontamentos',oldRow?'update':'insert',oldRow?.id||'ap:'+key,{...values,convocacao_id:key,data_servico:c.dataServico,colaborador_id:pid,engenheiro:c.supervisor,apontado_em:pointTime,apontado_por:executor,retroativo:Boolean(oldRow?.retroativo||ap.a.retroativo),atualizado_em:timestamp});
  const oldMeta=metadata(raw?.observacao).meta,first=ss[0],meta={...oldMeta,apontado_em:pointTime,apontado_por:executor,custos_separados:true,custo_pago:money(finance),valor_acordo:money(bonus),valor_adicional_noturno:money(night),servico_a_definir:!first,periodo_principal:first?.periodo||c.turno,servicos_adicionais:ss.slice(1).map(s=>({servico:works.get(s.obraId)?.nome,obra_id:s.obraId,periodo:s.periodo}))};
  add('convocacoes','update',key,{...values,obra_id:first?.obraId||work,observacao:'Turno: '+c.turno+(i.observacao?' | Obs: '+i.observacao:'')+' ||APROAR_META|| '+JSON.stringify(meta)});
  if(!same(normServices(oldPoint),ss)){for(const s of db.raw.servicos_apontamento.filter(x=>String(x.convocacao_id)===key))add('servicos_apontamento','delete',s.id);ss.forEach((s,index)=>add('servicos_apontamento','insert',`service:${key}:${index}`,{convocacao_id:key,obra_id:s.obraId,obra_nome_snapshot:works.get(s.obraId).nome,unidade_snapshot:works.get(s.obraId).unidade,periodo:s.periodo,principal:index===0,criado_em:timestamp,atualizado_em:timestamp}));}
 }
 // Availability and recorded conflicts use existing production tables.
 const sync=(name,table,convert,allowed)=>{const old=new Map(base[name].map(x=>[String(x.id),x]));for(const x of next[name]){const previous=old.get(String(x.id));if(previous&&same(previous,x))continue;if(!allowed(x,previous))fail('Sem permissão para alterar '+name+'.',403);if(!previous&&numericId(x.id))fail('Identificador novo inválido.');add(table,previous?'update':'insert',x.id,convert(x,previous));}for(const x of base[name])if(!next[name].some(y=>String(y.id)===String(x.id))){if(session.role!=='CONTROLADORIA')fail('Sem permissão para excluir registro.',403);add(table,'delete',x.id);}};
 sync('indisponibilidades','indisponibilidades',x=>{if(!staff.has(String(x.colaboradorId)))fail('Colaborador inválido.');date(x.inicio);date(x.fim);if(x.fim<x.inicio)fail('Período inválido.');return {colaborador_id:String(x.colaboradorId),colaborador_nome_snapshot:staff.get(String(x.colaboradorId)).nome,motivo:required(x.motivo,'Motivo'),inicio:x.inicio,fim:x.fim,observacao:String(x.obs||x.observacao||''),criado_por:session.user,ativo:true};},()=>session.role==='CONTROLADORIA');
 sync('conflitosTentados','conflitos_convocacao',(x,previous)=>previous?{resolvido:Boolean(x.resolvido),resolvido_em:x.resolvido?timestamp:null,resolvido_por:x.resolvido?session.user:null}:{colaborador_id:String(x.colaboradorId),colaborador_nome_snapshot:staff.get(String(x.colaboradorId))?.nome||'',data:date(x.dataServico),convocacao_existente_id:String(x.convocacaoExistenteId||''),engenheiro_original:required(x.supervisorExistente,'Supervisor original'),turno_original:period(x.turnoExistente),unidade_original:String(x.unidadeExistente||''),engenheiro_tentativa:session.role==='SUPERVISOR'?session.user:required(x.supervisor,'Supervisor'),turno_tentativa:period(x.turno),unidade_tentativa:String(x.unidade||''),criado_em:timestamp,resolvido:false,contexto:{origem:'aproar-web'}},(x,previous)=>previous?session.role==='CONTROLADORIA':['CONTROLADORIA','SUPERVISOR'].includes(session.role));
 if(session.role!=='CONTROLADORIA'){
  for(const k of ['teamsConfig','unitOwners','teamsAutomation','teamsMessage','teamsHistory'])if(!same(next[k]??base[k],base[k]))fail('Sem permissão para alterar configurações.',403);
 }else{
  for(const [s,x] of Object.entries(next.teamsConfig||{})){if(!supervisors.includes(s))fail('Supervisor inválido.');if(x.email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email))fail('E-mail inválido.');if(!same(x,base.teamsConfig?.[s]))add('engenheiros_teams','update',s,{email_teams:x.email||'',ativo:x.ativo!==false});}
  const history=(next.teamsHistory||[]).filter(x=>!numericId(x.id));const config={unitOwners:next.unitOwners||{},teamsAutomation:!!next.teamsAutomation,teamsMessage:next.teamsMessage||'',teamsHistory:history};if(!same(config,db.raw.settings[0]?.data||{}))add('aproar_web_settings','update',1,{data:config});
 }
 // Always generate a server audit record for actual changes, rather than trusting browser audit text.
 if(ops.length)add('auditoria','insert','audit:'+crypto.randomUUID(),{entidade:'aproar-web',entidade_id:null,acao:'SALVAR',usuario:session.user,ocorrido_em:timestamp,contexto:{perfil:session.role,operacoes:ops.map(o=>({tabela:o.table,acao:o.action,id:o.id}))}});
 if(ops.length>10000)fail('Alteração muito grande. Divida a operação em lotes.');return ops;
}
