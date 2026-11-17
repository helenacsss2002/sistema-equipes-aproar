// Resumo financeiro somente para exibição e exportação. Não altera os registros do Neon.
(function(root){
  'use strict';
  const amount=value=>Number.isFinite(Number(value))?Number(value):0;
  const round=value=>Math.round((value+Number.EPSILON)*100)/100;
  const fields=['extra','finance','night','bonus','ajudaCusto'];
  const normalized=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().replace(/\s+/g,' ').toUpperCase();
  function identityKey(row){
    const id=String(row.p?.id??row.i?.colaboradorId??'').trim();
    if(!id)return '';
    // Avulsos digitados manualmente recebem um ID novo em cada convocação.
    // Nome + função + supervisor unem as diárias do mesmo trabalhador;
    // colaboradores cadastrados continuam sempre identificados pelo ID real.
    if(row.p?.avulso==='Sim'&&normalized(row.p?.nome))
      return 'avulso|'+JSON.stringify([normalized(row.p.nome),normalized(row.p.funcao),normalized(row.c?.supervisor)]);
    return 'cadastro|'+id;
  }
  function summarize(entries){
    const source=Array.isArray(entries)?entries:[];
    // Homônimos com IDs diferentes no mesmo dia exigem revisão: não fundir.
    const seenByDate=new Map(),ambiguous=new Set();
    for(const row of source){
      if(!row)continue;
      const key=identityKey(row),date=row.c?.dataServico;
      if(!key.startsWith('avulso|')||!date)continue;
      const stamp=key+'|'+date,id=String(row.p?.id??row.i?.colaboradorId??'');
      if(seenByDate.has(stamp)&&seenByDate.get(stamp)!==id)ambiguous.add(key);
      else seenByDate.set(stamp,id);
    }
    const byPerson=new Map();
    for(const row of entries||[]){
      if(!row||['Falta','Atestado'].includes(row.i?.status))continue;
      const id=String(row.p?.id??row.i?.colaboradorId??'').trim();
      if(!id)continue;
      const values=fields.map(key=>Math.max(0,amount(row[key])));
      if(values.reduce((sum,value)=>sum+value,0)<=0.005)continue;
      const group=identityKey(row),key=ambiguous.has(group)?'registro|'+id:group;
      if(!key)continue;
      if(!byPerson.has(key))byPerson.set(key,{
        id:key,nome:String(row.p?.nome||'Colaborador sem nome'),funcao:String(row.p?.funcao||''),
        supervisors:new Set(),units:new Set(),days:new Set(),extra:0,finance:0,night:0,bonus:0,ajudaCusto:0,total:0
      });
      const item=byPerson.get(key);
      if(row.c?.supervisor)item.supervisors.add(String(row.c.supervisor));
      if(row.units&&typeof row.units[Symbol.iterator]==='function'){
        for(const unit of row.units)if(unit)item.units.add(String(unit));
      }else if(row.c?.unidade)item.units.add(String(row.c.unidade));
      if(row.c?.dataServico)item.days.add(String(row.c.dataServico));
      fields.forEach((key,index)=>{item[key]+=values[index];});
    }
    return [...byPerson.values()].map(item=>{
      fields.forEach(key=>{item[key]=round(item[key]);});
      item.total=round(fields.reduce((sum,key)=>sum+item[key],0));
      return {...item,dias:item.days.size,
        supervisores:[...item.supervisors].sort((a,b)=>a.localeCompare(b,'pt-BR')).join(', '),
        unidades:[...item.units].sort((a,b)=>a.localeCompare(b,'pt-BR')).join(', '),
        supervisors:undefined,units:undefined,days:undefined
      };
    }).sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR',{sensitivity:'base'})||a.id.localeCompare(b.id));
  }
  root.APROARFinanceConsolidado={summarize};
})(globalThis);
