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
const editableAp=['status','extra','observacao','servicos','financeiro','noturno','acordo','ajudaCusto','tipoDiariaAvulso','valorExtraDisponivel'];
const avulsoDailyTypes=['Meia diária','Diária','Uma e meia diária','Duas diárias'];
const pendingAvulsoInvalid=(i,p)=>i.tipoDiariaAvulso!=null&&(!p||p.avulso!=='Sim'||!avulsoDailyTypes.includes(i.tipoDiariaAvulso));
const normServices=i=>(i?.servicos||[]).map(s=>({obraId:String(s.obraId||''),periodo:s.periodo||'Integral'}));
const apView=i=>({...field(i,editableAp),ajudaCusto:Number(i?.ajudaCusto)||0,servicos:normServices(i)});
const overlap=(a,b)=>a===b||(a==='Integral'&&['Manhã','Tarde'].includes(b))||(b==='Integral'&&['Manhã','Tarde'].includes(a));
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
 for(const o of base.obras)if(!works.has(o.id)){if(session.role!=='CONTROLADORIA')fail('Sem permissão para excluir obra.',403);if(db.raw.convocacoes.some(c=>String(c.obra_id)===o.id)||db.raw.servicos_apontamento.some(x=>String(x.obra_id)===o.id)||next.convocacoes.some(c=>String(c.obraId)===o.id)||next.apontamentos.some(a=>a.itens.some(i=>normServices(i).some(s=>s.obraId===o.id))))fail('Esta obra possui convocações ou apontamentos vinculados e deve ser preservada.');add('obras','delete',o.id);}
 const oldConvs=new Map(base.convocacoes.map(c=>[c.id,c])),rawConvs=new Map(db.raw.convocacoes.map(c=>[String(c.id),c]));
 const records=new Map(),byGroup=new Map(),rawAps=new Map(db.raw.apontamentos.map(a=>[String(a.convocacao_id),a])),oldApByConv=new Map(base.apontamentos.map(a=>[String(a.convocacaoId),a]));
 const rawServicesByConv=new Map();for(const service of db.raw.servicos_apontamento){const id=String(service.convocacao_id);if(!rawServicesByConv.has(id))rawServicesByConv.set(id,[]);rawServicesByConv.get(id).push(service);}
 for(const c of next.convocacoes){const old=oldConvs.get(String(c.id));date(c.dataServico);period(c.turno);if(!supervisors.includes(c.supervisor)&&!(session.role==='CONTROLADORIA'&&c.supervisor==='PAULO')&&(!old||c.supervisor!==old.supervisor))fail('Supervisor inválido.');if(!Array.isArray(c.colaboradores)||!c.colaboradores.length||new Set(c.colaboradores).size!==c.colaboradores.length)fail('Equipe vazia ou duplicada.');if(!old&&numericId(c.id))fail('Convocação nova com identificador inválido.');
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
 for(const old of base.convocacoes){if(records.has(old.id))continue;if(!own(session,old))fail('Sem permissão para excluir esta convocação.',403);for(const s of (rawServicesByConv.get(old.id)||[]))add('servicos_apontamento','delete',s.id);const ap=rawAps.get(old.id);if(ap)add('apontamentos','delete',ap.id);add('convocacoes','delete',old.id);}
 for(const {key,c,pid,old,changed} of records.values()){
  const raw=old?rawConvs.get(old.id):null,oldPoint=oldApByConv.get(String(old?.id))?.itens.find(i=>i.colaboradorId===pid),ap=pointed.get(key),pointChanged=ap&&(changed||!same(apView(oldPoint),apView(ap.i)));
  if(oldPoint&&!ap){if(!own(session,c))fail('Sem permissão para remover apontamento.',403);const row=rawAps.get(key);if(row)add('apontamentos','delete',row.id);for(const s of (rawServicesByConv.get(key)||[]))add('servicos_apontamento','delete',s.id);const {text,meta}=metadata(raw.observacao);delete meta.apontado_em;delete meta.apontado_por;delete meta.apontamento_atrasado;delete meta.valor_ajuda_custo;add('convocacoes','update',key,{status:'Presente (Integral)',valor_extra:0,custo_pago:0,valor_acordo:0,valor_adicional_noturno:0,custos_separados:false,observacao:text+(Object.keys(meta).length?' ||APROAR_META|| '+JSON.stringify(meta):'')});}
  if(pointChanged){if(session.role==='FINANCEIRO'){if(!oldPoint)fail('Financeiro não cria apontamentos.',403);const ignore=(i)=>{const x=apView(i);delete x.financeiro;delete x.noturno;delete x.acordo;delete x.ajudaCusto;return x;};if(!same(ignore(oldPoint),ignore(ap.i)))fail('Financeiro só altera pagamentos, adicionais, acordos e passagens/ajuda de custo.',403);}else if(!own(session,c))fail('Você só pode apontar sua própria equipe.',403);
   if(c.dataServico>isoToday(timestamp))fail('Apontamento não aceita data futura.');if(!['Presente (Integral)','Presente (Só Manhã)','Presente (Só Tarde)','Saída Antecipada','Falta','Atestado'].includes(ap.i.status))fail('Status inválido.');if(!['Valor específico',...Object.keys({'Não':0,'Meia diária':.5,'Diária':1,'Uma e meia diária':1.5,'Duas diárias':2})].includes(ap.i.extra))fail('Extra inválido.');
   for(const k of ['financeiro','noturno','acordo','ajudaCusto'])if(!finite(ap.i[k]??0))fail('Valor financeiro inválido.');if(!finite(ap.i.valorExtraDisponivel??0))fail('Valor da extra disponível inválido.');if(oldPoint&&Number(ap.i.ajudaCusto??0)!==Number(oldPoint.ajudaCusto??0)&&session.role!=='FINANCEIRO'&&(session.role!=='SUPERVISOR'||oldPoint.financeAdjusted))fail('Somente o Financeiro pode alterar passagens/ajuda de custo após o ajuste financeiro.',403);
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
  const i={...ap.i};if(pendingAvulsoInvalid(i,staff.get(pid)))fail('Escolha um tipo válido de diária para o avulso.');if(session.role==='SUPERVISOR'&&oldPoint?.financeAdjusted){for(const k of ['financeiro','noturno','acordo','ajudaCusto'])i[k]=oldPoint[k];}const p=staff.get(pid),isPresent=present(i.status),ss=normServices(i).filter(s=>s.obraId),hasSebrae=ss.some(s=>clean(works.get(s.obraId)?.unidade)==='SEBRAE'),financialAdjusted=session.role==='FINANCEIRO'||oldPoint?.financeAdjusted===true;
  const extra=isPresent?(i.extra==='Valor específico'?Number(oldPoint.valorExtraOriginal):money(Number(p.custo)*mult(i.extra))):0;
  const night=isPresent&&hasSebrae?(financialAdjusted||[50,90].includes(Number(i.noturno))?Number(i.noturno):Math.max(90,Number(i.noturno)||0)):0,finance=isPresent?Number(i.financeiro):0,bonus=isPresent?Number(i.acordo):0,ajudaCusto=isPresent?Number(i.ajudaCusto||0):0;
  const weight=!isPresent?0:p.avulso==='Sim'&&avulsoDailyTypes.includes(i.tipoDiariaAvulso)?mult(i.tipoDiariaAvulso):['Presente (Só Manhã)','Presente (Só Tarde)','Saída Antecipada'].includes(i.status)?.5:['Manhã','Tarde'].includes(c.turno)?.5:1;
  const oldRow=rawAps.get(key),pointTime=oldRow?.apontado_em||metadata(raw?.observacao).meta.apontado_em||timestamp,executor=oldRow?.apontado_por||metadata(raw?.observacao).meta.apontado_por||session.user;
  const values={status:i.status,valor_extra:extra,observacao:String(i.observacao||''),tipo_diaria:i.extra==='Valor específico'?(oldPoint?.tipoDiariaOriginal||'Não'):i.extra,custo_pago:money(finance),custo_pago_definido_financeiro:financialAdjusted,valor_acordo:money(bonus),valor_adicional_noturno:money(night),custo_encargos_base:money(Number(p.custo)*weight+extra),custos_separados:true,migracao_sebrae_noturno_v2:true};
  add('apontamentos',oldRow?'update':'insert',oldRow?.id||'ap:'+key,{...values,convocacao_id:key,data_servico:c.dataServico,colaborador_id:pid,engenheiro:c.supervisor,apontado_em:pointTime,apontado_por:executor,retroativo:Boolean(oldRow?.retroativo||ap.a.retroativo),atualizado_em:timestamp});
  const oldMeta=metadata(raw?.observacao).meta,first=ss[0],meta={...oldMeta,valor_extra_disponivel:money(Number(i.valorExtraDisponivel??0)),apontado_em:pointTime,apontado_por:executor,custos_separados:true,custo_pago:money(finance),valor_acordo:money(bonus),valor_adicional_noturno:money(night),valor_ajuda_custo:money(ajudaCusto),servico_a_definir:!first,tipo_diaria_avulso:p.avulso==='Sim'?(i.tipoDiariaAvulso||'Diária'):null,periodo_principal:first?.periodo||c.turno,servicos_adicionais:ss.slice(1).map(s=>({servico:works.get(s.obraId)?.nome,obra_id:s.obraId,periodo:s.periodo}))};
  add('convocacoes','update',key,{...values,obra_id:first?.obraId||work,observacao:'Turno: '+c.turno+(i.observacao?' | Obs: '+i.observacao:'')+' ||APROAR_META|| '+JSON.stringify(meta)});
  if(!same(normServices(oldPoint),ss)){
    const previousServices=(rawServicesByConv.get(key)||[]).slice().sort((a,b)=>Number(b.principal)-Number(a.principal)||Number(a.id)-Number(b.id));
    ss.forEach((service,index)=>{
      const work=works.get(service.obraId),previous=previousServices[index];
      const values={convocacao_id:key,obra_id:service.obraId,obra_nome_snapshot:work.nome,unidade_snapshot:work.unidade,periodo:service.periodo,principal:index===0,atualizado_em:timestamp};
      if(previous)add('servicos_apontamento','update',String(previous.id),values);
      else add('servicos_apontamento','insert',`service:${key}:${index}`,{...values,criado_em:timestamp});
    });
    // Any actual removal of historical services continues to be blocked by production permissions.
    for(const previous of previousServices.slice(ss.length))add('servicos_apontamento','delete',String(previous.id));
   }
 }
 // Extra-only records are stored separately in the existing tables, without a second ordinary attendance.
 if(Array.isArray(next.extras)){
  const oldExtras=new Map((base.extras||[]).map(x=>[String(x.id),x]));
  const allExtras=db.state.extras||[],incomingIds=new Set(),incomingCombos=new Set();
  const rawExtraConvs=new Map(db.raw.convocacoes.filter(c=>metadata(c.observacao).meta.extra_avulsa===true).map(c=>[String(c.id),c]));
  for(const x of next.extras){
   const id=String(x.id||'');if(!id)fail('Identificador do extra inválido.');
   if(incomingIds.has(id))fail('Extra duplicada.');incomingIds.add(id);
   const old=oldExtras.get(id);if(!old&&numericId(id))fail('Identificador novo de extra inválido.');
   if(session.role!=='SUPERVISOR'&&session.role!=='CONTROLADORIA')fail('Sem permissão para lançar extras.',403);
   if(old&&!own(session,{supervisor:old.supervisor}))fail('Você não pode alterar a extra de outro supervisor.',403);
   const personId=String(x.colaboradorId||''),p=staff.get(personId),work=works.get(String(x.obraId||''));
   if(!p)fail('Colaborador não encontrado para a extra.');
   const serviceDate=date(x.dataServico);
   if(serviceDate>isoToday(timestamp))fail('Extra não aceita data futura.');
   if(!work)fail('Escolha um serviço válido para a extra.');
   const supervisor=session.role==='SUPERVISOR'?session.user:required(String(x.supervisor||old?.supervisor||''),'Supervisor responsável');
   if(!supervisors.includes(supervisor))fail('Supervisor inválido para a extra.');
   // Supervisors can allocate an extra to another registered unit; the extra remains separate from ordinary attendance.
   const kind=String(x.extra||''),factor=mult(kind);
   if(!factor)fail('Selecione um tipo de extra válido.');
   const combo=serviceDate+'|'+personId+'|'+String(work.id);
   if(incomingCombos.has(combo))fail('Há duas extras para o mesmo colaborador, data e serviço.');incomingCombos.add(combo);
   const duplicate=allExtras.find(y=>String(y.id)!==id&&y.dataServico===serviceDate&&String(y.colaboradorId)===personId&&String(y.obraId)===String(work.id));
   if(duplicate)fail('Já existe uma extra para este colaborador, data e serviço.',409,{extraId:duplicate.id});
   const raw=old?rawExtraConvs.get(id):null,rawPoint=old?rawAps.get(id):null;
   const oldMeta=metadata(raw?.observacao).meta,obs=String(x.observacao||'').trim().slice(0,2000);
   const dayConv=(db.state.convocacoes||[]).find(c=>c.dataServico===serviceDate&&c.colaboradores?.includes(personId));
   const dayWorkId=String(dayConv?.obraId||old?.servicoDiaId||'');
   const amount=money(Number(x.valorExtraOriginal));
   const unchanged=old&&old.supervisor===supervisor&&old.dataServico===serviceDate&&String(old.colaboradorId)===personId&&String(old.obraId)===String(work.id)&&old.extra===kind&&String(old.observacao||'')===obs&&money(Number(old.valorExtraOriginal)||0)===amount;
   // Legacy records, including zero-valued extras, must remain readable and must not block unrelated saves.
   if(unchanged)continue;
   if(!finite(x.valorExtraOriginal)||amount<=0)fail('Informe o Valor da Extra em reais; o valor não é pré-definido.');
   const created=old?.criadoEm||oldMeta.extra_lancado_em||timestamp,creator=old?.executor||oldMeta.extra_lancado_por||session.user;
   const meta={...oldMeta,extra_avulsa:true,extra_obra_id:String(work.id),extra_unidade:work.unidade,extra_dia_obra_id:dayWorkId,extra_observacao:obs,extra_lancado_em:created,extra_lancado_por:creator,apontado_em:created,apontado_por:creator,custos_separados:true,servico_a_definir:false};
   const convData={obra_id:String(work.id),colaborador_id:personId,data:serviceDate,engenheiro:supervisor,turno:'Integral',status:'Extra',valor_extra:amount,custo_pago:0,valor_acordo:0,valor_adicional_noturno:0,custo_encargos_base:amount,custos_separados:true,observacao:'Extra independente ||APROAR_META|| '+JSON.stringify(meta)};
   const convKey=old?id:'extra:'+id;
   if(old)add('convocacoes','update',id,convData);
   else add('convocacoes','insert',convKey,{...convData,criado_em:timestamp,criado_por:session.user});
   const pointData={convocacao_id:convKey,data_servico:serviceDate,colaborador_id:personId,engenheiro:supervisor,status:'Extra',valor_extra:amount,observacao:obs,tipo_diaria:kind,custo_pago:0,custo_pago_definido_financeiro:false,valor_acordo:0,valor_adicional_noturno:0,custo_encargos_base:amount,custos_separados:true,migracao_sebrae_noturno_v2:true,apontado_em:created,apontado_por:creator,retroativo:serviceDate<isoToday(timestamp),atualizado_em:timestamp};
   add('apontamentos',rawPoint?'update':'insert',rawPoint?.id||'extra-ap:'+id,pointData);
   if(!old||String(old.obraId)!==String(work.id)||(rawServicesByConv.get(id)||[]).length===0){
    if(old)for(const service of (rawServicesByConv.get(id)||[]))add('servicos_apontamento','delete',service.id);
    add('servicos_apontamento','insert','extra-service:'+id,{convocacao_id:convKey,obra_id:String(work.id),obra_nome_snapshot:work.nome,unidade_snapshot:work.unidade,periodo:'Integral',principal:true,criado_em:timestamp,atualizado_em:timestamp});
   }
  }
  for(const old of base.extras||[]){
   if(incomingIds.has(String(old.id)))continue;
   if(!own(session,{supervisor:old.supervisor}))fail('Sem permissão para excluir esta extra.',403);
   for(const service of (rawServicesByConv.get(String(old.id))||[]))add('servicos_apontamento','delete',service.id);
   const row=rawAps.get(String(old.id));if(row)add('apontamentos','delete',row.id);
   add('convocacoes','delete',old.id);
  }
 }
 // Availability and recorded conflicts use existing production tables.
 const sync=(name,table,convert,allowed)=>{const old=new Map(base[name].map(x=>[String(x.id),x]));for(const x of next[name]){const previous=old.get(String(x.id));if(previous&&same(previous,x))continue;if(!allowed(x,previous))fail('Sem permissão para alterar '+name+'.',403);if(!previous&&numericId(x.id))fail('Identificador novo inválido.');add(table,previous?'update':'insert',x.id,convert(x,previous));}for(const x of base[name])if(!next[name].some(y=>String(y.id)===String(x.id))){if(session.role!=='CONTROLADORIA')fail('Sem permissão para excluir registro.',403);add(table,'delete',x.id);}};
 sync('indisponibilidades','indisponibilidades',x=>{if(!staff.has(String(x.colaboradorId)))fail('Colaborador inválido.');date(x.inicio);date(x.fim);if(x.fim<x.inicio)fail('Período inválido.');return {colaborador_id:String(x.colaboradorId),colaborador_nome_snapshot:staff.get(String(x.colaboradorId)).nome,motivo:required(x.motivo,'Motivo'),inicio:x.inicio,fim:x.fim,observacao:String(x.obs||x.observacao||''),criado_por:session.user,ativo:true};},()=>session.role==='CONTROLADORIA');
 sync('conflitosTentados','conflitos_convocacao',(x,previous)=>previous?{resolvido:Boolean(x.resolvido),resolvido_em:x.resolvido?timestamp:null,resolvido_por:x.resolvido?session.user:null}:{colaborador_id:String(x.colaboradorId),colaborador_nome_snapshot:staff.get(String(x.colaboradorId))?.nome||'',data:date(x.dataServico),convocacao_existente_id:String(x.convocacaoExistenteId||''),engenheiro_original:required(x.supervisorExistente,'Supervisor original'),turno_original:period(x.turnoExistente),unidade_original:String(x.unidadeExistente||''),engenheiro_tentativa:session.role==='SUPERVISOR'?session.user:required(x.supervisor,'Supervisor'),turno_tentativa:period(x.turno),unidade_tentativa:String(x.unidade||''),criado_em:timestamp,resolvido:false,contexto:{origem:'aproar-web'}},(x,previous)=>previous?session.role==='CONTROLADORIA':['CONTROLADORIA','SUPERVISOR'].includes(session.role));
 if(session.role!=='CONTROLADORIA'){
  for(const k of ['units','teamsConfig','unitOwners','teamsAutomation','teamsMessage','teamsHistory'])if(!same(next[k]??base[k],base[k]))fail('Sem permissão para alterar configurações.',403);
 }else{
  for(const [s,x] of Object.entries(next.teamsConfig||{})){
   const previous=base.teamsConfig?.[s];
   // Old Teams recipients can still include supervisors no longer active in APROAR.
   // Preserve untouched legacy rows; only reject new or edited unsupported supervisors.
   if(!supervisors.includes(s)){if(!previous||!same(x,previous))fail('Supervisor inválido.');continue;}
   if(!same(x,previous)){
     if(x.email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email))fail('E-mail inválido.');
     add('engenheiros_teams','update',s,{email_teams:x.email||'',ativo:x.ativo!==false});
   }
  }
  const units=next.units??base.units;
   // Legacy work records can contain malformed unit labels (e.g. a Trello URL).
    // Preserve these exact already-loaded labels so unrelated Controladoria edits
    // (new works, unit removal, deleting unlinked works) are not blocked.
    // New or changed unit labels must still respect the 200-character limit.
    const originalUnits=new Set(base.units);
    if(!Array.isArray(units)||units.length>500||units.some(u=>typeof u!=='string'||!u.trim()||(u.length>200&&!originalUnits.has(u)))||new Set(units.map(clean)).size!==units.length||next.obras.some(o=>!units.includes(o.unidade)))fail('Cadastro de unidades inválido.');
   for(const removed of base.units.filter(u=>!units.includes(u))){
     if(base.obras.some(o=>o.unidade===removed)||db.state.convocacoes.some(c=>c.unidade===removed)||db.raw.servicos_apontamento.some(s=>s.unidade_snapshot===removed)||db.state.conflitosTentados.some(c=>c.unidade===removed||c.unidadeExistente===removed))fail('Unidade possui obras ou histórico vinculado. Remova os vínculos antes de excluir.');
   }const history=(next.teamsHistory||[]).filter(x=>!numericId(x.id));
    // Derived units from legacy works are visible in the UI but should not
    // become permanent unit registrations just because another edit was saved.
    const previousConfig=db.raw.settings[0]?.data||{};
    const persistedUnits=units.filter(u=>u.length<=200||(Array.isArray(previousConfig.units)&&previousConfig.units.includes(u)));
    const config={units:persistedUnits,unitOwners:next.unitOwners||{},teamsAutomation:!!next.teamsAutomation,teamsMessage:next.teamsMessage||'',teamsHistory:history};if(!same(config,previousConfig))add('aproar_web_settings','update',1,{data:config});
 }
 // Always generate a server audit record for actual changes, rather than trusting browser audit text.
 if(ops.length)add('auditoria','insert','audit:'+crypto.randomUUID(),{entidade:'aproar-web',entidade_id:null,acao:'SALVAR',usuario:session.user,ocorrido_em:timestamp,contexto:{perfil:session.role,operacoes:ops.map(o=>({tabela:o.table,acao:o.action,id:o.id}))}});
 if(ops.length>10000)fail('Alteração muito grande. Divida a operação em lotes.');return ops;
}
