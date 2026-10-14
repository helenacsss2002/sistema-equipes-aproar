// Resumo financeiro somente para exibição e exportação. Não altera os registros do Neon.
(function(root){
  'use strict';
  const amount=value=>Number.isFinite(Number(value))?Number(value):0;
  const round=value=>Math.round((value+Number.EPSILON)*100)/100;
  const fields=['finance','night','bonus','ajudaCusto'];
  function summarize(entries){
    const byPerson=new Map();
    for(const row of entries||[]){
      if(!row||['Falta','Atestado'].includes(row.i?.status))continue;
      const id=String(row.p?.id??row.i?.colaboradorId??'').trim();
      if(!id)continue;
      const values=fields.map(key=>Math.max(0,amount(row[key])));
      if(values.reduce((sum,value)=>sum+value,0)<=0.005)continue;
      if(!byPerson.has(id))byPerson.set(id,{
        id,nome:String(row.p?.nome||'Colaborador sem nome'),funcao:String(row.p?.funcao||''),
        supervisors:new Set(),units:new Set(),days:new Set(),finance:0,night:0,bonus:0,ajudaCusto:0,total:0
      });
      const item=byPerson.get(id);
      if(row.c?.supervisor)item.supervisors.add(String(row.c.supervisor));
      if(row.c?.unidade)item.units.add(String(row.c.unidade));
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
