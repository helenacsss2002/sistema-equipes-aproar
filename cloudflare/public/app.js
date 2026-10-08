
(() => {
  const STORAGE_KEY = 'aproar_v1_demo_data';
  const PROFILE_KEY = 'aproar_v2_perfil';
  const SESSION_KEY = 'aproar_v1_supervisor';

  const SUPERVISORES = ['EDUARDO', 'FELIPE', 'GABRIEL', 'JOEL', 'NETO', 'SOARES', 'VICTOR'];
  const COLABORADORES=[];
  const OBRAS=[];

  const STATUS_OPTIONS = [
    'Presente (Integral)',
    'Presente (Só Manhã)',
    'Presente (Só Tarde)',
    'Falta',
    'Atestado',
    'Saída Antecipada',
  ];

  const EXTRA_OPTIONS = ['Não', 'Meia diária', 'Diária', 'Uma e meia diária', 'Duas diárias'];

  const seedData=()=>({version:2,colaboradores:[],obras:[],convocacoes:[],apontamentos:[],indisponibilidades:[],conflitosTentados:[],auditoria:[]});

  let state = loadData();
  if(state.obras) OBRAS.splice(0,OBRAS.length,...state.obras);
  if(state.colaboradores) COLABORADORES.splice(0,COLABORADORES.length,...state.colaboradores);
  state.indisponibilidades ||= []; state.auditoria ||= [];
  delete state.servicosPrevistos;
  
  
  
  let perfilAtual = '';
  let supervisorAtual = '';
  let loginPerfilSelecionado = 'CONTROLADORIA';
  let portalDate=isoToday();
  let portalUnit='Todas';
  let viewAtual = 'inicio';
  let apontamentoTab = 'normal';
  let retroDateSelected='';

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function loadData(){return seedData();}
  function now() { return new Date(); }
  function uid(prefix) { return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2,7)}`; }

  function dateLocal(iso) {
    const [y,m,d] = String(iso).split('-').map(Number);
    return new Date(y, (m || 1) - 1, d || 1, 12, 0, 0, 0);
  }

  function formatDate(iso) {
    if (!iso) return '-';
    const [y,m,d] = String(iso).slice(0,10).split('-');
    return `${d}/${m}/${y}`;
  }

  function formatDateTime(v) {
    if (!v) return '-';
    const d = new Date(v);
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short', timeZone:'America/Fortaleza' }).format(d);
  }

  function isoToday(){return brazilDate(now());}

  function isWeekend(iso) {
    const w = dateLocal(iso).getDay();
    return w === 0 || w === 6;
  }

  function previousBusinessDay(iso) {
    const d = dateLocal(iso);
    do { d.setDate(d.getDate()-1); } while ([0,6].includes(d.getDay()));
    return d;
  }

  function nextBusinessDay(iso) {
    const d = dateLocal(iso);
    do { d.setDate(d.getDate()+1); } while ([0,6].includes(d.getDay()));
    return d;
  }

  function atTime(d, h, m) {
    const x = new Date(d);
    x.setHours(h,m,0,0);
    return x;
  }

  function deadlineConvocacao(conv){if(isWeekend(conv.dataServico))return null;return brazilTime(calendarISO(previousBusinessDay(conv.dataServico)),16);}

  function convocacaoAtrasada(conv){
    if(isWeekend(conv.dataServico))return false;const registered=brazilDate(new Date(conv.criadoEm));if(isWeekend(registered))return false;const p=brazilParts(new Date(conv.criadoEm));return Number(p.hour)>=16&&conv.dataServico===calendarISO(nextBusinessDay(registered));
  }
  function deadlineApontamento(date){return brazilTime(calendarISO(nextBusinessDay(date)),9,30);}
  function apontamentoAtrasado(ap){return !isWeekend(ap.dataServico)&&new Date(ap.apontadoEm)>=deadlineApontamento(ap.dataServico);}

  function convocacoesSupervisor() {
    return state.convocacoes.filter(c => c.supervisor === supervisorAtual || perfilAtual==='CONTROLADORIA');
  }

  function apontamentosSupervisor() {
    return state.apontamentos.filter(a => a.supervisor === supervisorAtual || perfilAtual==='CONTROLADORIA');
  }

  function apForConv(convId) {
    return state.apontamentos.find(a => a.convocacaoId === convId);
  }

  function obraById(id) { return OBRAS.find(o => o.id === id); }
  function colaboradorById(id) { return COLABORADORES.find(c => c.id === id); }

  function statusConv(conv) {
    const ap = apForConv(conv.id);
    if (completeConv(conv)) return apontamentoAtrasado(ap) ? 'Regularizado com atraso' : 'Regularizado';
    const limite = deadlineApontamento(conv.dataServico);
    if (now() >= limite) return 'Pendente de apontamento';
    if (dateLocal(conv.dataServico) > now()) return 'Aguardando serviço';
    return 'Aguardando apontamento';
  }

  function badgeForStatus(status) {
    if (status === 'Regularizado') return `<span class="badge success">✓ ${status}</span>`;
    if (status === 'Regularizado com atraso') return `<span class="badge warning">↻ ${status}</span>`;
    if (status.includes('Pendente')) return `<span class="badge danger">! ${status}</span>`;
    return `<span class="badge info">• ${status}</span>`;
  }

  function pendenciasApontamento() {
    return convocacoesSupervisor().filter(c => !completeConv(c) && now() >= deadlineApontamento(c.dataServico));
  }

  function diasSemConvocacao(supervisores=SUPERVISORES,inicio='2026-09-16',fim=isoToday()) {
    const out=[];const end=fim<isoToday()?fim:isoToday();
    for(const supervisor of supervisores){let start=inicio>'2026-09-16'?inicio:'2026-09-16';if(supervisor==='FELIPE'&&start<'2026-09-28')start='2026-09-28';
      for(let d=dateLocal(start);d<=dateLocal(end);d.setDate(d.getDate()+1)){const date=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');if(!state.convocacoes.some(c=>c.supervisor===supervisor&&c.dataServico===date&&(c.executor||c.supervisor)===supervisor))out.push({supervisor,dataServico:date});}
    }return out;
  }
  function previstasSemConvocacao(){return diasSemConvocacao(perfilAtual==='SUPERVISOR'?[supervisorAtual]:SUPERVISORES);}

  function regularizacoesAtrasadas() {
    return apontamentosSupervisor().filter(apontamentoAtrasado);
  }

  function perfilLabel(perfil) {
    return {
      SUPERVISOR: 'Portal do Supervisor',
      CONTROLADORIA: 'Controladoria',
      FINANCEIRO: 'Financeiro',
      VISUALIZAR: 'Somente visualizar',
    }[perfil] || 'APROAR';
  }

  function navConfig() {
    const item=(view,label,icon,group='')=>({view,label,icon,group});
    if(perfilAtual==='CONTROLADORIA') return [item('inicio','Início','⌂'),item('convocacao','Convocação','▤','OPERAÇÃO'),item('conflitos','Conflitos','!'),item('apontamento','Apontamento','✓'),item('whatsapp','WhatsApp','◌'),item('disponibilidade','Disponibilidade','♙'),item('indisponibilidade','Indisponibilidade','⊘'),item('dashboard','Dashboard','▦','ANÁLISE E FECHAMENTO'),item('relatorios','Relatórios','▥'),item('indicadores','Indicadores','↗'),item('configuracoes','Configurações','⚙','SISTEMA')];
    if(perfilAtual==='VISUALIZAR') return [item('dashboard','Dashboard','▦'),item('relatorios','Relatórios','▥'),item('indicadores','Indicadores','↗')];
    if(perfilAtual==='FINANCEIRO') return [item('inicio','Início','⌂'),item('financeiro','Pagamentos','$'),item('ausencias','Faltas / Atestados','⊘'),item('relatorios','Relatório','▥')];
    return [item('inicio','Início','⌂'),item('convocacao','Convocação','▤'),item('apontamento','Apontamento','✓'),item('disponibilidade','Disponibilidade','♙'),item('pendencias','Pendências','!')];
  }

  function sidebarIcon(view){
    const shapes={
      inicio:'<path d="m3 10 9-7 9 7"/><path d="M5 9v12h5v-7h4v7h5V9"/>',
      convocacao:'<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h4M9 12h6M9 16h6"/>',
      conflitos:'<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5"/><path d="M12 17h.01"/>',
      apontamento:'<rect x="4" y="4" width="16" height="16" rx="2"/><path d="m8 12 3 3 5-6"/>',
      whatsapp:'<path d="M4 4h16v13H9l-5 4V4Z"/><path d="M8 8h8M8 12h5"/>',
      disponibilidade:'<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3"/>',
      indisponibilidade:'<circle cx="12" cy="12" r="9"/><path d="m6 6 12 12"/>',
      dashboard:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
      relatorios:'<path d="M3 21h18M6 18v-7M12 18V4M18 18v-11"/>',
      indicadores:'<path d="m3 17 6-6 4 4 8-10M16 5h5v5"/>',
      configuracoes:'<path d="m12 2 8.7 5v10L12 22l-8.7-5V7L12 2Z"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
      financeiro:'<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
      ausencias:'<circle cx="12" cy="12" r="9"/><path d="m6 6 12 12"/>',
      pendencias:'<circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/>'
    };
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${shapes[view]||shapes.convocacao}</svg>`;
  }

  function renderNav() {
    const nav = $('#side-nav');
    nav.innerHTML = navConfig().map(item => `${item.group ? `<div class="side-group">${item.group}</div>` : ''}
      <button data-view="${item.view}" class="nav-item ${item.view === viewAtual ? 'active' : ''}">
        <span class="nav-icon">${sidebarIcon(item.view)}</span> ${item.label}
      </button>
    `).join('');
  }

  function setView(view) {
    const permitidas = navConfig().map(x => x.view);
    viewAtual = permitidas.includes(view) ? view : 'inicio';
    renderNav();
    const map = {
      inicio:'Início',
      convocacao:'Convocação',
      apontamento:'Apontamento',
      pendencias:'Pendências',
      indicadores:'Indicadores',
      relatorios:'Relatórios',
      financeiro:'Fechamento financeiro',
    };
    $('#topbar-title').textContent = navConfig().find(x=>x.view===viewAtual)?.label || map[viewAtual] || 'APROAR';
    $('.sidebar').classList.remove('open');
    render();
  }

  function render() {
    if (!perfilAtual) return showLogin();
    if (perfilAtual === 'SUPERVISOR' && !supervisorAtual) return showLogin();

    showApp();
    if(perfilAtual==='VISUALIZAR'){const pages={dashboard:renderDashboard,relatorios:renderReports,indicadores:renderIndicators};return (pages[viewAtual]||renderDashboard)();}

    if (perfilAtual === 'CONTROLADORIA') {
      const renderers = { inicio: renderControladoriaInicio, indicadores: renderControladoriaIndicadores, relatorios: renderRelatoriosBase };
      return (extendedRenderers[viewAtual] || renderers[viewAtual] || renderControladoriaInicio)();
    }

    if (perfilAtual === 'FINANCEIRO') {
      const renderers = { inicio: renderFinanceiroInicio, financeiro: renderFinanceiroFechamento, relatorios: renderRelatoriosBase };
      return (extendedRenderers[viewAtual] || renderers[viewAtual] || renderFinanceiroInicio)();
    }

    const renderers = { inicio: renderInicio, convocacao: renderConvocacao, apontamento: renderApontamento, pendencias: renderPendencias };
    (extendedRenderers[viewAtual] || renderers[viewAtual] || renderInicio)();
    renderSupervisorHeader();
  }

  function showLogin() {
    $('#login-view').classList.remove('hidden');
    $('#app-view').classList.add('hidden');
    syncLoginProfileUI();
  }

  function showApp() {
    $('#login-view').classList.add('hidden');
    $('#app-view').classList.remove('hidden');

    $('#app-view').classList.toggle('supervisor-layout',perfilAtual==='SUPERVISOR');
    $('#reset-demo').classList.toggle('hidden',perfilAtual==='VISUALIZAR');
    const label = perfilLabel(perfilAtual);
    const nomeUsuario = perfilAtual === 'SUPERVISOR' ? supervisorAtual : label.toUpperCase();
    const avatar = perfilAtual === 'SUPERVISOR' ? supervisorAtual.charAt(0) : (perfilAtual === 'CONTROLADORIA' ? 'C' : 'F');

    $('#sidebar-user').textContent = nomeUsuario;
    if(perfilAtual==='CONTROLADORIA')$('#sidebar-avatar').innerHTML='<svg viewBox="0 0 32 32" width="27" height="27" role="img" aria-label="Capacete branco de supervisor"><path d="M6 23v-4a10 10 0 0 1 20 0v4" fill="#f8fafc" stroke="#d4deea" stroke-width="1.2"/><path d="M13 22V9a3 3 0 0 1 6 0v13" fill="#ffffff" stroke="#d4deea" stroke-width="1.2"/><path d="M8 18v5M24 18v5" stroke="#c0cddd" stroke-width="1.3"/><rect x="3" y="22" width="26" height="5" rx="2" fill="#ffffff" stroke="#d4deea" stroke-width="1.2"/></svg>';else $('#sidebar-avatar').textContent = avatar;
    $('#sidebar-role').textContent = label;
    $('#topbar-eyebrow').textContent = label.toUpperCase();
    $('#today-chip').textContent = new Intl.DateTimeFormat('pt-BR', { dateStyle:'full' }).format(now());

    renderNav();
  }

  function allApontamentosPendentes() {
    return state.convocacoes.filter(c => !completeConv(c) && now() >= deadlineApontamento(c.dataServico));
  }

  function allServicosPrevistosSemConvocacao(){return diasSemConvocacao();}

  function renderControladoriaInicioBase() {
    const diasConv = new Set(state.convocacoes.map(c => `${c.supervisor}|${c.dataServico}`)).size;
    const pend = allApontamentosPendentes();
    const previstos = allServicosPrevistosSemConvocacao();
    const regularizadosAtraso = state.apontamentos.filter(apontamentoAtrasado);

    $('#main-content').innerHTML = `
      <div class="page-head">
        <div>
          <div class="eyebrow">CONTROLADORIA</div>
          <h2>Visão geral operacional</h2>
          <p>Esta área fica separada do portal dos supervisores. Nesta primeira versão, ela resume os dados de homologação do sistema.</p>
        </div>
        <span class="role-badge">Perfil administrativo</span>
      </div>

      <div class="grid grid-4">
        ${metric('DIAS COM CONVOCAÇÃO', diasConv, '1 supervisor + 1 data = 1 convocação')}
        ${metric('APONTAMENTOS SALVOS', state.apontamentos.length, 'registros efetivamente apontados')}
        ${metric('APONTAMENTOS PENDENTES', pend.length, 'convocação existente e prazo vencido')}
        ${metric('CONVOCAÇÕES NÃO FEITAS', previstos.length, 'dias sem convocação por supervisor')}
      </div>

      <div class="section grid grid-2">
        <div class="card card-pad">
          <div class="section-title"><div><h3>O que a Controladoria acompanha</h3><p>Estrutura inicial desta área.</p></div></div>
          <div class="placeholder-list">
            <div class="placeholder-item"><div><strong>Indicadores por supervisor</strong><br><small>Convocações, atrasos, apontamentos e pendências.</small></div><button class="link-btn" data-admin-go="indicadores">Abrir</button></div>
            <div class="placeholder-item"><div><strong>Relatórios operacionais</strong><br><small>Base para PDF, Excel e consolidação por período.</small></div><button class="link-btn" data-admin-go="relatorios">Abrir</button></div>
          </div>
        </div>
        <div class="card card-pad">
          <div class="section-title"><div><h3>Regra de leitura</h3><p>Pendência atual não é igual a atraso histórico.</p></div></div>
          <div class="notice info"><strong>${regularizadosAtraso.length}</strong> apontamento(s) estão regularizados com atraso no conjunto fictício. Eles permanecem no histórico, mas não devem continuar como pendência.</div>
          <div class="notice success" style="margin-top:10px">Apontamento retroativo resolve a pendência da data e preserva a informação de que o lançamento foi realizado depois.</div>
        </div>
      </div>
    `;
    $$('[data-admin-go]').forEach(b => b.onclick = () => setView(b.dataset.adminGo));
  }

  function renderControladoriaIndicadores() {
    const linhas = SUPERVISORES.map(s => {
      const convs = state.convocacoes.filter(c => c.supervisor === s&&(c.executor||c.supervisor)===s);
      const diasConv = new Set(convs.map(c => c.dataServico)).size;
      const atrasadas = new Set(convs.filter(convocacaoAtrasada).map(c => c.dataServico)).size;
      const aps = state.apontamentos.filter(a => a.supervisor === s&&(a.executor||a.supervisor)===s);
      const diasAp = new Set(aps.map(a => a.dataServico)).size;
      const apAtr = new Set(aps.filter(apontamentoAtrasado).map(a => a.dataServico)).size;
      const noPrazo = diasConv ? Math.max(0, ((diasConv - atrasadas) / diasConv * 100)) : null;
      return { s, diasConv, atrasadas, noPrazo, diasAp, apAtr };
    });

    $('#main-content').innerHTML = `
      <div class="page-head"><div><div class="eyebrow">CONTROLADORIA</div><h2>Indicadores</h2><p>Resumo com a mesma unidade de contagem que estamos usando: supervisor + data de serviço.</p></div></div>
      <div class="card card-pad">
        <div class="table-wrap">
          <table>
            <thead><tr><th>Supervisor</th><th>Convocações</th><th>Atrasadas</th><th>No prazo</th><th>Apontamentos</th><th>Apt. atrasados</th></tr></thead>
            <tbody>${linhas.map(x => `<tr><td><strong>${x.s}</strong></td><td>${x.diasConv}</td><td>${x.atrasadas}</td><td>${x.noPrazo === null ? '-' : x.noPrazo.toFixed(1)+'%'}</td><td>${x.diasAp}</td><td>${x.apAtr}</td></tr>`).join('')}</tbody>
          </table>
        </div>
      </div>
      <div class="section notice info">A tabela é propositalmente simples nesta fase. Vamos refinar as regras de datas, pendências e início histórico antes de transformar isso no relatório definitivo.</div>
    `;
  }

  function renderFinanceiroInicio() {
    const itens = state.apontamentos.flatMap(a => a.itens || []);
    const presentes = itens.filter(i => String(i.status || '').startsWith('Presente')).length;
    const faltas = itens.filter(i => i.status === 'Falta').length;
    const extras = itens.filter(i => i.extra && i.extra !== 'Não').length;

    $('#main-content').innerHTML = `
      <div class="page-head">
        <div>
          <div class="eyebrow">FINANCEIRO</div>
          <h2>Visão financeira</h2>
          <p>Área separada do apontamento operacional. Nesta fase, usa os apontamentos fictícios já confirmados.</p>
        </div>
        <span class="role-badge">Perfil financeiro</span>
      </div>
      <div class="grid grid-4">
        ${metric('APONTAMENTOS', state.apontamentos.length, 'lançamentos salvos')}
        ${metric('PRESENÇAS', presentes, 'itens apontados como presença')}
        ${metric('FALTAS', faltas, 'itens apontados como falta')}
        ${metric('EXTRAS', extras, 'itens com Extra diferente de “Não”')}
      </div>
      <div class="section card card-pad">
        <div class="section-title"><div><h3>Próximas regras</h3><p>O financeiro não altera a lógica operacional de convocação.</p></div></div>
        <div class="notice info">Nesta primeira versão, o Financeiro só lê apontamentos efetivamente salvos. Convocação sem apontamento não entra como presença nem como lançamento financeiro.</div>
      </div>
    `;
  }

  function renderFinanceiroFechamento() {
    const linhas = state.apontamentos
      .slice()
      .sort((a,b) => b.dataServico.localeCompare(a.dataServico))
      .flatMap(a => (a.itens || []).map(i => ({
        data: a.dataServico,
        supervisor: a.supervisor,
        colaborador: colaboradorById(i.colaboradorId)?.nome || i.colaboradorId,
        status: i.status,
        extra: i.extra || 'Não',
        retroativo: a.retroativo,
      })));

    $('#main-content').innerHTML = `
      <div class="page-head"><div><div class="eyebrow">FINANCEIRO</div><h2>Fechamento</h2><p>Somente apontamentos realmente salvos entram nesta base de apontamentos.</p></div></div>
      <div class="card card-pad">
        ${linhas.length ? `<div class="table-wrap"><table><thead><tr><th>Data</th><th>Supervisor</th><th>Colaborador</th><th>Status</th><th>Extra</th><th>Origem</th></tr></thead><tbody>${linhas.map(x=>`<tr><td>${formatDate(x.data)}</td><td>${x.supervisor}</td><td>${escapeHtml(x.colaborador)}</td><td>${escapeHtml(x.status)}</td><td>${escapeHtml(x.extra)}</td><td>${x.retroativo ? 'Retroativo' : 'Normal'}</td></tr>`).join('')}</tbody></table></div>` : '<div class="empty">Sem apontamentos para fechamento.</div>'}
      </div>
    `;
  }

  function renderRelatoriosBase() {
    $('#main-content').innerHTML = `
      <div class="page-head"><div><div class="eyebrow">${perfilLabel(perfilAtual).toUpperCase()}</div><h2>Relatórios</h2><p>Estrutura reservada para os relatórios da próxima etapa.</p></div></div>
      <div class="card card-pad">
        <div class="notice info">Vamos montar esta área depois que as regras operacionais de convocação, apontamento, retroativo, pendência e atraso estiverem fechadas. Assim os relatórios nascem usando a mesma fonte de verdade.</div>
      </div>
    `;
  }

  function renderInicio() {
    const convs = convocacoesSupervisor();
    const aps = apontamentosSupervisor();
    const pend = pendenciasApontamento();
    const atrasadas = regularizacoesAtrasadas();
    const convAtrasadas = new Set(convs.filter(convocacaoAtrasada).map(c=>c.dataServico)).size;
    const proximas = convs.filter(c => dateLocal(c.dataServico) >= dateLocal(isoToday())).sort((a,b)=>a.dataServico.localeCompare(b.dataServico)).slice(0,5);

    $('#main-content').innerHTML = `
      <div class="page-head">
        <div>
          <div class="eyebrow">VISÃO DO SUPERVISOR</div>
          <h2>Olá, ${supervisorAtual}</h2>
          <p>Convocação planeja o serviço. Apontamento confirma o que realmente aconteceu.</p>
        </div>
        <div class="inline-actions">
          <button class="btn btn-primary" id="quick-conv">Nova convocação</button>
          <button class="btn btn-secondary" id="quick-ap">Fazer apontamento</button>
        </div>
      </div>

      <div class="grid grid-4">
        ${metric('DIAS COM CONVOCAÇÃO', new Set(convs.map(c=>c.dataServico)).size, `${convs.length} registro(s) de equipe`)}
        ${metric('APONTAMENTOS', aps.length, 'salvos pelo supervisor')}
        ${metric('PENDÊNCIAS', pend.length, 'convocações sem apontamento vencido')}
        ${metric('REGULARIZADOS COM ATRASO', atrasadas.length, `${convAtrasadas} convocação(ões) criada(s) fora do prazo`)}
      </div>

      <div class="section grid grid-2">
        <div class="card card-pad">
          <div class="section-title"><div><h3>Próximos serviços</h3><p>Convocações já registradas.</p></div></div>
          ${proximas.length ? tableProximas(proximas) : '<div class="empty">Nenhuma convocação futura cadastrada.</div>'}
        </div>
        <div class="card card-pad">
          <div class="section-title"><div><h3>Regra principal</h3><p>Como o protótipo trata pendência e atraso.</p></div></div>
          <div class="notice info"><strong>Pendência</strong> é algo ainda não resolvido. Quando você faz um apontamento retroativo, a pendência desaparece. Se o lançamento aconteceu depois do prazo, o sistema mantém apenas o histórico de <strong>regularizado com atraso</strong>.</div>
          <div class="notice success" style="margin-top:10px"><strong>Fim de semana:</strong> serviço de sábado ou domingo pode ser apontado até segunda-feira às 09:30 sem atraso.</div>
        </div>
      </div>
    `;
    $('#quick-conv').onclick = () => setView('convocacao');
    $('#quick-ap').onclick = () => setView('apontamento');
  }

  function metric(label, value, note) {
    label = label.charAt(0).toLocaleUpperCase("pt-BR") + label.slice(1).toLocaleLowerCase("pt-BR");
    return `<div class="card metric"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-note">${note}</div></div>`;
  }

  function tableProximas(items) {
    return `<div class="table-wrap"><table><thead><tr><th>Data</th><th>Unidade</th><th>Serviço</th><th>Situação</th></tr></thead><tbody>${items.map(c => {
      const obra = obraById(c.obraId);
      return `<tr><td>${formatDate(c.dataServico)}</td><td>${c.unidade}</td><td>${obra?.nome || '-'}</td><td>${badgeForStatus(statusConv(c))}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  }

  function renderConvocacao() {
    const unidades = [...new Set(OBRAS.map(o=>o.unidade))];
    $('#main-content').innerHTML = `
      <div class="page-head"><div><div class="eyebrow">PLANEJAMENTO</div><h2>Nova convocação</h2><p>Cadastre a equipe para a data real do serviço.</p></div></div>
      <div class="grid grid-2">
        <div class="card card-pad">
          <form id="form-convocacao">
            <div class="form-grid">
              ${perfilAtual==='CONTROLADORIA' ? `<div class="full"><label class="field-label">Supervisor responsável</label><select class="control" id="conv-supervisor">${SUPERVISORES.map(x=>`<option>${x}</option>`).join('')}</select></div>` : ''}<div><label class="field-label">Data do serviço</label><input class="control" type="date" id="conv-data" value="${perfilAtual==='SUPERVISOR'?portalDate:isoToday()}" required></div>
              <div><label class="field-label">Turno</label><select class="control" id="conv-turno"><option>Integral</option><option>Manhã</option><option>Tarde</option><option>Noite</option><option>Outro</option></select></div>
              <div><label class="field-label">Unidade</label><select class="control" id="conv-unidade">${unidades.map(u=>`<option>${u}</option>`).join('')}</select></div>
              <div><label class="field-label">Obra / Serviço</label><select class="control" id="conv-obra"></select></div>
              <div class="full"><label class="field-label">Equipe</label><div class="checkbox-grid">${COLABORADORES.filter(c=>!c.inativo).map(c=>`<label class="check-card"><input type="checkbox" name="conv-colab" value="${c.id}"><span><strong>${c.nome}</strong><br><small>${c.funcao}</small></span></label>`).join('')}</div></div>
            </div>
            <details class="section"><summary>Incluir colaborador avulso</summary><div class="form-grid">${field('Nome do avulso','<input class="control" id="avulso-nome">')}${field('Função','<input class="control" id="avulso-funcao">')}${field('Categoria da diária','<select class="control" id="avulso-categoria"><option>Profissional</option><option>Ajudante</option></select>')}</div></details>
            <div class="form-actions"><button class="btn btn-primary" type="submit">Salvar convocação</button></div>
          </form>
        </div>
        <div class="card card-pad">
          <div class="section-title"><div><h3>Como o prazo é calculado</h3><p>Regra de demonstração desta versão.</p></div></div>
          <div class="notice info">Para serviços de segunda a sexta, a convocação é considerada no prazo quando registrada antes das <strong>16:00 para o próximo dia útil</strong>. Serviços e lançamentos em sábado ou domingo não geram atraso automático de convocação.</div>
          <div class="notice warning" style="margin-top:10px">A data escolhida é a <strong>data do serviço</strong>. Se você registra no dia 18 uma equipe que trabalhará no dia 19, o serviço fica associado a 19/09.</div>
        </div>
      </div>
    `;

    const unidade = $('#conv-unidade');
    const obra = $('#conv-obra');
    const refreshObras = () => {
      const opts = OBRAS.filter(o=>o.unidade===unidade.value);
      obra.innerHTML = opts.map(o=>`<option value="${o.id}">${o.nome}</option>`).join('');
    };
    unidade.onchange = refreshObras;
    refreshObras();

    $('#form-convocacao').onsubmit = (e) => {
      e.preventDefault();
      const colaboradores = $$('input[name="conv-colab"]:checked').map(x=>x.value);
      if (!colaboradores.length && !$('#avulso-nome')?.value.trim()) return toast('Selecione pelo menos um colaborador.', true);
      const avulso=$('#avulso-nome')?.value.trim();
      if(avulso){const id=uid('c');COLABORADORES.push({id,nome:avulso,funcao:$('#avulso-funcao').value.trim()||'Avulso',categoria:$('#avulso-categoria').value,avulso:'Sim',custo:180});colaboradores.push(id);}
      const obraRef = obraById(obra.value);
      const conv = {
        id: uid('cv'), supervisor: $('#conv-supervisor')?.value || supervisorAtual, dataServico: $('#conv-data').value,
        unidade: obraRef?.unidade || unidade.value, obraId: obra.value, turno: $('#conv-turno').value,
        colaboradores, criadoEm: now().toISOString(), origem: 'normal'
      };
      const bloqueio=colaboradores.find(id=>blocked(id,conv.dataServico)||state.convocacoes.some(c=>c.dataServico===conv.dataServico&&c.colaboradores.includes(id)&&overlaps(c.turno,conv.turno)));
      if(bloqueio) return toast('Colaborador indisponível ou já convocado neste turno: '+colaboradorById(bloqueio)?.nome,true);
      conv.executor=supervisorAtual||perfilLabel(perfilAtual);state.convocacoes.push(conv); audit('Nova convocação',conv.id); saveData();
      toast(convocacaoAtrasada(conv) ? 'Convocação salva e registrada como fora do prazo.' : 'Convocação salva com sucesso.');
      setView('inicio');
    };
  }

  function renderApontamento() {
    $('#main-content').innerHTML = `
      <div class="page-head">
        <div><div class="eyebrow">EXECUÇÃO</div><h2>Apontamento</h2><p>Confirme a equipe convocada ou regularize um serviço antigo.</p></div>
        <div class="tabs"><button class="tab-btn ${apontamentoTab==='normal'?'active':''}" data-tab="normal">Normal</button><button class="tab-btn ${apontamentoTab==='retroativo'?'active':''}" data-tab="retroativo">Retroativo</button></div>
      </div>
      <div id="apontamento-body"></div>
    `;
    $$('.tab-btn').forEach(b => b.onclick = () => { apontamentoTab = b.dataset.tab; render(); });
    if (apontamentoTab === 'normal') renderApontamentoNormal(); else renderApontamentoRetroativo();
  }

  let adminApDate='',adminApSup='',adminApUnit='';
  function renderApontamentoNormal(){
    if(perfilAtual==='SUPERVISOR')return renderEquipeDia();
    const body=$('#apontamento-body');adminApDate||=isoToday();
    body.innerHTML=`<div class="card card-pad"><div class="reference-filters">${field('Data do serviço',`<input id="ap-data" class="control" type="date" value="${adminApDate}">`)}${field('Supervisor','<select id="ap-supervisor" class="control"></select>')}${field('Unidade','<select id="ap-unit" class="control"></select>')}</div><div id="ap-equipe" class="section"></div></div>`;
    const candidates=()=>state.convocacoes.filter(c=>c.dataServico===adminApDate);
    const refreshSupervisors=()=>{adminApDate=$('#ap-data').value;const sups=[...new Set(candidates().map(c=>c.supervisor))].sort();if(!sups.includes(adminApSup))adminApSup=sups[0]||'';$('#ap-supervisor').innerHTML=sups.length?options(sups):'<option value="">Nenhum supervisor com convocação</option>';$('#ap-supervisor').value=adminApSup;refreshUnits();};
    const refreshUnits=()=>{adminApSup=$('#ap-supervisor').value;const units=[...new Set(candidates().filter(c=>c.supervisor===adminApSup).map(c=>c.unidade))].sort();if(!units.includes(adminApUnit))adminApUnit=units[0]||'';$('#ap-unit').innerHTML=units.length?options(units):'<option value="">Nenhuma unidade convocada</option>';$('#ap-unit').value=adminApUnit;refreshTeam();};
    const refreshTeam=()=>{adminApUnit=$('#ap-unit').value;const convs=candidates().filter(c=>c.supervisor===adminApSup&&c.unidade===adminApUnit);$('#ap-equipe').innerHTML=convs.length?convs.map((conv,index)=>{const ap=apForConv(conv.id);return `<section class="section"><div class="section-title"><div><h3>${escapeHtml(conv.unidade)} · ${escapeHtml(conv.turno)}</h3><p>${escapeHtml(conv.supervisor)} · ${conv.colaboradores.length} colaborador(es)</p></div>${badgeForStatus(statusConv(conv))}</div><form id="admin-ap-form-${index}">${conv.colaboradores.map(cid=>personRow(cid,ap?.itens.find(i=>i.colaboradorId===cid),conv.unidade,conv.obraId)).join('')}<details class="section"><summary>Incluir colaborador que não estava na convocação</summary><select class="control" id="admin-ap-add-${index}"><option value="">Selecione</option>${options(COLABORADORES.filter(c=>!c.inativo&&!conv.colaboradores.includes(c.id)))}</select><button class="btn btn-secondary section" id="admin-ap-include-${index}" type="button">Incluir na equipe</button></details><div class="form-actions"><button class="btn btn-primary">${ap?'Atualizar':'Salvar'} apontamento · ${escapeHtml(conv.turno)}</button></div></form></section>`;}).join(''):'<div class="empty">Nenhuma convocação nesta data para o supervisor selecionado. Use o retroativo para um serviço sem convocação prévia.</div>';bindServiceRows();convs.forEach((conv,index)=>{const form=$('#admin-ap-form-'+index);form.onsubmit=e=>{e.preventDefault();const itens=readPersonRows(conv.colaboradores,form);if(!validServices(itens,conv.unidade))return;const ap=apForConv(conv.id);if(ap){ap.itens=itens;ap.atualizadoEm=now().toISOString();}else state.apontamentos.push({id:uid('ap'),convocacaoId:conv.id,supervisor:conv.supervisor,executor:'CONTROLADORIA',dataServico:conv.dataServico,apontadoEm:now().toISOString(),retroativo:false,itens});audit('Apontamento administrativo',conv.supervisor+' · '+conv.unidade);saveData();toast('Apontamento salvo.');refreshTeam();};$('#admin-ap-include-'+index).onclick=()=>{const id=$('#admin-ap-add-'+index).value;if(!id)return;if(blocked(id,conv.dataServico)||state.convocacoes.some(c=>c.id!==conv.id&&c.dataServico===conv.dataServico&&c.colaboradores.includes(id)&&overlaps(c.turno,conv.turno)))return toast('Colaborador indisponível ou já convocado neste turno.',true);conv.colaboradores.push(id);audit('Inclusão na equipe',conv.id);saveData();refreshTeam();};});};
    $('#ap-data').onchange=refreshSupervisors;$('#ap-supervisor').onchange=refreshUnits;$('#ap-unit').onchange=refreshTeam;refreshSupervisors();
  }


  function allocationRow(unit,service={},index=0){
    const works=OBRAS.filter(o=>o.unidade===unit);
    return `<div class="allocation-row"><div>${field(index?'Obra / Serviço adicional '+index:'Obra / Serviço',`<select class="control service-work"><option value="">— Selecione o serviço —</option>${works.map(o=>`<option value="${o.id}" ${o.id===service.obraId?'selected':''}>${escapeHtml(o.nome)}</option>`).join('')}</select>`)}</div><div>${field('Período',`<select class="control service-period">${['Integral','Manhã','Tarde','Noite'].map(x=>`<option ${x===(service.periodo||'Integral')?'selected':''}>${x}</option>`).join('')}</select>`)}</div></div>`;
  }
  function itemServices(item,defaultObra){
    if(item?.servicos?.length)return item.servicos;
    const first=item?.obraId||defaultObra;
    if(item?.segundaObraId)return [{obraId:first,periodo:item.periodo||'Manhã',percentual:50},{obraId:item.segundaObraId,periodo:item.segundoPeriodo||'Tarde',percentual:50}];
    return [{obraId:item?first:'',periodo:item?.periodo||'Integral',percentual:100}];
  }
  function personRow(cid,item=null,unit='',defaultObra=''){
    const c=colaboradorById(cid),services=itemServices(item,defaultObra);
    return `<div class="person-row person-card" data-person="${cid}" data-unit="${escapeHtml(unit)}" data-extra-original="${item?.valorExtraOriginal||0}" data-finance-adjusted="${item?.financeAdjusted?'true':'false'}"><div class="person-name">${escapeHtml(c?.nome||cid)}<br><small>${escapeHtml(c?.funcao||'')} · ${escapeHtml(unit)}</small></div>
      <div class="person-top">${field('Status',`<select class="control row-status">${STATUS_OPTIONS.map(x=>`<option ${x===(item?.status||'Presente (Integral)')?'selected':''}>${x}</option>`).join('')}</select>`)}</div>
      <div class="person-services"><div class="allocations principal-service">${allocationRow(unit,services[0],0)}</div>
      <div class="form-grid">${field('Extra',`<select class="control row-extra">${[...EXTRA_OPTIONS,...(item?.extra==='Valor específico'?['Valor específico']:[])].map(x=>`<option ${x===(item?.extra||'Não')?'selected':''}>${x}</option>`).join('')}</select>`)}${field('Financeiro (R$)',`<input class="control row-financeiro" type="number" min="0" step="0.01" value="${item?.financeiro??0}">`)}${field('Acordos / Bonificações (R$)',`<input class="control row-acordo" type="number" min="0" step="0.01" value="${item?.acordo||0}">`)}</div>
      <details class="more-services"><summary>Mais opções</summary>${field('Observação / justificativa',`<input class="control row-obs" value="${escapeHtml(item?.observacao||'')}">`)}${field('Adic. noturno (SEBRAE)',`<input class="control row-noturno" type="number" min="0" step="0.01" value="${unit==='SEBRAE'&&presence(item?.status||'Presente (Integral)')?(item?.financeAdjusted?(item?.noturno||0):Math.max(90,item?.noturno||0)):0}" readonly>`)}<div class="additional-services">${services.slice(1).map((x,i)=>allocationRow(unit,x,i+1)).join('')}</div><div class="inline-actions section"><button type="button" class="btn btn-primary add-service">+ Adicionar serviço</button><button type="button" class="btn btn-secondary remove-last-service">− Remover último</button><span class="service-count">${Math.max(0,services.length-1)} serviço(s) adicional(is)</span></div></details></div></div>`;
  }
  function bindServiceRows(){
    $$('.person-card').forEach(card=>{
      const update=()=>card.querySelector('.service-count').textContent=card.querySelectorAll('.additional-services .allocation-row').length+' serviço(s) adicional(is)';
      card.querySelector('.add-service').onclick=()=>{card.querySelector('.additional-services').insertAdjacentHTML('beforeend',allocationRow(card.dataset.unit,{},card.querySelectorAll('.allocation-row').length));update();};
      card.querySelector('.row-status').onchange=()=>{const n=card.querySelector('.row-noturno');n.value=card.dataset.unit==='SEBRAE'&&presence(card.querySelector('.row-status').value)?(card.dataset.financeAdjusted==='true'?n.value:Math.max(90,Number(n.value)||0)):0;};
      card.querySelector('.remove-last-service').onclick=()=>{card.querySelector('.additional-services .allocation-row:last-child')?.remove();update();};
    });
  }
  function readPersonRows(ids,scope=document){
    return ids.map(cid=>{const row=scope.querySelector(`[data-person="${cid}"]`);const servicos=[...row.querySelectorAll('.allocation-row')].map(r=>({obraId:r.querySelector('.service-work').value,periodo:r.querySelector('.service-period').value}));return {colaboradorId:cid,status:row.querySelector('.row-status').value,extra:row.querySelector('.row-extra').value,valorExtraOriginal:Number(row.dataset.extraOriginal)||0,observacao:row.querySelector('.row-obs').value.trim(),servicos,obraId:servicos[0]?.obraId||'',financeAdjusted:row.dataset.financeAdjusted==='true',financeiro:Number(row.querySelector('.row-financeiro').value||0),noturno:Number(row.querySelector('.row-noturno').value),acordo:Number(row.querySelector('.row-acordo').value)};});
  }
  function validServices(items,unit){
    for(const i of items){if(!presence(i.status))continue;const ss=i.servicos;
      if(!ss.length||ss.some(x=>!x.obraId||obraById(x.obraId)?.unidade!==unit)){toast('Escolha os serviços de cada colaborador dentro da unidade selecionada.',true);return false;}
      if(new Set(ss.map(x=>x.obraId+'|'+x.periodo)).size!==ss.length){toast('Há um serviço repetido no mesmo período para o colaborador.',true);return false;}
    }return true;
  }

  function renderApontamentoRetroativo() {
    if(perfilAtual==='SUPERVISOR'&&retroDateSelected)portalDate=retroDateSelected;
    const body = $('#apontamento-body');
    const unidades = [...new Set(OBRAS.map(o=>o.unidade))];
    body.innerHTML = `
      <div class="grid grid-2">
        <div class="card card-pad">
          <form id="form-retro">
          ${perfilAtual==='CONTROLADORIA'?`<label class="field-label">Supervisor responsável</label><select class="control" id="retro-sup">${options(SUPERVISORES)}</select>`:''}
            <div class="form-grid">
              <div><label class="field-label">Data do serviço</label><input id="retro-data" type="date" class="control" value="${retroDateSelected||portalDate}" max="${isoToday()}" required></div>
              <div><label class="field-label">Turno</label><select id="retro-turno" class="control"><option>Integral</option><option>Manhã</option><option>Tarde</option><option>Noite</option><option>Outro</option></select></div>
              <div><label class="field-label">Unidade</label><select id="retro-unidade" class="control">${unidades.map(u=>`<option>${u}</option>`).join('')}</select></div>
              <div class="notice info">Selecione os serviços individualmente na ficha de cada colaborador.</div>
              <div class="full"><label class="field-label">Colaboradores a apontar</label><p style="font-size:12px">Não selecionar alguém não registra falta. Para registrar falta, selecione a pessoa e escolha “Falta” no Status. Convocados sem apontamento permanecem pendentes.</p><div class="checkbox-grid retro-person-list">${COLABORADORES.filter(c=>!c.inativo).map(c=>`<label class="check-card"><input type="checkbox" name="retro-colab" value="${c.id}"><span><strong>${c.nome}</strong><br><small>${c.funcao}</small></span></label>`).join('')}</div></div>
              <div class="full" id="retro-rows"></div>
            </div>
            <div class="form-actions"><button class="btn btn-primary" type="submit">Salvar apontamento retroativo</button></div>
          </form>
        </div>
        ${perfilAtual==='SUPERVISOR'?'<aside class="card card-pad"><div class="section-title"><div><h3>Datas com apontamento pendente</h3><p>Selecione uma equipe para regularizar.</p></div></div><div id="retro-pending-list" class="retro-pending-list"></div></aside>':`        <div class="card card-pad">
          <div class="section-title"><div><h3>O que acontece ao salvar</h3><p>Regularização automática da data.</p></div></div>
          <div class="notice success"><strong>Se não houver convocação:</strong> o sistema cria o registro daquela data e salva o apontamento ao mesmo tempo.</div>
          <div class="notice info" style="margin-top:10px"><strong>Se já houver convocação pendente:</strong> ela é vinculada ao apontamento e deixa de ser pendência.</div>
          <div class="notice warning" style="margin-top:10px"><strong>Histórico:</strong> se o prazo já venceu, o item fica como “Regularizado com atraso”, mas não permanece na lista de pendências.</div>
        </div>`}

      </div>`;

    const unidade = $('#retro-unidade'), rows = $('#retro-rows');
    let retroDrafts=new Map();
    if(perfilAtual==='SUPERVISOR'){
      const pending=new Map();for(const c of state.convocacoes.filter(c=>c.supervisor===supervisorAtual&&c.dataServico<=isoToday()&&!completeConv(c))){const done=new Set(apForConv(c.id)?.itens.map(i=>i.colaboradorId)||[]),ids=c.colaboradores.filter(id=>!done.has(id));if(!ids.length)continue;const key=c.dataServico+'|'+c.unidade+'|'+c.turno;if(!pending.has(key))pending.set(key,{date:c.dataServico,unit:c.unidade,turn:c.turno,ids:new Set()});ids.forEach(id=>pending.get(key).ids.add(id));}
      const groups=[...pending.values()].sort((a,b)=>a.date.localeCompare(b.date)||a.unit.localeCompare(b.unit,'pt-BR')||a.turn.localeCompare(b.turn,'pt-BR'));
      let date='';$('#retro-pending-list').innerHTML=groups.length?groups.map((g,index)=>{const title=date!==g.date?'<h4 class="retro-pending-date">'+formatDate(g.date)+'</h4>':'';date=g.date;return title+`<button type="button" class="retro-pending-item" data-retro-pending="${index}"><span><strong>${escapeHtml(g.unit)}</strong><small>${escapeHtml(g.turn)} · ${g.ids.size} colaborador(es) sem apontamento</small></span><span class="retro-pending-action">Regularizar →</span></button>`;}).join(''):'<div class="notice success">Nenhum apontamento pendente até hoje.</div>';
      $$('[data-retro-pending]').forEach(button=>button.onclick=()=>{const g=groups[Number(button.dataset.retroPending)];retroDateSelected=g.date;portalDate=g.date;portalUnit=g.unit;$('#retro-data').value=g.date;unidade.value=g.unit;$('#retro-turno').value=g.turn;retroDrafts.clear();$$('input[name="retro-colab"]').forEach(input=>input.checked=g.ids.has(input.value));refreshRows(true);syncRetroHeader();if($('#portal-unit'))$('#portal-unit').value=g.unit;$$('[data-retro-pending]').forEach(b=>b.classList.toggle('active',b===button));});
    }
    $('#retro-data').onchange=()=>{retroDateSelected=$('#retro-data').value;if(perfilAtual==='SUPERVISOR'&&retroDateSelected){portalDate=retroDateSelected;syncRetroHeader();}};
    unidade.onchange=()=>{retroDrafts.clear();refreshRows(true);};
    if(perfilAtual==='SUPERVISOR'&&portalUnit!=='Todas')unidade.value=portalUnit;

    function refreshRows(reset=false) {
      const current=$$('#retro-rows [data-person]').map(x=>x.dataset.person);if(!reset)readPersonRows(current).forEach(i=>retroDrafts.set(i.colaboradorId,i));
      const ids = $$('input[name="retro-colab"]:checked').map(x=>x.value);
      rows.innerHTML = ids.length ? `<div class="section-title" style="margin-top:12px"><div><h3>Apontamento da equipe</h3><p>Defina status e extra. Extra inicia em “Não”.</p></div></div>${ids.map(id=>personRow(id,retroDrafts.get(id),unidade.value)).join('')}` : '';
      bindServiceRows();
    }
    $$('input[name="retro-colab"]').forEach(x=>x.onchange = ()=>refreshRows());

    $('#form-retro').onsubmit = (e) => {
      e.preventDefault();
      const dataServico = $('#retro-data').value;
      if (!dataServico) return toast('Escolha a data do serviço.', true);if(dataServico>isoToday())return toast('O apontamento retroativo não aceita data futura.',true);
      const ids = $$('input[name="retro-colab"]:checked').map(x=>x.value);
      if (!ids.length) return toast('Selecione pelo menos um colaborador.', true);
      const itens=readPersonRows(ids);if(!validServices(itens,unidade.value))return;
      const obraRef=obraById(itens.find(i=>i.servicos[0]?.obraId)?.servicos[0]?.obraId)||OBRAS.find(o=>o.unidade===unidade.value);
      const responsavel=$('#retro-sup')?.value||supervisorAtual;
      const matching=state.convocacoes.filter(c=>c.supervisor===responsavel&&c.dataServico===dataServico&&c.unidade===unidade.value&&c.turno===$('#retro-turno').value);
      const batches=new Map(),newIds=[];
      for(const id of ids){const c=matching.find(c=>c.colaboradores.includes(id));if(c){if(!batches.has(c.id))batches.set(c.id,{conv:c,items:[]});batches.get(c.id).items.push(itens.find(i=>i.colaboradorId===id));}else newIds.push(id);}
      if(newIds.length){const conv={id:uid('cv'),supervisor:responsavel,dataServico,unidade:unidade.value,obraId:obraRef?.id||'',turno:$('#retro-turno').value,colaboradores:newIds,criadoEm:now().toISOString(),origem:'retroativo'};state.convocacoes.push(conv);batches.set(conv.id,{conv,items:itens.filter(i=>newIds.includes(i.colaboradorId))});}
      for(const {conv,items} of batches.values()){const selected=new Set(items.map(i=>i.colaboradorId));let ap=apForConv(conv.id);if(ap){ap.itens=[...ap.itens.filter(i=>!selected.has(i.colaboradorId)),...items];ap.atualizadoEm=now().toISOString();ap.retroativo=true;}else state.apontamentos.push({executor:supervisorAtual||perfilLabel(perfilAtual),id:uid('ap'),convocacaoId:conv.id,supervisor:conv.supervisor,dataServico,apontadoEm:now().toISOString(),retroativo:true,itens:items});}
      audit('Apontamento retroativo',dataServico);saveData();toast([...batches.values()].every(({conv})=>completeConv(conv))?'Apontamento retroativo salvo. Equipe regularizada.':'Apontamento salvo. Há colaboradores convocados que continuam pendentes.');
      setView('pendencias');
    };
  }

  function renderPendencias() {
    const pend = pendenciasApontamento();
    const example=pend.find(c=>c.exemploRegularizacao);
    const previstas = previstasSemConvocacao();
    const reg = regularizacoesAtrasadas().sort((a,b)=>b.dataServico.localeCompare(a.dataServico));

    $('#main-content').innerHTML = `
      <div class="page-head"><div><div class="eyebrow">ACOMPANHAMENTO</div><h2>Pendências</h2><p>Pendência é algo ainda sem solução. Itens regularizados saem daqui e permanecem apenas no histórico.</p></div><button id="go-retro" class="btn btn-primary">Regularizar retroativamente</button></div>

      ${example?`<div class="notice info section">Exemplo para testar: ${example.supervisor} · ${example.unidade} · ${formatDate(example.dataServico)}. Use “Regularizar” na linha abaixo e salve o apontamento.</div>`:''}
      <div class="grid grid-3">
        ${metric('APONTAMENTOS PENDENTES', pend.length, 'há convocação, mas não há apontamento salvo')}
        ${metric('CONVOCAÇÕES NÃO FEITAS', previstas.length, 'dias sem convocação por supervisor')}
        ${metric('REGULARIZADOS COM ATRASO', reg.length, 'histórico, não pendência')}
      </div>

      <div class="section card card-pad">
        <div class="section-title"><div><h3>Apontamentos pendentes</h3><p>Só aparecem quando existe convocação e o prazo já venceu.</p></div></div>
        ${pend.length ? `<div class="table-wrap"><table><thead><tr><th>Data</th><th>Unidade</th><th>Serviço</th><th>Prazo</th><th>Ação</th></tr></thead><tbody>${pend.map(c=>`<tr><td>${formatDate(c.dataServico)}</td><td>${c.unidade}</td><td>${obraById(c.obraId)?.nome || '-'}</td><td>${formatDateTime(deadlineApontamento(c.dataServico))}<br><small>${apForConv(c.id)?'Apontamento parcial':'Não apontado'}</small></td><td><button class="link-btn regularizar" data-date="${c.dataServico}">Regularizar</button></td></tr>`).join('')}</tbody></table></div>` : '<div class="empty">Nenhum apontamento pendente.</div>'}
      </div>

      <div class="section card card-pad">
        <div class="section-title"><div><h3>Convocações não feitas</h3><p>Dias sem convocação registrada por supervisor. Felipe é considerado a partir de 28/09.</p></div></div>
        ${table(['Supervisor','Quantidade','Dias sem convocação'],[...new Set(previstas.map(x=>x.supervisor))].map(s=>{const days=previstas.filter(x=>x.supervisor===s).map(x=>x.dataServico);return [s,days.length,days.map(formatDate).join(', ')];}))}
      </div>

      ${perfilAtual==='SUPERVISOR'?'':`      <div class="section card card-pad">
        <div class="section-title"><div><h3>Histórico de regularizações com atraso</h3><p>Já foram resolvidas e não são mais pendências.</p></div></div>
        ${reg.length ? `<div class="table-wrap"><table><thead><tr><th>Data do serviço</th><th>Registrado em</th><th>Origem</th><th>Status</th></tr></thead><tbody>${reg.map(a=>`<tr><td>${formatDate(a.dataServico)}</td><td>${formatDateTime(a.apontadoEm)}</td><td>${a.retroativo ? 'Retroativo' : 'Apontamento normal'}</td><td>${badgeForStatus('Regularizado com atraso')}</td></tr>`).join('')}</tbody></table></div>` : '<div class="empty">Nenhuma regularização atrasada neste conjunto de teste.</div>'}
      </div>`}`;

    $('#go-retro').onclick = () => { apontamentoTab = 'retroativo'; setView('apontamento'); };
    $$('.regularizar').forEach(b => b.onclick = () => {
      apontamentoTab = 'retroativo';
      setView('apontamento');
      setTimeout(() => { const inp = $('#retro-data'); if (inp){inp.value=b.dataset.date;inp.onchange?.();const source=state.convocacoes.find(c=>c.dataServico===b.dataset.date&&(perfilAtual!=='SUPERVISOR'||c.supervisor===supervisorAtual)&&c.unidade===$('#retro-unidade')?.value&&!completeConv(c));if(source){$$('input[name="retro-colab"]').forEach(x=>x.checked=source.colaboradores.includes(x.value));$('input[name="retro-colab"]:checked')?.onchange?.();}} }, 0);
    });
  }

  function escapeHtml(v) {
    return String(v ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function showToast(msg, error=false) {
    const el = $('#toast');
    el.textContent = msg;
    el.style.background = error ? '#8f2d2d' : '#0f2c4d';
    el.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(()=>el.classList.remove('show'), 2800);
  }

  let loginRole='CONTROLADORIA';
  function syncLoginProfileUI(){ const role=loginRole;$('#login-supervisor-wrap').classList.toggle('hidden',role!=='SUPERVISOR');$('#login-password').required=!['SUPERVISOR','VISUALIZAR'].includes(role);$('#login-password').closest('.password-wrap').classList.toggle('hidden',['SUPERVISOR','VISUALIZAR'].includes(role));document.querySelector('label[for="login-password"]').classList.toggle('hidden',['SUPERVISOR','VISUALIZAR'].includes(role));$('#login-error').textContent='';$('#login-password').value=''; }
  function enterProfile(profile){
    perfilAtual=profile;sessionStorage.setItem(PROFILE_KEY,profile);
    if(profile==='SUPERVISOR'){supervisorAtual=SUPERVISORES.includes(supervisorAtual)?supervisorAtual:SUPERVISORES[0];sessionStorage.setItem(SESSION_KEY,supervisorAtual);viewAtual='apontamento';portalUnit=state.convocacoes.find(c=>c.supervisor===supervisorAtual&&c.dataServico===portalDate)?.unidade||OBRAS[0]?.unidade||'Todas';}
    else{supervisorAtual='';sessionStorage.removeItem(SESSION_KEY);viewAtual=profile==='VISUALIZAR'?'dashboard':'inicio';}
    render();
  }
  function init(){
    $('#login-access').onchange=syncLoginProfileUI;
    $('#show-password').onclick=()=>{const inp=$('#login-password');inp.type=inp.type==='password'?'text':'password';$('#show-password').setAttribute('aria-label',inp.type==='password'?'Mostrar senha':'Ocultar senha');};
    $('#enter-supervisor').onclick=()=>enterProfile('SUPERVISOR');$('#enter-viewer').onclick=()=>enterProfile('VISUALIZAR');$('#logout-button').onclick=logout;
    $('#reset-demo').onclick=()=>{if(perfilAtual!=='VISUALIZAR')resetData();};
    $('#side-nav').onclick=e=>{const btn=e.target.closest('.nav-item');if(btn)setView(btn.dataset.view);};
    $('#mobile-menu').onclick=()=>$('.sidebar').classList.toggle('open');
    if(perfilAtual==='SUPERVISOR')viewAtual='apontamento';if(perfilAtual==='VISUALIZAR')viewAtual='dashboard';render();
  }
  function syncRetroHeader(){
    const convs=convocacoesSupervisor().filter(c=>c.dataServico===portalDate&&(portalUnit==='Todas'||c.unidade===portalUnit));
    const total=convs.reduce((v,c)=>v+c.colaboradores.length,0),pointed=convs.reduce((v,c)=>v+c.colaboradores.filter(id=>apForConv(c.id)?.itens.some(i=>i.colaboradorId===id)).length,0);
    if($('#portal-date-label'))$('#portal-date-label').textContent=formatDate(portalDate);
    if($('#portal-date'))$('#portal-date').value=portalDate;
    if($('#portal-total'))$('#portal-total').textContent=total;
    if($('#portal-pointed'))$('#portal-pointed').textContent=pointed;
    if($('#portal-pending-total'))$('#portal-pending-total').textContent=Math.max(0,total-pointed);
  }
  function renderSupervisorHeader(){
    const convs=convocacoesSupervisor().filter(c=>c.dataServico===portalDate&&(portalUnit==='Todas'||c.unidade===portalUnit));
    const total=convs.reduce((v,c)=>v+c.colaboradores.length,0);const pointed=convs.reduce((v,c)=>v+c.colaboradores.filter(id=>apForConv(c.id)?.itens.some(i=>i.colaboradorId===id)).length,0);
    const logo=$('.brand-lockup img').src;
    $('#main-content').insertAdjacentHTML('afterbegin',`<div class="portal-hero"><img src="${logo}" alt="Logo da APROAR"><div class="portal-heading"><span>Portal do Supervisor</span><h1>Minha equipe</h1></div><div class="portal-hero-end"><div class="portal-date">Data<strong id="portal-date-label">${formatDate(portalDate)}</strong></div><div class="inline-actions"><button class="btn btn-outline" id="portal-reset">Restaurar testes</button><button class="btn btn-outline" id="portal-logout">Sair</button></div></div></div>
      <div class="portal-tabs">${[['apontamento','Apontamentos'],['convocacao','Convocação'],['disponibilidade','Disponibilidade']].map(([v,l])=>`<button class="tab-btn ${viewAtual===v?'active':''}" data-portal-view="${v}">${l}</button>`).join('')}</div>
      <div class="portal-filters">${field('SUPERVISOR',`<select id="portal-sup" class="control">${options(SUPERVISORES)}</select>`)}${field('Unidade',`<select id="portal-unit" class="control">${options(['Todas',...[...new Set(OBRAS.map(o=>o.unidade))]])}</select>`)}${field('Data',`<input id="portal-date" class="control" type="date" value="${portalDate}">`)}</div>
      <div class="grid grid-3 portal-metrics"><div class="portal-metric"><strong id="portal-total">${total}</strong><span>convocados</span></div><div class="portal-metric"><strong id="portal-pointed">${pointed}</strong><span>apontados</span></div><button class="portal-metric pending" id="portal-pending"><strong id="portal-pending-total">${Math.max(0,total-pointed)}</strong><span>pendentes do dia</span><small>Ver minhas pendências</small></button></div>`);
    $('#portal-sup').value=supervisorAtual;$('#portal-unit').value=portalUnit;
    $('#portal-sup').onchange=()=>{supervisorAtual=$('#portal-sup').value;portalUnit=state.convocacoes.find(c=>c.supervisor===supervisorAtual&&c.dataServico===portalDate)?.unidade||portalUnit;sessionStorage.setItem(SESSION_KEY,supervisorAtual);render();};
    $('#portal-unit').onchange=()=>{portalUnit=$('#portal-unit').value;render();};$('#portal-date').onchange=()=>{portalDate=$('#portal-date').value;if(viewAtual==='apontamento'&&apontamentoTab==='retroativo'){retroDateSelected=portalDate;$('#retro-data').value=portalDate;syncRetroHeader();}else render();};
    $('#portal-logout').onclick=logout;$('#portal-reset').onclick=resetData;$('#portal-pending').onclick=()=>setView('pendencias');$$('[data-portal-view]').forEach(b=>b.onclick=()=>setView(b.dataset.portalView));
    const unidade=$('#conv-unidade')||$('#disp-unit');if(unidade&&portalUnit!=='Todas'){unidade.value=portalUnit;unidade.onchange?.();}
    const apDate=$('#ap-data');if(apDate)apDate.onchange=()=>{portalDate=apDate.value;render();};
  }

  function audit(action,ref='') {state.auditoria.push({data:now().toISOString(),usuario:supervisorAtual||perfilLabel(perfilAtual),action,ref});}
  function head(title,desc){return `<div class="page-head"><div><div class="eyebrow">${perfilLabel(perfilAtual)}</div><h2>${title}</h2><p>${desc}</p></div></div>`;}
  function table(headers,rows){
    const align=headers.map((header,index)=>{const h=String(header).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
      if(/r\$|custo|financeiro|valor diario|valor diaria|impacto|noturno|periculosidade|bonifica|acordos/.test(h)||rows.some(r=>typeof r[index]==='string'&&/^R\$/.test(r[index].trim())))return 'align-money';
      if(/nome|colaborador|supervisor|supervisor|responsave|unidade|obra|grupo|funcao|moradia|observa|referencia|detalhe|ocorrencia|destinatario|email|e-mail|dias sem/.test(h))return 'align-text';
      if(/data|registrado|registro|situacao|status|turno|periodo|categoria|avulso|ativo|acao|selecion|posicao|quantidade|faltas|atestados|convocac|apontament|pendencia|ausencia|taxa|prazo|atrasad|extra|total/.test(h))return 'align-center';
      return 'align-text';});
    return rows.length?`<div class="table-wrap"><table><thead><tr>${headers.map((x,j)=>`<th class="${align[j]}">${escapeHtml(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map((c,j)=>`<td class="${align[j]||'align-text'}">${c??'—'}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:'<div class="empty">Nenhum registro para os filtros selecionados.</div>';
  }
  function options(list){return list.map(x=>`<option value="${escapeHtml(x.id??x)}">${escapeHtml(x.nome??x)}</option>`).join('');}
  function field(label,input){return `<div><label class="field-label">${label}</label>${input}</div>`;}
  function blocked(id,date){return state.indisponibilidades.some(x=>x.colaboradorId===id&&x.inicio<=date&&x.fim>=date);}
  function overlaps(a,b){return a===b||a==='Integral'||b==='Integral'||a==='Outro'||b==='Outro';}
  function localDownload(name,content,mime='text/plain'){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([content],{type:mime}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
  function exportTable(){const t=$('#main-content table');if(!t)return toast('Sem dados para exportar.',true);const csv=[...t.rows].map(r=>[...r.cells].map(c=>'"'+c.innerText.replaceAll('"','""')+'"').join(';')).join('\r\n');localDownload('aproar_relatorio.csv','\uFEFF'+csv,'text/csv;charset=utf-8');}
  function exportButtons(){return `<div class="inline-actions section"><button class="btn btn-secondary" id="export-csv">Exportar CSV</button><button class="btn btn-secondary" id="export-excel">Gerar Excel</button><button class="btn btn-primary" id="export-pdf">Gerar PDF</button></div>`;}
  function bindExports(){$('#export-csv').onclick=exportTable;$('#export-excel').onclick=()=>['relatorios','pagamentos','financeiro'].includes(viewAtual)?exportReportsExcel():exportVisibleWorkbook('aproar_relatorio');$('#export-pdf').onclick=()=>reportPDF(perfilAtual==='FINANCEIRO'?'financial':'control');}
  function renderConvCompletaBase(){
    if(perfilAtual==='SUPERVISOR')return renderUnitConvocacao();
    renderConvocacao();
    if(perfilAtual!=='CONTROLADORIA')return;
    const content=$('#main-content');content.insertAdjacentHTML('afterbegin','<div class="tabs" style="margin-bottom:20px"><button class="tab-btn active" id="new-conv">Nova convocação</button><button class="tab-btn" id="edit-conv">Correção / Exclusão administrativa</button></div>');
    $('#new-conv').onclick=renderConvCompleta;
    $('#edit-conv').onclick=()=>{content.innerHTML=head('Correção / Exclusão administrativa','Corrija a data, responsável, obra e turno de registros.')+table(['Selecionar','Data','Supervisor','Obra','Turno','Ação'],state.convocacoes.map(c=>[`<input type="checkbox" class="del-conv" value="${c.id}">`,formatDate(c.dataServico),c.supervisor,escapeHtml(obraById(c.obraId)?.nome),c.turno,`<button class="link-btn" data-edit="${c.id}">Editar</button>`]))+'<div class="form-actions"><button class="btn btn-secondary" id="back-conv">Nova convocação</button><button class="btn btn-primary" id="delete-convs">Excluir selecionadas</button></div><div id="edit-area"></div>';
    $('#back-conv').onclick=renderConvCompleta;
    $('#delete-convs').onclick=()=>{const ids=$$('.del-conv:checked').map(x=>x.value);if(!ids.length)return toast('Selecione os registros.',true);state.convocacoes=state.convocacoes.filter(c=>!ids.includes(c.id));state.apontamentos=state.apontamentos.filter(a=>!ids.includes(a.convocacaoId));audit('Exclusão de convocações',ids.join(', '));saveData();toast('Registros excluídos.');renderConvCompleta();};
    $$('[data-edit]').forEach(b=>b.onclick=()=>{const c=state.convocacoes.find(c=>c.id===b.dataset.edit);$('#edit-area').innerHTML=`<form id="edit-form" class="card card-pad form-grid">${field('Data',`<input class="control" id="edit-date" type="date" value="${c.dataServico}" required>`)}${field('Supervisor',`<select class="control" id="edit-sup">${options(SUPERVISORES)}</select>`)}${field('Obra',`<select class="control" id="edit-obra">${options(OBRAS)}</select>`)}${field('Turno',`<select class="control" id="edit-turno">${options(['Integral','Manhã','Tarde','Noite'])}</select>`)}<button class="btn btn-primary">Salvar correção</button></form>`;$('#edit-sup').value=c.supervisor;$('#edit-obra').value=c.obraId;$('#edit-turno').value=c.turno;$('#edit-form').onsubmit=e=>{e.preventDefault();const date=$('#edit-date').value,turno=$('#edit-turno').value;if(c.colaboradores.some(id=>blocked(id,date)||state.convocacoes.some(o=>o.id!==c.id&&o.dataServico===date&&o.colaboradores.includes(id)&&overlaps(o.turno,turno))))return toast('A correção geraria conflito de equipe.',true);Object.assign(c,{dataServico:date,turno,supervisor:$('#edit-sup').value,obraId:$('#edit-obra').value,unidade:obraById($('#edit-obra').value).unidade});const ap=apForConv(c.id);if(ap)Object.assign(ap,{dataServico:date,supervisor:c.supervisor});c.corrigidoPor=perfilLabel(perfilAtual);audit('Correção administrativa',c.id);saveData();toast('Correção salva.');renderConvCompleta();};});};
  }
  function renderApCompleto(){renderApontamento();if(perfilAtual==='CONTROLADORIA')$('#main-content').insertAdjacentHTML('afterbegin','<div class="notice info" style="margin-bottom:16px">A Controladoria pode apontar equipes de todos os supervisores. O responsável do registro original é preservado.</div>');}
  function renderDisponibilidade(){
    $('#main-content').innerHTML=head('Disponibilidade da equipe','Consulte ocupação e bloqueios por data e turno.')+`<div class="card card-pad form-grid">${field('Data',`<input class="control" type="date" id="disp-data" value="${perfilAtual==='SUPERVISOR'?portalDate:isoToday()}">`)}${field('Turno',`<select class="control" id="disp-turno">${options(['Integral','Manhã','Tarde','Noite'])}</select>`)}</div><div class="section" id="disp-table"></div>`;
    let selected='ocupados';
    const refresh=()=>{
      const d=$('#disp-data').value,t=$('#disp-turno').value,groups={ocupados:[],disponiveis:[],indisponiveis:[]};
      for(const c of COLABORADORES.filter(c=>!c.inativo).sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR'))){
        const conv=state.convocacoes.filter(x=>x.dataServico===d&&x.colaboradores.includes(c.id)&&overlaps(t,x.turno));
        const blocks=state.indisponibilidades.filter(x=>x.colaboradorId===c.id&&x.inicio<=d&&x.fim>=d);
        const group=blocks.length?'indisponiveis':conv.length?'ocupados':'disponiveis';
        const allocation=conv.map(x=>escapeHtml(x.supervisor+' · '+x.unidade+' · '+x.turno)).join('<br>');
        const reason=blocks.map(x=>escapeHtml(x.motivo)+(x.obs||x.observacao?' · '+escapeHtml(x.obs||x.observacao):'')).join('<br>');
        groups[group].push([escapeHtml(c.nome),escapeHtml(c.funcao),group==='indisponiveis'?reason+(allocation?'<br><small>Convocação registrada: '+allocation+'</small>':''):group==='ocupados'?allocation:'Livre no turno selecionado']);
      }
      const labels={ocupados:'Ocupados',disponiveis:'Disponíveis',indisponiveis:'Indisponíveis'};
      $('#disp-table').innerHTML='<div class="availability-tabs" role="tablist" aria-label="Situação da equipe">'+Object.keys(groups).map(k=>`<button type="button" role="tab" aria-selected="${selected===k}" class="availability-tab ${k} ${selected===k?'active':''}" data-availability="${k}">${labels[k]} <span>${groups[k].length}</span></button>`).join('')+'</div><div class="availability-panel" role="tabpanel">'+(groups[selected].length?table(['Colaborador','Função',selected==='indisponiveis'?'Motivo / observação':selected==='ocupados'?'Alocação':'Disponibilidade'],groups[selected]):'<div class="card empty">Nenhum colaborador nesta situação para a data e o turno selecionados.</div>')+'</div>';
      $$('[data-availability]').forEach(btn=>btn.onclick=()=>{selected=btn.dataset.availability;refresh();});
    };$('#disp-data').onchange=refresh;$('#disp-turno').onchange=refresh;refresh();
  }
  function renderIndisponibilidade(){
    $('#main-content').innerHTML=head('Indisponibilidade','Férias, atestados e afastamentos bloqueiam novas convocações nas datas cadastradas.')+`<form id="ind-form" class="card card-pad"><div class="form-grid">${field('Colaborador',`<select class="control" id="ind-colab">${options(COLABORADORES.filter(c=>!c.inativo))}</select>`)}${field('Motivo',`<select class="control" id="ind-motivo">${options(['Férias','Atestado','Afastamento','Outro'])}</select>`)}${field('Início',`<input class="control" type="date" id="ind-ini" value="${perfilAtual==='SUPERVISOR'?portalDate:isoToday()}" required>`)}${field('Fim',`<input class="control" type="date" id="ind-fim" value="${perfilAtual==='SUPERVISOR'?portalDate:isoToday()}" required>`)}${field('Observação','<input class="control" id="ind-obs">')}</div><div class="form-actions"><button class="btn btn-primary">Registrar indisponibilidade</button></div></form><div class="section">${table(['Colaborador','Motivo','Início','Fim','Observação','Ação'],state.indisponibilidades.map(x=>[escapeHtml(colaboradorById(x.colaboradorId)?.nome),x.motivo,formatDate(x.inicio),formatDate(x.fim),escapeHtml(x.obs),`<button class="link-btn" data-remove-ind="${x.id}">Excluir</button>`]))}</div>`;
    $('#ind-form').onsubmit=e=>{e.preventDefault();if($('#ind-fim').value<$('#ind-ini').value)return toast('O fim deve ser igual ou posterior ao início.',true);state.indisponibilidades.push({id:uid('ind'),colaboradorId:$('#ind-colab').value,motivo:$('#ind-motivo').value,inicio:$('#ind-ini').value,fim:$('#ind-fim').value,obs:$('#ind-obs').value});audit('Registro de indisponibilidade');saveData();renderIndisponibilidade();};$$('[data-remove-ind]').forEach(b=>b.onclick=()=>{state.indisponibilidades=state.indisponibilidades.filter(x=>x.id!==b.dataset.removeInd);audit('Exclusão de indisponibilidade');saveData();renderIndisponibilidade();});
  }
  function registerConvocationConflicts(ids,date,turno,unit,supervisor){
    state.conflitosTentados??=[];
    for(const id of ids){const existing=state.convocacoes.filter(c=>c.dataServico===date&&c.colaboradores.includes(id)&&c.unidade!==unit&&overlaps(c.turno,turno));
      for(const c of existing)state.conflitosTentados.push({id:uid('conf'),data:now().toISOString(),dataServico:date,colaboradorId:id,colaboradorNome:colaboradorById(id)?.nome||id,supervisor,unidade:unit,turno,executor:perfilAtual==='SUPERVISOR'?supervisorAtual:'CONTROLADORIA',convocacaoExistenteId:c.id,supervisorExistente:c.supervisor,unidadeExistente:c.unidade,turnoExistente:c.turno,resolvido:false});
    }saveData();
  }
  function convocationConflictRows(){return (state.conflitosTentados||[]).flatMap((x,index)=>{
    if(x.supervisorExistente&&x.unidadeExistente)return [{...x,key:x.id||String(index)}];
    // Recover old blocked attempts from their matching original convocation.
    return state.convocacoes.filter(c=>c.dataServico===x.dataServico&&c.colaboradores.includes(x.colaboradorId)&&c.unidade!==x.unidade&&overlaps(c.turno,x.turno)).map(c=>({...x,key:String(index),colaboradorNome:colaboradorById(x.colaboradorId)?.nome,supervisorExistente:c.supervisor,unidadeExistente:c.unidade,turnoExistente:c.turno}));
  });}
  function renderConflitos(){const attempts=convocationConflictRows(),pending=attempts.filter(x=>!x.resolvido);
    $('#main-content').innerHTML=head('Conflitos','Tentativas bloqueadas: um colaborador já convocado em outra unidade, na mesma data e em turno sobreposto.')+metric('Conflitos pendentes',pending.length,'tentativas que precisam de conferência')+`<div class="section">${table(['Data do serviço','Colaborador','Quem tentou convocar','Unidade solicitada','Turno solicitado','Já convocado por','Unidade original','Turno original','Tentativa registrada em','Situação','Ação'],attempts.slice().reverse().map(x=>[formatDate(x.dataServico),escapeHtml(x.colaboradorNome||colaboradorById(x.colaboradorId)?.nome),escapeHtml(x.supervisor),escapeHtml(x.unidade),escapeHtml(x.turno),escapeHtml(x.supervisorExistente),escapeHtml(x.unidadeExistente),escapeHtml(x.turnoExistente),formatDateTime(x.data),x.resolvido?'Conferido':'Pendente',x.resolvido?'—':`<button class="link-btn" data-resolve-conflict="${escapeHtml(x.key)}">Marcar como conferido</button>`]))}</div><div class="notice info section">A tentativa foi bloqueada: a convocação original permanece válida. Indisponibilidade cadastrada é acompanhada na aba Indisponibilidade. Turnos sem sobreposição não geram conflito.</div><div class="form-actions"><button class="btn btn-primary" id="conf-edit">Abrir convocações</button></div>`;
    $('#conf-edit').onclick=()=>setView('convocacao');$$('[data-resolve-conflict]').forEach(b=>b.onclick=()=>{const x=(state.conflitosTentados||[]).find((x,index)=>(x.id||String(index))===b.dataset.resolveConflict);if(!x)return;x.resolvido=true;x.conferidoEm=now().toISOString();audit('Conflito conferido',x.colaboradorId);saveData();renderConflitos();});
  }

  function renderWhatsAppBase(){
    $('#main-content').innerHTML=head('WhatsApp','Prepare e copie a relação de equipes. O envio é manual nesta demonstração.')+`<div class="card card-pad form-grid">${field('Data',`<input class="control" type="date" id="wp-data" value="${perfilAtual==='SUPERVISOR'?portalDate:isoToday()}">`)}${field('Funções','<label><input type="checkbox" id="wp-func" checked> Mostrar função entre parênteses</label>')}<div class="full"><textarea class="control" id="wp-text" style="min-height:240px" readonly></textarea></div><label><input type="checkbox" id="wp-pend"> Ainda existem demandas que serão enviadas por outros responsáveis</label></div><div class="form-actions"><button class="btn btn-primary" id="wp-copy">Copiar mensagem</button></div><div class="section" id="wp-missing"></div>`;
    const update=()=>{const convs=state.convocacoes.filter(c=>c.dataServico===$('#wp-data').value);$('#wp-text').value='APROAR — Equipes de '+formatDate($('#wp-data').value)+'\n\n'+convs.map(c=>c.unidade+' · '+c.supervisor+' · '+c.turno+'\n'+c.colaboradores.map(id=>{const p=colaboradorById(id);return '• '+p?.nome+($('#wp-func').checked?' ('+p?.funcao+')':'');}).join('\n')).join('\n\n')+($('#wp-pend').checked?'\n\nOutras demandas serão enviadas posteriormente.':'');$('#wp-missing').innerHTML='<div class="notice info">Unidades sem convocação nesta data: '+escapeHtml([...new Set(OBRAS.map(o=>o.unidade))].filter(u=>!convs.some(c=>c.unidade===u)).join(', ')||'nenhuma')+'</div>';};['wp-data','wp-func','wp-pend'].forEach(id=>$('#'+id).onchange=update);$('#wp-copy').onclick=async()=>{try{await navigator.clipboard.writeText($('#wp-text').value);toast('Mensagem copiada.');}catch{$('#wp-text').select();toast('Selecione e copie com Ctrl+C.');}};update();
  }
  let reportFilters={inicio:'2026-09-01',fim:isoToday(),supervisor:'Todos',obra:'Todas'};
  function filterControls(){return `<div class="card card-pad form-grid">${field('Periodicidade',`<select class="control" id="r-period">${options(['Personalizado','Diário','Semanal','Mensal'])}</select>`)}${field('Supervisor',`<select class="control" id="r-sup">${options(['Todos',...SUPERVISORES])}</select>`)}${field('Início',`<input class="control" id="r-ini" type="date" value="${reportFilters.inicio}">`)}${field('Fim',`<input class="control" id="r-fim" type="date" value="${reportFilters.fim}">`)}${field('Obra / serviço',`<select class="control" id="r-obra"><option value="Todas">Todas</option>${options(OBRAS)}</select>`)}</div>`;}
  function bindFilters(refresh){$('#r-sup').value=reportFilters.supervisor;$('#r-obra').value=reportFilters.obra;['r-sup','r-obra','r-ini','r-fim'].forEach(id=>$('#'+id).onchange=()=>{reportFilters={inicio:$('#r-ini').value,fim:$('#r-fim').value,supervisor:$('#r-sup').value,obra:$('#r-obra').value};refresh();});$('#r-period').onchange=()=>{let d=dateLocal(isoToday());const p=$('#r-period').value;if(p==='Semanal')d.setDate(d.getDate()-6);if(p==='Mensal')d.setDate(1);if(p!=='Personalizado'){reportFilters.inicio=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');reportFilters.fim=isoToday();$('#r-ini').value=reportFilters.inicio;$('#r-fim').value=reportFilters.fim;refresh();}};}
  function filteredConvs(){return state.convocacoes.filter(c=>c.dataServico>=reportFilters.inicio&&c.dataServico<=reportFilters.fim&&(reportFilters.supervisor==='Todos'||c.supervisor===reportFilters.supervisor)&&(reportFilters.obra==='Todas'||c.obraId===reportFilters.obra||(apForConv(c.id)?.itens||[]).some(i=>serviceList(i,c).some(x=>x.obraId===reportFilters.obra))));}
  const money=v=>Number(v||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const roundMoney=x=>Math.round((Number(x)||0)*100)/100;
  const clean=x=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
  function presence(status){return ['Presente (Integral)','Presente (Só Manhã)','Presente (Só Tarde)','Saída Antecipada','Presente','Extra'].includes(status);}
  function category(p){const cat=clean(p?.categoria||p?.categoria_diaria);if(/AJUD|SERVENT|AUX/.test(cat))return 'Ajudante';if(/PROF/.test(cat))return 'Profissional';if(/AJUDANTE|AUXILIAR|AUX[. ]|SERVENTE/.test(clean(p?.funcao)))return 'Ajudante';const ref=Number(p?.custo??p?.valor_diaria)||0;return ref>0&&ref<220?'Ajudante':'Profissional';}
  function dayCost(p){const v=Number(p?.custo??p?.valor_diaria);return v>0?v:category(p)==='Ajudante'?182.34:241.74;}
  function extraMultiplier(value){const v=clean(value);if(!v||['NAO','N','SEM EXTRA','SEM'].includes(v))return 0;if(/UMA E MEIA|1 E MEIA|1[.,]5/.test(v))return 1.5;if(/DUAS|2 DIARIA|2DIARIA/.test(v))return 2;if(v.includes('MEIA'))return .5;return 1;}
  function defaultFinancial(p,extra){return roundMoney((category(p)==='Ajudante'?80:120)*extraMultiplier(extra));}
  function dangerEligible(p){const f=clean(p?.funcao);return f==='ELETRICISTA'||(f.includes('ELETRICISTA')&&(f.includes('AUXILIAR')||/^AUX[. ]/.test(f)));}
  function brazilParts(date=new Date()){return Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Fortaleza',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).formatToParts(date).filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));}
  function brazilDate(date=new Date()){const p=brazilParts(date);return p.year+'-'+p.month+'-'+p.day;}
  function calendarISO(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
  function brazilTime(date,hour,minute=0){return new Date(date+'T'+String(hour).padStart(2,'0')+':'+String(minute).padStart(2,'0')+':00-03:00');}
  function completeConv(c){const ap=apForConv(c.id);return !!ap&&c.colaboradores.every(id=>ap.itens.some(i=>i.colaboradorId===id));}
  function serviceList(i,c){const raw=i.servicos?.length?i.servicos:itemServices(i,c.obraId);const seen=new Set();return raw.filter(s=>{if(!s.obraId)return false;const key=s.obraId+'|'+(s.periodo||c.turno);if(seen.has(key))return false;seen.add(key);return true;}).map(s=>({...s,periodo:s.periodo||c.turno||'Integral'}));}
  function hasSebrae(i,c){return clean(c.unidade)==='SEBRAE'||serviceList(i,c).some(s=>clean(obraById(s.obraId)?.unidade)==='SEBRAE');}
  function nocturnal(i,c){if(!presence(i.status)||!hasSebrae(i,c))return 0;const v=Math.max(0,Number(i.noturno)||0);return roundMoney(i.financeAdjusted?v:Math.max(90,v));}
  function periodBlocks(p){return p==='Manhã'?{M:.5}:p==='Tarde'?{T:.5}:p==='Noite'?{N:1}:{M:.5,T:.5};}
  function presenceBlocks(i,c){if(!presence(i.status))return {};if(i.status==='Presente (Só Manhã)')return {M:.5};if(i.status==='Presente (Só Tarde)')return {T:.5};if(i.status==='Saída Antecipada')return c.turno==='Noite'?{N:.5}:c.turno==='Tarde'?{T:.5}:{M:.5};return periodBlocks(c.turno);}
  function entries(){
    const groups=new Map();for(const c of state.convocacoes){if(c.dataServico<reportFilters.inicio||c.dataServico>reportFilters.fim||(reportFilters.supervisor!=='Todos'&&c.supervisor!==reportFilters.supervisor))continue;for(const i of apForConv(c.id)?.itens||[]){const k=c.dataServico+'|'+i.colaboradorId;if(!groups.has(k))groups.set(k,[]);groups.get(k).push({c,i});}}
    const out=[];
    for(const regs of groups.values()){
      const p=colaboradorById(regs[0].i.colaboradorId),services=new Map(),blocks={daily:{},extra:{},finance:{}},refs=regs.map(x=>x.i);
      for(const {c,i} of regs){const ss=serviceList(i,c);if(!ss.length){if(!presence(i.status)){const fake={obraId:c.obraId||'',periodo:c.turno};ss.push(fake);}else continue;}
        const isPresent=presence(i.status),serviceBlocks=[...new Set(ss.flatMap(s=>Object.keys(periodBlocks(s.periodo))))];
        const financial=isPresent?Math.max(0,Number(i.financeiro)||0):0,extra=isPresent?(i.extra==='Valor específico'?Number(i.valorExtraOriginal)||0:roundMoney(dayCost(p)*extraMultiplier(i.extra))):0;
        for(const b of serviceBlocks){blocks.finance[b]=Math.max(blocks.finance[b]||0,financial/serviceBlocks.length);blocks.extra[b]=Math.max(blocks.extra[b]||0,extra/serviceBlocks.length);}
        for(const [b,w] of Object.entries(presenceBlocks(i,c)))blocks.daily[b]=Math.max(blocks.daily[b]||0,roundMoney(dayCost(p)*w));
        const sb=ss.filter(s=>clean(obraById(s.obraId)?.unidade||c.unidade)==='SEBRAE');
        for(const s of ss){const key=s.obraId||'unassigned_'+c.unidade;let row=services.get(key);if(!row){row={c:{...c,obraId:s.obraId,unidade:obraById(s.obraId)?.unidade||c.unidade},i,p,refs,blocks:new Set(),periods:new Set(),supervisors:new Set(),statuses:new Set(),extras:new Set(),daily:0,extra:0,finance:0,night:0,bonus:0,danger:0,share:1};services.set(key,row);}Object.keys(periodBlocks(s.periodo)).forEach(b=>row.blocks.add(b));row.periods.add(s.periodo);row.supervisors.add(c.supervisor);row.statuses.add(i.status);row.extras.add(i.extra||'Não');if(sb.includes(s))row.night+=nocturnal(i,c)/sb.length;row.bonus+=(isPresent?Math.max(0,Number(i.acordo)||0):0)/ss.length;}
      }
      for(const b of new Set([...Object.keys(blocks.daily),...Object.keys(blocks.extra),...Object.keys(blocks.finance)])){let participants=[...services.values()].filter(x=>x.blocks.has(b));if(!participants.length)participants=[...services.values()];for(const row of participants)for(const field of ['daily','extra','finance'])row[field]+=(blocks[field][b]||0)/participants.length;}
      for(const row of services.values()){row.daily=roundMoney(row.daily);row.extra=roundMoney(row.extra);row.finance=roundMoney(row.finance);row.night=roundMoney(row.night);row.bonus=roundMoney(row.bonus);if(dangerEligible(p))row.danger=roundMoney(row.daily*1.3)-row.daily+roundMoney(row.extra*1.3)-row.extra;row.danger=roundMoney(row.danger);row.service={obraId:row.c.obraId,periodo:[...row.periods].join(' + ')};row.c.supervisor=[...row.supervisors].join(' / ');row.displayStatus=[...row.statuses].join(' / ');row.displayExtra=[...row.extras].join(' / ');if(reportFilters.obra==='Todas'||row.c.obraId===reportFilters.obra)out.push(row);}
    }return out;
  }
  function financialEntries(){const map=new Map();for(const x of entries()){const key=x.c.dataServico+'|'+x.i.colaboradorId+'|'+x.c.supervisor;if(!map.has(key))map.set(key,{...x,refs:[...x.refs],units:new Set([x.c.unidade]),works:new Set([x.c.obraId])});else{const prev=map.get(key);for(const k of ['daily','extra','danger','night','bonus','finance'])prev[k]+=x[k];prev.units.add(x.c.unidade);prev.works.add(x.c.obraId);prev.refs=[...new Set([...prev.refs,...x.refs])];}}return [...map.values()];}
  function adjustPayment(row,field,value){const data={financeiro:row.finance,noturno:row.night,acordo:row.bonus};data[field]=Math.max(0,Number(value)||0);for(const [index,i] of row.refs.entries()){i.financeiro=index===0?roundMoney(data.financeiro):0;i.noturno=index===0&&row.units.has('SEBRAE')?roundMoney(data.noturno):0;i.acordo=index===0?roundMoney(data.acordo):0;i.financeAdjusted=true;}audit('Ajuste financeiro',row.c.dataServico+' · '+row.p?.nome);saveData();}
  function financialCycle(ref=isoToday(),offset=0){const d=dateLocal(ref),n=(d.getDay()-2+7)%7;d.setDate(d.getDate()-n+offset*7);const end=new Date(d);end.setDate(end.getDate()+6);const pay=new Date(end);pay.setDate(pay.getDate()+1);return {inicio:calendarISO(d),fim:calendarISO(end),pagamento:calendarISO(pay)};}
  function reminder(c){const today=isoToday(),p=brazilParts(now()),hh=Number(p.hour)+Number(p.minute)/60;if(c.dataServico>today)return 'Ainda não iniciou';if(clean(c.unidade)==='SEBRAE')return c.dataServico===today?(hh<21?'Hoje · 21:00':'Lembrete de 21:00 já passou'):'Somente manual';if(c.dataServico===today)return hh<16?'Hoje · 16:00':'Próximo dia · 09:30';const d=dateLocal(c.dataServico);d.setDate(d.getDate()+1);return calendarISO(d)===today?(hh<9.5?'Hoje · 09:30':'Lembrete de 09:30 já passou'):'Somente manual';}

  function personCount(e,test){return new Set(e.filter(test).map(x=>x.c.id+'|'+x.i.colaboradorId)).size;}
  function renderReports(){
    const financial=perfilAtual==='FINANCEIRO';if(financial&&selectedCycle!=='custom'){const cycle=financialCycle(isoToday(),Number(selectedCycle));reportFilters.inicio=cycle.inicio;reportFilters.fim=cycle.fim;}
    $('#main-content').innerHTML=head('Relatórios','Dados de homologação por período, com consolidado e detalhamento por dia.')+(financial?cycleControl():'')+filterControls()+'<div class="section report-toolbar"><div class="report-view" id="report-tabs"></div>'+exportButtons()+'</div><div class="section" id="report-body"></div>';let day='Todos';
    const refresh=()=>{const rows=entries().filter(x=>!financial||(presence(x.i.status)&&x.finance+x.night+x.bonus>0.005)),dates=[...new Set(filteredConvs().map(c=>c.dataServico))].sort();if(!dates.includes(day))day='Todos';$('#report-tabs').innerHTML=field('Visualização',`<select id="report-day-select" class="control"><option value="Todos">Consolidado do período</option>${dates.map(d=>`<option value="${d}">${formatDate(d)}</option>`).join('')}</select>`);$('#report-day-select').value=day;const selected=rows.filter(x=>day==='Todos'||x.c.dataServico===day);const fin=perfilAtual==='FINANCEIRO';$('#report-body').innerHTML=table(['Data','Supervisor','Unidade','Obra','Colaborador','Período','Status',fin?'Financeiro':'Custo normal','Extra','Adic. noturno','Acordos / Bonificações',...(fin?[]:['Periculosidade 30%']),'Total'],selected.map(x=>[formatDate(x.c.dataServico),x.c.supervisor,escapeHtml(x.c.unidade),escapeHtml(fin?financialWorkNumber(x.c.obraId):obraById(x.c.obraId)?.nome),escapeHtml(x.p?.nome),escapeHtml(x.service.periodo),escapeHtml(x.displayStatus||x.i.status),money(fin?x.finance:x.daily),escapeHtml(x.displayExtra||x.i.extra),money(x.night),money(x.bonus),...(fin?[]:[money(x.danger)]),money(fin?x.finance+x.night+x.bonus:x.daily+x.extra+x.danger+x.night+x.bonus)]))+`<div class="notice info section">Valores de demonstração. ${fin?'Financeiro sem adicional de periculosidade.':'Periculosidade de 30% para eletricista e auxiliar de eletricista, somente na Controladoria.'} Convocações sem apontamento ficam fora dos custos.</div>`;$('#report-day-select').onchange=()=>{day=$('#report-day-select').value;refresh();};};bindFilters(()=>{if(financial){selectedCycle='custom';$('#financial-cycle').value='custom';}refresh();});if(financial){$('#financial-cycle').onchange=()=>{selectedCycle=$('#financial-cycle').value;renderReports();};if(selectedCycle!=='custom')$('#cycle-caption').textContent='Pagamento em '+formatDate(financialCycle(isoToday(),Number(selectedCycle)).pagamento);}refresh();bindExports();
  }
  function renderDashboard(){
    $('#main-content').innerHTML=head('Dashboard','Presença, faltas e custos confirmados por unidade e responsável.')+filterControls()+'<div class="section" id="dash-body"></div>';
    const refresh=()=>{const e=entries();$('#dash-body').innerHTML=`<div class="grid grid-4">${metric('PRESENÇAS',personCount(e,x=>presence(x.i.status)),'apontadas')}${metric('FALTAS',personCount(e,x=>x.i.status==='Falta'),'registros')}${metric('ATESTADOS',personCount(e,x=>x.i.status==='Atestado'),'registros')}${metric('CUSTO TOTAL',money(e.reduce((v,x)=>v+x.daily+x.extra+x.danger+x.night+x.bonus,0)),'valores fictícios')}</div><div class="section grid grid-2 dashboard-breakdown">${['unidade','supervisor'].map(k=>'<div class="card card-pad"><h3>Por '+(k==='unidade'?'unidade':'supervisor')+'</h3>'+table(['Grupo','Custo'],[...new Set(e.map(x=>x.c[k]))].map(v=>[escapeHtml(v),money(e.filter(x=>x.c[k]===v).reduce((s,x)=>s+x.daily+x.extra+x.danger+x.night+x.bonus,0))]))+'</div>').join('')}</div>`;};bindFilters(refresh);refresh();
  }
  function renderIndicatorsBase(){
    $('#main-content').innerHTML=head('Indicadores','Cada supervisor e data conta como uma convocação. Os apontamentos pendentes são conferidos por dia, inclusive quando parciais.')+filterControls()+'<div class="section" id="indicator-body"></div>'+exportButtons();
    const refresh=()=>{
      const sups=reportFilters.supervisor==='Todos'?SUPERVISORES:[reportFilters.supervisor];const inside=date=>date>=reportFilters.inicio&&date<=reportFilters.fim;
      const cv=state.convocacoes.filter(c=>inside(c.dataServico)&&sups.includes(c.supervisor));const ap=state.apontamentos.filter(a=>inside(a.dataServico)&&sups.includes(a.supervisor));
      const missing=diasSemConvocacao(sups,reportFilters.inicio,reportFilters.fim),countDays=rows=>new Set(rows.map(x=>x.dataServico)).size;
      const summary=sups.map(s=>{const own=cv.filter(c=>c.supervisor===s&&(c.executor||c.supervisor)===s);const pointed=ap.filter(a=>a.supervisor===s&&(a.executor||a.supervisor)===s);const n=countDays(own),late=countDays(own.filter(convocacaoAtrasada));return [s,n,late,n?((n-late)/n*100).toFixed(1)+'%':'—',countDays(pointed),countDays(pointed.filter(apontamentoAtrasado))];});
      const gaps=sups.map(s=>{const noCv=missing.filter(x=>x.supervisor===s).map(x=>x.dataServico);const noAp=[...new Set(cv.filter(c=>c.supervisor===s&&!completeConv(c)&&now()>=deadlineApontamento(c.dataServico)).map(c=>c.dataServico))].sort();return [s,noCv.length,noCv.map(formatDate).join(', ')||'Nenhum',noAp.length,noAp.map(formatDate).join(', ')||'Nenhum'];});
      const events=[...cv.filter(convocacaoAtrasada).map(c=>[formatDate(c.dataServico),c.supervisor,'Convocação',formatDateTime(c.criadoEm)]),...ap.filter(apontamentoAtrasado).map(a=>[formatDate(a.dataServico),a.supervisor,'Apontamento',formatDateTime(a.apontadoEm)])];
      $('#indicator-body').innerHTML='<div class="card card-pad"><h3>Cumprimento por supervisor</h3>'+table(['Supervisor','Convocações feitas','Conv. atrasadas','No prazo','Apontamentos feitos','Ap. atrasados'],summary)+'</div><div class="card card-pad section"><h3>Convocações e apontamentos não feitos</h3>'+table(['Supervisor','Conv. não feitas','Dias sem convocação','Ap. não feitos','Dias sem apontamento'],gaps)+'</div><div class="card card-pad section"><h3>Datas e ocorrências de atraso</h3>'+table(['Data do serviço','Supervisor','Tipo','Registro'],events)+'</div><div class="notice info section">Felipe é considerado a partir de 28/09/2026. Sábados e domingos aparecem na conferência de dias sem convocação, mas não geram atraso automático. Apontamento só é cobrado quando há convocação e o prazo de 09:30 do próximo dia útil venceu.</div>';
    };bindFilters(refresh);refresh();bindExports();
  }
  let selectedCycle='0';
  function cycleControl(){return `<div class="card card-pad section">${field('Ciclo de pagamento',`<select class="control" id="financial-cycle">${Array.from({length:26},(_,index)=>{const c=financialCycle(isoToday(),-index);return `<option value="${-index}" ${String(-index)===selectedCycle?'selected':''}>${formatDate(c.inicio)} a ${formatDate(c.fim)} · pagamento ${formatDate(c.pagamento)}</option>`;}).join('')}<option value="custom" ${selectedCycle==='custom'?'selected':''}>Período personalizado</option></select>`)}<p id="cycle-caption" style="font-size:12px"></p></div>`;}
  function renderPayments(){
    if(selectedCycle!=='custom'){const cycle=financialCycle(isoToday(),Number(selectedCycle));reportFilters.inicio=cycle.inicio;reportFilters.fim=cycle.fim;}
    $('#main-content').innerHTML=head('Pagamentos','Ciclo de terça a segunda, com pagamento na terça seguinte.')+cycleControl()+filterControls()+'<div class="section" id="pay-body"></div>'+exportButtons();
    const refresh=()=>{const e=financialEntries().filter(x=>x.finance>0.005||x.night>0.005||x.bonus>0.005);$('#pay-body').innerHTML=metric('TOTAL A PAGAR',money(e.reduce((v,x)=>v+x.finance+x.night+x.bonus,0)),'sem periculosidade')+`<div class="section">${table(['Colaborador','Total a pagar'],[...new Set(e.map(x=>x.p?.id))].map(id=>[escapeHtml(colaboradorById(id)?.nome),money(e.filter(x=>x.p?.id===id).reduce((v,x)=>v+x.finance+x.night+x.bonus,0))]))}</div><h3>Detalhamento por dia</h3>`+table(['Data','Colaborador','Status','Financeiro (R$)','Noturno (R$)','Acordos (R$)'],e.map((x,index)=>[formatDate(x.c.dataServico),escapeHtml(x.p?.nome),escapeHtml(x.i.status),...['financeiro','noturno','acordo'].map(k=>`<input aria-label="${k}" class="control pay-input" type="number" min="0" step="0.01" data-index="${index}" data-field="${k}" value="${k==='financeiro'?x.finance:k==='noturno'?x.night:x.bonus}" ${k==='noturno'&&!x.units.has('SEBRAE')?'disabled':''}>`)]));$$('.pay-input').forEach(inp=>inp.onchange=()=>{adjustPayment(e[Number(inp.dataset.index)],inp.dataset.field,inp.value);refresh();});};bindFilters(()=>{selectedCycle='custom';$('#financial-cycle').value='custom';refresh();});$('#financial-cycle').onchange=()=>{selectedCycle=$('#financial-cycle').value;renderPayments();};if(selectedCycle!=='custom')$('#cycle-caption').textContent='Pagamento em '+formatDate(financialCycle(isoToday(),Number(selectedCycle)).pagamento);refresh();bindExports();
  }
  function absenceRecords(){const groups=new Map();for(const x of operationalRows(filteredConvs()).filter(x=>['Falta','Atestado'].includes(x.i?.status))){const key=[x.c.dataServico,x.i.colaboradorId,x.c.supervisor,x.i.status].join('|');if(!groups.has(key))groups.set(key,{...x,units:new Set(),notes:new Set()});const r=groups.get(key);r.units.add(x.c.unidade);if(x.i.observacao)r.notes.add(x.i.observacao);}return [...groups.values()].sort((a,b)=>a.c.dataServico.localeCompare(b.c.dataServico)||(a.p?.nome||'').localeCompare(b.p?.nome||'','pt-BR'));}
  function absenceReportRows(){return absenceRecords().map(x=>[formatDate(x.c.dataServico),x.c.supervisor,x.p?.nome||'',x.p?.funcao||'',[...x.units].join(', '),x.i.status,[...x.notes].join(' · ')]);}
  const absenceHeaders=['Data','Supervisor','Colaborador','Função','Unidade(s)','Status','Observação'];
  function renderAbsences(){if(selectedCycle!=='custom'){const cycle=financialCycle(isoToday(),Number(selectedCycle));reportFilters.inicio=cycle.inicio;reportFilters.fim=cycle.fim;}$('#main-content').innerHTML=head('Faltas / Atestados','Ausências do ciclo de terça a segunda, separadas dos pagamentos de extras.')+cycleControl()+filterControls()+'<div class="section" id="abs-body"></div>'+exportButtons();const refresh=()=>$('#abs-body').innerHTML=table(absenceHeaders,absenceReportRows().map(r=>r.map(escapeHtml)));bindFilters(()=>{selectedCycle='custom';$('#financial-cycle').value='custom';refresh();});$('#financial-cycle').onchange=()=>{selectedCycle=$('#financial-cycle').value;renderAbsences();};if(selectedCycle!=='custom')$('#cycle-caption').textContent='Ciclo de terça a segunda · pagamento em '+formatDate(financialCycle(isoToday(),Number(selectedCycle)).pagamento);refresh();$('#export-csv').onclick=()=>{const csv=[absenceHeaders,...absenceReportRows()].map(r=>r.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(';')).join('\r\n');localDownload('faltas_atestados_'+reportFilters.inicio+'_a_'+reportFilters.fim+'.csv','\uFEFF'+csv,'text/csv;charset=utf-8');};$('#export-excel').onclick=()=>exportWorkbook([{name:'Faltas e Atestados',headers:[3],titles:[0,1],freeze:4,merges:['A1:G1','A2:G2'],widths:[14,20,38,26,26,16,48],center:[0,5],rows:[['APROAR | FALTAS E ATESTADOS'],['Período: '+reportPeriod()],[],absenceHeaders,...absenceReportRows()]}],'faltas_atestados_'+reportFilters.inicio+'_a_'+reportFilters.fim);$('#export-pdf').onclick=()=>reportPDF('absences');}

  let settingsTab='Obras';
  function renderSettingsBase(){
    const tabs=['Obras','Colaboradores','Importar Colaboradores','Cobranças Teams','Limpeza de Dados'];
    $('#main-content').innerHTML=head('Configurações','Cadastros, sincronização, histórico e manutenção da demonstração.')+`<div class="grid settings-diagnostics"><details class="card card-pad"><summary>Diagnóstico e saúde do sistema</summary><p>Demonstração HTML • dados locais • ${state.convocacoes.length} convocações • ${state.apontamentos.length} apontamentos.</p><span class="badge info">Sem conexão com o banco de produção</span></details><details class="card card-pad"><summary>Histórico de auditoria</summary><div class="section">${table(['Data','Responsável','Ação','Referência'],state.auditoria.slice().reverse().map(x=>[formatDateTime(x.data),escapeHtml(x.usuario),escapeHtml(x.action),escapeHtml(x.ref)]))}</div></details></div><details class="card card-pad section"><summary>Sincronização com o Trello</summary><p>Lista principal: EM EXECUÇÃO • atualização a cada 12 horas no sistema original.</p><div class="form-grid">${field('Lista','<select class="control"><option>EM EXECUÇÃO</option><option>Busca manual</option></select>')}${field('Buscar card ou lista','<input class="control" placeholder="Nome do card ou lista">')}</div><div class="notice info section">Área de integração preservada. Esta versão HTML usa obras fictícias e não consulta o Trello.</div><details class="section"><summary>Diagnóstico técnico</summary><p>Conexão externa ainda não configurada nesta demonstração. Regras locais: SEBRAE R$ 90; valores Financeiro livres; custos por cadastro e categoria; Extra separado; periculosidade sobre dia e Extra; alocação por blocos de período; prazos no fuso de Fortaleza; pendências parciais; ciclo financeiro de terça a segunda.</p></details></details><div class="tabs section">${tabs.map(t=>`<button class="tab-btn ${t===settingsTab?'active':''}" data-settings="${t}">${t}</button>`).join('')}</div><div id="settings-body" class="section"></div>`;
    $$('[data-settings]').forEach(b=>b.onclick=()=>{settingsTab=b.dataset.settings;renderSettings();});
    const body=$('#settings-body');
    if(settingsTab==='Obras'){
      body.innerHTML=`<form id="obra-form" class="card card-pad"><h3>Cadastrar obra</h3><div class="form-grid">${field('Nome da obra','<input class="control" id="obra-nome" required>')}${field('Unidade','<input class="control" id="obra-unidade" required>')}</div><div class="form-actions"><button class="btn btn-primary">Cadastrar obra</button></div></form><div class="section">${table(['Obra','Unidade','Ação'],OBRAS.map(o=>[escapeHtml(o.nome),escapeHtml(o.unidade),`<button class="link-btn" data-edit-obra="${o.id}">Editar</button>`]))}</div>`;
      let editing=null;$$('[data-edit-obra]').forEach(b=>b.onclick=()=>{editing=obraById(b.dataset.editObra);$('#obra-nome').value=editing.nome;$('#obra-unidade').value=editing.unidade;});$('#obra-form').onsubmit=e=>{e.preventDefault();const nome=$('#obra-nome').value.trim(),unidade=$('#obra-unidade').value.trim().toUpperCase();if(OBRAS.some(o=>o.id!==editing?.id&&o.nome.toUpperCase()===nome.toUpperCase()&&o.unidade===unidade))return toast('Obra já cadastrada nesta unidade.',true);if(editing){Object.assign(editing,{nome,unidade});state.convocacoes.filter(c=>c.obraId===editing.id).forEach(c=>c.unidade=unidade);}else OBRAS.push({id:uid('obra'),nome,unidade});audit('Cadastro / edição de obra');saveData();renderSettings();};
    } else if(settingsTab==='Colaboradores'){
      body.innerHTML=`<form id="colab-form" class="card card-pad"><h3>Cadastrar / editar colaborador</h3><div class="form-grid">${field('Nome completo','<input class="control" id="colab-nome" required>')}${field('Função','<input class="control" id="colab-funcao" required>')}${field('Custo diário com encargos (R$)','<input class="control" id="colab-custo" type="number" min="0" step="0.01" value="180" required>')}${field('Moradia','<input class="control" id="colab-moradia">')}${field('Categoria','<select class="control" id="colab-categoria"><option>Profissional</option><option>Ajudante</option></select>')}${field('Avulso','<select class="control" id="colab-avulso"><option>Não</option><option>Sim</option></select>')}</div><div class="form-actions"><button class="btn btn-primary">Salvar colaborador</button></div></form><div class="section"><input class="control" id="colab-search" placeholder="Buscar nome, função ou moradia"></div><div class="section" id="colab-table"></div>`;
      let editing=null;const refresh=()=>{$('#colab-table').innerHTML=table(['Nome','Função','Moradia','Custo diário','Categoria','Avulso','Ação'],COLABORADORES.filter(c=>(c.nome+' '+c.funcao+' '+(c.moradia||'')).toLowerCase().includes($('#colab-search').value.toLowerCase())).map(c=>[escapeHtml(c.nome),escapeHtml(c.funcao),escapeHtml(c.moradia||'—'),money(c.custo||180),escapeHtml(c.categoria||'Profissional'),escapeHtml(c.avulso||'Não'),`<button class="link-btn" data-edit-colab="${c.id}">Editar</button>`]));$$('[data-edit-colab]').forEach(b=>b.onclick=()=>{editing=colaboradorById(b.dataset.editColab);for(const [k,id] of [['nome','nome'],['funcao','funcao'],['custo','custo'],['moradia','moradia'],['categoria','categoria'],['avulso','avulso']])$('#colab-'+id).value=editing[k]??(k==='custo'?180:k==='categoria'?'Profissional':k==='avulso'?'Não':'');});};$('#colab-search').oninput=refresh;refresh();$('#colab-form').onsubmit=e=>{e.preventDefault();const data={nome:$('#colab-nome').value.trim(),funcao:$('#colab-funcao').value.trim(),custo:Number($('#colab-custo').value),moradia:$('#colab-moradia').value.trim(),categoria:$('#colab-categoria').value,avulso:$('#colab-avulso').value};if(editing)Object.assign(editing,data);else COLABORADORES.push({id:uid('c'),...data});audit('Cadastro / edição de colaborador');saveData();renderSettings();};
    } else if(settingsTab==='Importar Colaboradores'){
      body.innerHTML=`<div class="card card-pad"><h3>Importar colaboradores</h3><p>CSV com separador ponto e vírgula. Colunas: nome;funcao;custo;moradia;categoria;avulso.</p><input class="control" type="file" id="import-file" accept=".csv"><div class="notice info section">A importação Excel e o mapeamento de colunas do sistema original estão previstos na estrutura. Neste HTML, a importação funcional usa CSV.</div><div id="import-preview" class="section"></div><div class="form-actions"><button class="btn btn-secondary" id="import-template">Baixar modelo CSV</button><button class="btn btn-primary" id="import-save" disabled>Importar prévia</button></div></div>`;
      let rows=[];$('#import-template').onclick=()=>localDownload('modelo_colaboradores.csv','\uFEFFnome;funcao;custo;moradia;categoria;avulso\nExemplo fictício;Pedreiro;180;Fortaleza;Profissional;Não','text/csv;charset=utf-8');$('#import-file').onchange=async()=>{const f=$('#import-file').files[0];if(!f)return;const lines=(await f.text()).replace(/^\uFEFF/,'').trim().split(/\r?\n/);const cols=lines.shift().split(';').map(x=>x.trim().toLowerCase());if(!['nome','funcao','custo'].every(x=>cols.includes(x)))return toast('As colunas nome, funcao e custo são obrigatórias.',true);rows=lines.map(line=>{const values=line.split(';');return Object.fromEntries(cols.map((key,i)=>[key,values[i]?.trim()||'']));}).filter(x=>x.nome&&x.funcao&&Number.isFinite(Number(x.custo.replace(',','.'))));$('#import-preview').innerHTML=table(['Nome','Função','Custo'],rows.map(x=>[escapeHtml(x.nome),escapeHtml(x.funcao),escapeHtml(x.custo)]));$('#import-save').disabled=!rows.length;};$('#import-save').onclick=()=>{rows.forEach(x=>{const data={...x,custo:Number(x.custo.replace(',','.'))};const existing=COLABORADORES.find(c=>c.nome.toLowerCase()===x.nome.toLowerCase());if(existing)Object.assign(existing,data);else COLABORADORES.push({id:uid('c'),...data});});audit('Importação de colaboradores',String(rows.length));saveData();toast(rows.length+' colaboradores importados.');renderSettings();};
    } else if(settingsTab==='Cobranças Teams'){
      body.innerHTML=`<div class="card card-pad"><h3>Cobranças Teams</h3><div class="form-grid">${field('Supervisor',`<select class="control" id="teams-sup">${options(SUPERVISORES)}</select>`)}${field('Rotina','<label><input type="checkbox" id="teams-active"> Cobranças automáticas ativas (configuração demonstrativa)</label>')}</div><p>Prévia da cobrança</p><textarea class="control" id="teams-text" readonly></textarea><div class="notice info section">O envio automático ao Teams depende da integração. A prévia abaixo usa pendências reais desta demonstração.</div></div>`;const refresh=()=>{const s=$('#teams-sup').value,p=state.convocacoes.filter(c=>c.supervisor===s&&!completeConv(c)&&c.dataServico<=isoToday());$('#teams-text').value=s+', regularize os apontamentos pendentes no Portal do Supervisor. Datas: '+[...new Set(p.map(c=>c.dataServico))].map(formatDate).join(', ')+(p.length?'': 'nenhuma pendência.');body.querySelector('.notice').innerHTML='Prévia da rotina, sem envio nesta demonstração.'+table(['Data','Unidade','Situação','Próximo lembrete'],p.map(c=>[formatDate(c.dataServico),escapeHtml(c.unidade),!isWeekend(c.dataServico)&&now()>=deadlineApontamento(c.dataServico)?'ATRASADO':'PENDENTE',reminder(c)]));};$('#teams-sup').onchange=refresh;refresh();
    } else {
      body.innerHTML=`<div class="card card-pad"><h3>Limpeza de dados de homologação</h3><p>Excluir registros de uma data ou reiniciar os dados operacionais locais.</p>${field('Data','<input class="control" id="clean-date" type="date">')}<div class="form-actions"><button class="btn btn-secondary" id="clean-day">Excluir a data</button></div>${field('Confirmação','<input class="control" id="clean-confirm" placeholder="Digite LIMPAR DADOS">')}<div class="form-actions"><button class="btn btn-primary" id="clean-all">Limpar dados operacionais</button></div></div>`;$('#clean-day').onclick=()=>{const d=$('#clean-date').value;if(!d)return toast('Escolha uma data.',true);state.convocacoes=state.convocacoes.filter(c=>c.dataServico!==d);state.apontamentos=state.apontamentos.filter(a=>a.dataServico!==d);audit('Limpeza por data',d);saveData();toast('Registros da data excluídos.');};$('#clean-all').onclick=()=>{if($('#clean-confirm').value!=='LIMPAR DADOS')return toast('Digite LIMPAR DADOS para confirmar.',true);state.convocacoes=[];state.apontamentos=[];audit('Limpeza dos dados operacionais');saveData();toast('Dados operacionais fictícios excluídos.');renderSettings();};
    }
  }

  function renderEquipeDia(){
    const body=$('#apontamento-body');const convs=convocacoesSupervisor().filter(c=>c.dataServico===portalDate&&(portalUnit==='Todas'||c.unidade===portalUnit));
    const people=new Map();for(const c of convs)for(const id of c.colaboradores)if(!people.has(id))people.set(id,{conv:c,item:apForConv(c.id)?.itens.find(i=>i.colaboradorId===id)});
    body.innerHTML=`<h3>Equipe do dia</h3><p style="font-size:12px">Preencha os apontamentos e salve tudo de uma vez.</p><details class="card card-pad"><summary>Adicionar colaborador / avulso ao apontamento</summary><div class="form-grid">${field('Colaborador',`<select class="control" id="day-add-person"><option value="">Selecione</option>${options(COLABORADORES.filter(c=>!c.inativo&&!people.has(c.id)))}</select>`)}${field('Nome do avulso','<input class="control" id="day-avulso-nome">')}${field('Função do avulso','<input class="control" id="day-avulso-funcao">')}</div><div class="form-actions"><button class="btn btn-secondary" type="button" id="day-add-button">Adicionar à equipe</button></div></details><p style="font-size:12px">Para marcar todos como presentes, defina primeiro a obra/serviço de todos os colaboradores exibidos.</p><button class="btn btn-primary" style="width:100%" id="day-all-present">Marcar todos como presentes</button><form id="day-form" class="section">${people.size?[...people].map(([id,x])=>personRow(id,x.item,x.conv.unidade,x.conv.obraId)).join(''):'<div class="empty">Não há equipe convocada para esta unidade e data. Use Convocação ou adicione um colaborador acima.</div>'}<div class="form-actions"><button class="btn btn-primary" ${!people.size?'disabled':''}>Salvar apontamentos da equipe</button></div></form>`;
    bindServiceRows();
    $('#day-all-present').onclick=()=>{if(!people.size)return toast('Adicione pessoas à equipe.',true);const items=readPersonRows([...people.keys()]);if(items.some(i=>i.servicos.some(s=>!s.obraId)))return toast('Selecione primeiro os serviços de todos os colaboradores.',true);$$('.row-status').forEach(x=>{x.value='Presente (Integral)';x.onchange?.();});};
    $('#day-add-button').onclick=()=>{const unit=portalUnit==='Todas'?OBRAS[0].unidade:portalUnit;const name=$('#day-avulso-nome').value.trim();let id=$('#day-add-person').value;if(!id&&!name)return toast('Escolha um colaborador ou informe o nome do avulso.',true);if(!id){id=uid('c');COLABORADORES.push({id,nome:name,funcao:$('#day-avulso-funcao').value.trim()||'Avulso',avulso:'Sim',custo:180});}if(blocked(id,portalDate)||state.convocacoes.some(c=>c.dataServico===portalDate&&c.colaboradores.includes(id)&&overlaps(c.turno,'Integral')))return toast('Colaborador indisponível ou convocado em outra equipe.',true);let conv=convs.find(c=>c.unidade===unit);if(!conv){conv={id:uid('cv'),supervisor:supervisorAtual,dataServico:portalDate,unidade:unit,obraId:'',turno:'Integral',colaboradores:[],criadoEm:now().toISOString(),origem:'inclusao_apontamento'};state.convocacoes.push(conv);}conv.colaboradores.push(id);saveData();render();};
    $('#day-form').onsubmit=e=>{e.preventDefault();if(portalDate>isoToday())return toast('Não é possível apontar uma data futura.',true);const items=readPersonRows([...people.keys()]);for(const i of items)if(!validServices([i],people.get(i.colaboradorId).conv.unidade))return;for(const c of convs){const selected=items.filter(i=>c.colaboradores.includes(i.colaboradorId));if(!selected.length)continue;let ap=apForConv(c.id);if(ap){ap.itens=[...ap.itens.filter(i=>!selected.some(x=>x.colaboradorId===i.colaboradorId)),...selected];ap.atualizadoEm=now().toISOString();}else state.apontamentos.push({executor:supervisorAtual||perfilLabel(perfilAtual),id:uid('ap'),convocacaoId:c.id,supervisor:c.supervisor,dataServico:c.dataServico,apontadoEm:now().toISOString(),retroativo:false,itens:selected});}audit('Apontamento da equipe',portalDate);saveData();toast('Apontamentos da equipe salvos.');render();};
  }
  let unitConvDate='';let avulsoDraft=[];
  function renderUnitConvocacao(){
    if(!unitConvDate){const d=nextBusinessDay(isoToday());unitConvDate=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
    const existing=convocacoesSupervisor().filter(c=>c.dataServico===unitConvDate);const total=existing.reduce((v,c)=>v+c.colaboradores.length,0);
    $('#main-content').innerHTML=head('Convocação','Escolha unidade, turno e pessoas. Os serviços serão definidos individualmente no apontamento.')+`<div class="grid grid-3">${metric('DATA',formatDate(unitConvDate),'data da convocação')}${metric('CONVOCADOS',total,'já registrados')}${metric('AÇÃO','Montar','e confirmar abaixo')}</div><details class="card card-pad section"><summary>Já convocados · ${total}</summary>${existing.map(c=>c.colaboradores.map(id=>{const p=colaboradorById(id);return `<div class="team-list-item"><strong>${escapeHtml(p?.nome)}</strong><small>${escapeHtml(p?.funcao)} · ${escapeHtml(c.unidade)} · ${c.turno}</small></div>`;}).join('')).join('')||'<p>Nenhum convocado nesta data.</p>'}</details><form id="unit-conv-form" class="card card-pad section unit-conv"><h3>Adicionar à equipe</h3><p style="font-size:12px">Ao confirmar, a equipe é salva de uma vez.</p><div class="convocation-fields">${field('Data',`<input class="control" id="unit-conv-date" type="date" value="${unitConvDate}" required>`)}${field('Unidade',`<select class="control" id="unit-conv-unit">${options([...new Set(OBRAS.map(o=>o.unidade))])}</select>`)}${field('Turno',`<select class="control" id="unit-conv-turn">${options(['Integral','Manhã','Tarde','Noite'])}</select>`)}${field('Função',`<select class="control" id="unit-conv-function">${options(['Todas',...[...new Set(COLABORADORES.map(c=>c.funcao))]])}</select>`)}</div><details class="card card-pad section" id="previous-team-panel"><summary>Usar equipe do dia anterior</summary><p style="font-size:12px">Confira a equipe desta unidade. Desmarque quem não precisa ser convocado.</p>${field('Data da equipe de referência','<input id="previous-team-date" type="date" class="control">')}<div id="previous-team-list" class="rect-list section"></div><div class="form-actions"><button id="previous-team-use" type="button" class="btn btn-secondary">Usar pessoas selecionadas</button></div></details>${field('Colaboradores','<input class="control" id="unit-conv-search" placeholder="Digite um nome para buscar…">')}<div id="unit-conv-people" class="checkbox-grid section"></div><details class="section"><summary>Adicionar pessoas que não estão na lista</summary><p style="font-size:12px">Adicione quantos avulsos precisar e confirme toda a equipe de uma vez.</p>${field('Nome','<input class="control" id="unit-avulso-name" placeholder="Nome completo">')}${field('Função','<input class="control" id="unit-avulso-function">')}<label class="field-label"><input id="unit-avulso-check" type="checkbox" checked> É avulso?</label><button class="btn btn-secondary" type="button" id="unit-avulso-add">Adicionar pessoa</button><div id="unit-avulso-list" class="section"></div></details><div class="form-actions"><button class="btn btn-primary">Confirmar convocação da equipe</button></div></form>`;
    const selected=new Set();const refresh=(sync=true)=>{if(sync)$$('#unit-conv-people input').forEach(x=>x.checked?selected.add(x.value):selected.delete(x.value));const term=$('#unit-conv-search').value.toLowerCase(),func=$('#unit-conv-function').value;$('#unit-conv-people').innerHTML=COLABORADORES.filter(c=>!c.inativo&&c.nome.toLowerCase().includes(term)&&(func==='Todas'||c.funcao===func)).map(c=>`<label class="check-card"><input type="checkbox" value="${c.id}" ${selected.has(c.id)?'checked':''}><span>${escapeHtml(c.nome)}<small style="display:block;color:var(--muted)">${escapeHtml(c.funcao)}</small></span></label>`).join('');};$('#unit-conv-search').oninput=refresh;$('#unit-conv-function').onchange=refresh;refresh();
    if(portalUnit!=='Todas')$('#unit-conv-unit').value=portalUnit;
    const referenceDate=()=>{const d=dateLocal(unitConvDate);d.setDate(d.getDate()-1);return calendarISO(d);};$('#previous-team-date').value=referenceDate();
    const previewPrevious=()=>{const date=$('#previous-team-date').value,unit=$('#unit-conv-unit').value,turn=$('#unit-conv-turn').value;const source=state.convocacoes.filter(c=>c.supervisor===supervisorAtual&&c.dataServico===date&&c.unidade===unit);const ids=[...new Set(source.flatMap(c=>c.colaboradores))];
      $('#previous-team-list').innerHTML=ids.length?ids.map(id=>{const p=colaboradorById(id);const reason=blocked(id,unitConvDate)?'Indisponível na data de destino':state.convocacoes.some(c=>c.dataServico===unitConvDate&&c.colaboradores.includes(id)&&overlaps(c.turno,turn))?'Já convocado no turno de destino':'';return `<label class="check-card"><input class="previous-team-person" type="checkbox" value="${id}" ${reason?'disabled':'checked'}><span><strong>${escapeHtml(p?.nome||id)}</strong><small style="display:block">${escapeHtml(p?.funcao||'')} · ${escapeHtml(unit)}${reason?' · '+reason:''}</small></span></label>`;}).join(''):'<div class="empty">Não há equipe convocada nesta unidade em '+formatDate(date)+'. Escolha outra data de referência ou monte a equipe abaixo.</div>';
      $('#previous-team-use').disabled=!ids.length;
    };
    $('#previous-team-date').onchange=previewPrevious;$('#unit-conv-unit').onchange=previewPrevious;$('#unit-conv-turn').onchange=previewPrevious;previewPrevious();
    $('#previous-team-use').onclick=()=>{const ids=$$('.previous-team-person:checked').filter(x=>!x.disabled).map(x=>x.value);if(!ids.length)return toast('Nenhuma pessoa disponível foi selecionada.',true);selected.clear();ids.forEach(id=>selected.add(id));$('#unit-conv-function').value='Todas';$('#unit-conv-search').value='';refresh(false);toast('Equipe carregada. Você pode desmarcar pessoas antes de confirmar.');};
    $('#unit-conv-date').onchange=()=>{unitConvDate=$('#unit-conv-date').value;render();};
    const avulsoList=()=>$('#unit-avulso-list').innerHTML=avulsoDraft.map(x=>`<div class="team-list-item">${escapeHtml(x.nome)} · ${escapeHtml(x.funcao)}</div>`).join('');avulsoList();
    $('#unit-avulso-add').onclick=()=>{const nome=$('#unit-avulso-name').value.trim();if(!nome)return toast('Informe o nome.',true);avulsoDraft.push({id:uid('c'),nome,funcao:$('#unit-avulso-function').value.trim()||'Avulso',avulso:$('#unit-avulso-check').checked?'Sim':'Não',custo:180});$('#unit-avulso-name').value='';$('#unit-avulso-function').value='';avulsoList();};
    $('#unit-conv-form').onsubmit=e=>{e.preventDefault();$$('#unit-conv-people input').forEach(x=>x.checked?selected.add(x.value):selected.delete(x.value));const ids=[...selected,...avulsoDraft.map(x=>x.id)],date=$('#unit-conv-date').value,turno=$('#unit-conv-turn').value,unit=$('#unit-conv-unit').value;if(!ids.length)return toast('Selecione pelo menos uma pessoa.',true);const conflict=ids.find(id=>blocked(id,date)||state.convocacoes.some(c=>c.dataServico===date&&c.colaboradores.includes(id)&&overlaps(c.turno,turno)));if(conflict){registerConvocationConflicts(ids,date,turno,unit,supervisorAtual);return toast('Colaborador indisponível ou já convocado neste turno: '+(colaboradorById(conflict)?.nome||conflict),true);}COLABORADORES.push(...avulsoDraft);state.convocacoes.push({id:uid('cv'),supervisor:supervisorAtual,dataServico:date,unidade:unit,obraId:'',turno,colaboradores:ids,criadoEm:now().toISOString(),origem:'normal',executor:supervisorAtual});avulsoDraft=[];audit('Convocação da equipe',date);saveData();toast('Equipe convocada. Serviços serão escolhidos no apontamento.');render();};
  }

  function operationalRows(convs){return convs.flatMap(c=>c.colaboradores.map(id=>({c,p:colaboradorById(id),i:(apForConv(c.id)?.itens||[]).find(i=>i.colaboradorId===id),id})));}
  function readableName(value){return String(value||'').toLocaleLowerCase('pt-BR').split(/\s+/).map((v,i)=>i&&['da','das','de','do','dos','e'].includes(v)?v:v.charAt(0).toLocaleUpperCase('pt-BR')+v.slice(1)).join(' ');}
  function unitTitle(u){return ['SEBRAE','UNIFOR','FIEC','PARTICULAR'].includes(clean(u))?clean(u):readableName(u);}
  async function copyText(id){const el=$('#'+id);try{await navigator.clipboard.writeText(el.value);toast('Mensagem copiada.');}catch{el.select();toast('Use Ctrl+C para copiar a mensagem selecionada.');}}
  function renderWhatsApp(){
    $('#main-content').innerHTML=head('WhatsApp','Gere a mensagem de convocação já organizada para copiar e enviar aos grupos.')+`<div class="form-grid">${field('Data da divisão',`<input id="wp-data" class="control" type="date" value="${isoToday()}">`)}${field('','<label><input id="wp-func" type="checkbox"> Mostrar função entre parênteses</label>')}</div><div id="wp-missing" class="section"></div><label class="section" style="display:block"><input id="wp-pend" type="checkbox" checked> Ainda existem demandas que serão enviadas por outros responsáveis</label><h3 class="section">Mensagem completa</h3><p>Copie o texto abaixo e cole no WhatsApp.</p><textarea id="wp-text" class="control message-box" readonly></textarea><button class="btn btn-secondary section" id="wp-copy">Copiar mensagem completa</button><h3 class="section">Mensagem separada por unidade</h3><p>Caso prefira enviar a divisão de cada unidade separadamente.</p><div id="wp-units"></div><p class="section">A mensagem usa somente a unidade da convocação. Obra e serviço não são exibidos.</p>`;
    const update=()=>{const date=$('#wp-data').value,convs=state.convocacoes.filter(c=>c.dataServico===date),group={};for(const {c,p} of operationalRows(convs)){const names=(group[c.unidade]??={})[c.turno]??=new Set();names.add(readableName(p?.nome)+($('#wp-func').checked?' ('+readableName(p?.funcao)+')':''));}const units=Object.keys(group).sort((a,b)=>clean(a).localeCompare(clean(b)));const next=dateLocal(isoToday());next.setDate(next.getDate()+1);const label=date===isoToday()?'hoje':date===calendarISO(next)?'amanhã':'o dia';const message=u=>{let n=1;const turns=Object.keys(group[u]).sort((a,b)=>['Integral','Manhã','Tarde','Noite'].indexOf(a)-['Integral','Manhã','Tarde','Noite'].indexOf(b));return '*'+unitTitle(u)+'*\n\n'+turns.map(t=>(turns.length>1||t!=='Integral'?'_'+t+'_\n':'')+[...group[u][t]].sort().map(name=>n+++'. '+name).join('\n')).join('\n\n');};const prefix='Segue divisão de Equipes para '+label+' '+formatDate(date).slice(0,5)+'\n\n';$('#wp-text').value=prefix+units.map(message).join('\n\n')+($('#wp-pend').checked?'\n\nAs demais demandas serão enviadas pelos respectivos responsáveis.':'');const missing=[...new Set(OBRAS.map(o=>o.unidade))].filter(u=>!units.includes(u));$('#wp-missing').innerHTML=`<div class="notice success">${operationalRows(convs).length} convocação(ões) encontrada(s) em ${units.length} unidade(s).</div><details class="card card-pad section"><summary>Unidades sem convocação registrada nesta data</summary><p>${escapeHtml(missing.join(', ')||'Nenhuma')}</p></details>`;$('#wp-units').innerHTML=units.map((u,index)=>`<details class="card card-pad section"><summary>${escapeHtml(unitTitle(u))}</summary><textarea class="control message-box" id="wp-unit-${index}" readonly>${escapeHtml(prefix+message(u))}</textarea><button class="btn btn-secondary section" data-copy-unit="${index}">Copiar mensagem</button></details>`).join('');$$('[data-copy-unit]').forEach(b=>b.onclick=()=>copyText('wp-unit-'+b.dataset.copyUnit));};['wp-data','wp-func','wp-pend'].forEach(id=>$('#'+id).onchange=update);$('#wp-copy').onclick=()=>copyText('wp-text');update();
  }
  let indicatorUnit='Todas',indicatorSup=SUPERVISORES[0],indicatorOnlyLate=true;
  function renderIndicators(){
    $('#main-content').innerHTML=head('Indicadores','Acompanhe prazos, ausências e comportamento operacional das equipes.')+`<div class="reference-filters">${field('Início',`<input class="control" id="ix-start" type="date" value="${reportFilters.inicio}">`)}${field('Fim',`<input class="control" id="ix-end" type="date" value="${reportFilters.fim}">`)}${field('Unidade',`<select class="control" id="ix-unit">${options(['Todas',...[...new Set(OBRAS.map(o=>o.unidade))]])}</select>`)}</div><div id="indicator-body" class="section"></div><div class="form-actions"><button id="ix-excel" class="btn btn-secondary">Baixar indicador de prazos em Excel</button><button id="ix-pdf" class="btn btn-primary">Baixar relatório executivo em PDF</button></div>`;$('#ix-unit').value=indicatorUnit;
    const refresh=()=>{reportFilters.inicio=$('#ix-start').value;reportFilters.fim=$('#ix-end').value;indicatorUnit=$('#ix-unit').value;if(reportFilters.fim<reportFilters.inicio)return toast('O fim deve ser igual ou posterior ao início.',true);const cv=state.convocacoes.filter(c=>c.dataServico>=reportFilters.inicio&&c.dataServico<=reportFilters.fim&&(indicatorUnit==='Todas'||c.unidade===indicatorUnit));const ids=new Set(cv.map(c=>c.id));const ap=state.apontamentos.filter(a=>ids.has(a.convocacaoId));const count=rows=>new Set(rows.map(x=>x.dataServico)).size;const summary=SUPERVISORES.map(s=>{const own=cv.filter(c=>c.supervisor===s&&(c.executor||s)===s),pointed=ap.filter(a=>a.supervisor===s&&(a.executor||s)===s),n=count(own),late=count(own.filter(convocacaoAtrasada));return [s,n,late,count(pointed),count(pointed.filter(apontamentoAtrasado)),n?((n-late)/n*100).toFixed(1)+'%':'—'];});const records=operationalRows(cv);const absent=records.filter(x=>['Falta','Atestado'].includes(x.i?.status));const impact=xs=>xs.reduce((v,x)=>v+dayCost(x.p),0);const ranking=new Map();absent.filter(x=>x.i.status==='Falta').forEach(x=>ranking.set(x.p?.nome||x.id,(ranking.get(x.p?.nome||x.id)||0)+1));const days=['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];const weekday=days.map((d,i)=>({d,f:absent.filter(x=>dateLocal(x.c.dataServico).getDay()===i&&x.i.status==='Falta').length,a:absent.filter(x=>dateLocal(x.c.dataServico).getDay()===i&&x.i.status==='Atestado').length}));const max=Math.max(1,...weekday.map(x=>x.f+x.a));const chart=`<div class="absence-chart" role="img" aria-label="Ausências por dia da semana">${weekday.map(x=>`<div class="chart-column"><div class="chart-track"><div title="${x.d}: ${x.a} atestados, ${x.f} faltas" style="height:${(x.f+x.a)/max*100}%;display:flex;flex-direction:column"><div style="background:#0068c9;flex:${x.a}"></div><div style="background:#83c9ff;flex:${x.f}"></div></div></div><small>${x.d}</small><strong>${x.f+x.a}</strong></div>`).join('')}</div><p class="chart-legend"><span style="color:#0068c9">■ Atestado</span> <span style="color:#54aceb">■ Falta</span></p>`;const unitRows=[...new Set(records.map(x=>x.c.unidade))].map(u=>{const xs=records.filter(x=>x.c.unidade===u),f=xs.filter(x=>x.i?.status==='Falta').length,a=xs.filter(x=>x.i?.status==='Atestado').length;return [u,xs.length,f,a,f+a,((f+a)/xs.length*100).toFixed(1)+'%',money(impact(xs.filter(x=>['Falta','Atestado'].includes(x.i?.status))))];}).sort((a,b)=>parseFloat(b[5])-parseFloat(a[5]));const missing=diasSemConvocacao(SUPERVISORES,reportFilters.inicio,reportFilters.fim);const gaps=SUPERVISORES.map(s=>{const dates=indicatorUnit==='Todas'?missing.filter(x=>x.supervisor===s).map(x=>x.dataServico):[];const noAp=[...new Set(cv.filter(c=>c.supervisor===s&&!completeConv(c)&&now()>=deadlineApontamento(c.dataServico)).map(c=>c.dataServico))];return [s,indicatorUnit==='Todas'?dates.length:'—',noAp.length,dates.map(formatDate).join(', ')||(indicatorUnit==='Todas'?'Nenhum':'Selecione Todas para esta conferência'),noAp.map(formatDate).join(', ')||'Nenhum'];}).sort((a,b)=>Number(b[1])-Number(a[1]));
      $('#indicator-body').innerHTML=`<h3>Cumprimento por supervisor</h3><p>Cada dia com convocação conta como uma convocação por supervisor. Sábados e domingos não geram atraso automático.</p>${table(['Supervisor','Convocações feitas','Convocações atrasadas','Apontamentos feitos','Apontamentos atrasados','No prazo (%)'],summary)}<h3 class="section">Ver datas e ocorrências</h3>${field('Supervisor para detalhar',`<select class="control" id="ix-sup">${options(SUPERVISORES)}</select>`)}<label style="display:block;margin:12px 0"><input type="checkbox" id="ix-late" ${indicatorOnlyLate?'checked':''}> Mostrar somente atrasos</label><div id="ix-events"></div><h3 class="section">Absenteísmo</h3><p>Faltas, atestados e impacto por colaborador, dia e unidade.</p><div class="grid grid-5">${metric('Convocações',records.length,'colaboradores convocados')}${metric('Faltas',absent.filter(x=>x.i.status==='Falta').length,'confirmadas')}${metric('Atestados',absent.filter(x=>x.i.status==='Atestado').length,'registrados')}${metric('Absenteísmo',records.length?(absent.length/records.length*100).toFixed(1)+'%':'0%','ausências / convocações')}${metric('Impacto est.',money(impact(absent)),'diárias-base das ausências')}</div><p>Impacto estimado = soma das diárias-base associadas às faltas e atestados.</p><div class="grid grid-2 section"><div><h3>Colaboradores com mais faltas</h3><div class="limited-table absence-ranking">${table(['Posição','Colaborador','Quantidade de faltas'],[...ranking].sort((a,b)=>b[1]-a[1]).map(([n,v],i)=>[i+1,escapeHtml(n),v]))}</div></div><div><h3>Ausências por dia da semana</h3><div class="card card-pad">${chart}</div></div></div><h3 class="section">Detalhamento por unidade</h3>${table(['Unidade','Convocações','Faltas','Atestados','Total ausências','Taxa absenteísmo (%)','Impacto estimado (R$)'],unitRows)}<h3 class="section">Supervisores sem convocações registradas</h3><p>Convocações e apontamentos não realizados, com as respectivas datas. Felipe é considerado a partir de 28/09/2026.</p>${table(['Supervisor','Conv. não feitas','Apt. não feitos','Dias sem convocação','Dias sem apontamento'],gaps)}`;
      const events=()=>{indicatorSup=$('#ix-sup').value;indicatorOnlyLate=$('#ix-late').checked;const rows=[];for(const c of cv.filter(c=>c.supervisor===indicatorSup)){const late=convocacaoAtrasada(c);if(!indicatorOnlyLate||late)c.colaboradores.forEach(id=>rows.push([c.supervisor,formatDate(c.dataServico),escapeHtml(colaboradorById(id)?.nome),'Convocação',formatDateTime(c.criadoEm),late?'SIM':'NÃO']));const a=apForConv(c.id);if(a){const lateAp=apontamentoAtrasado(a);if(!indicatorOnlyLate||lateAp)a.itens.forEach(i=>rows.push([c.supervisor,formatDate(c.dataServico),escapeHtml(colaboradorById(i.colaboradorId)?.nome),'Apontamento',formatDateTime(a.apontadoEm),lateAp?'SIM':'NÃO']));}}$('#ix-events').innerHTML=table(['Supervisor','Data do serviço','Colaborador','Tipo','Registrado em','Atrasado'],rows);};$('#ix-sup').value=indicatorSup;$('#ix-sup').onchange=events;$('#ix-late').onchange=events;events();};['ix-start','ix-end','ix-unit'].forEach(id=>$('#'+id).onchange=refresh);$('#ix-pdf').onclick=()=>reportPDF('executive');$('#ix-excel').onclick=()=>exportWorkbook(indicatorWorkbook(),'indicador_prazos_'+reportFilters.inicio+'_a_'+reportFilters.fim);refresh();
  }

  let homeDate=isoToday(),homeUnit='Todas',homeSup='Todos';
  function renderControladoriaInicio(){
    $('#main-content').innerHTML=head('Visão do dia','O que precisa de atenção e como está a equipe hoje.')+`<div class="reference-filters home-filters">${field('Data',`<input class="control" id="home-date" type="date" value="${homeDate}">`)}${field('Unidade',`<select class="control" id="home-unit">${options(['Todas',...[...new Set(OBRAS.map(o=>o.unidade))]])}</select>`)}${field('Supervisor',`<select class="control" id="home-sup">${options(['Todos',...SUPERVISORES])}</select>`)}<button class="btn btn-primary" id="home-refresh">Atualizar</button></div><div id="home-body" class="section"></div>`;$('#home-unit').value=homeUnit;$('#home-sup').value=homeSup;const refresh=()=>{homeDate=$('#home-date').value;homeUnit=$('#home-unit').value;homeSup=$('#home-sup').value;const match=c=>(homeUnit==='Todas'||c.unidade===homeUnit)&&(homeSup==='Todos'||c.supervisor===homeSup);const cv=state.convocacoes.filter(c=>c.dataServico===homeDate&&match(c)),rows=operationalRows(cv),pointed=rows.filter(x=>x.i),pending=rows.filter(x=>!x.i),absent=pointed.filter(x=>['Falta','Atestado'].includes(x.i.status));const next=dateLocal(homeDate);next.setDate(next.getDate()+1);const tomorrow=operationalRows(state.convocacoes.filter(c=>c.dataServico===calendarISO(next)&&match(c))).length;const conflicts=convocationConflictRows().filter(x=>!x.resolvido&&x.dataServico===homeDate&&(homeUnit==='Todas'||x.unidade===homeUnit||x.unidadeExistente===homeUnit)&&(homeSup==='Todos'||x.supervisor===homeSup||x.supervisorExistente===homeSup));$('#home-body').innerHTML=`<div class="grid grid-5 home-metrics">${metric('Equipe hoje',rows.length,'convocados na data')}${metric('Apontados',pointed.length,rows.length?(pointed.length/rows.length*100).toFixed(0)+'% da equipe':'sem equipe')}${metric('Pendentes do dia',pending.length,'ainda sem apontamento')}<button type="button" class="card metric clickable-metric" id="home-absences-button" aria-controls="home-absences" aria-expanded="false"><span class="metric-label">Faltas / Atestados</span><span class="metric-value">${absent.length}</span><span class="metric-note">Ver colaboradores →</span></button>${metric('Convocados amanhã',tomorrow,formatDate(calendarISO(next)))}</div><div class="grid grid-2 section home-attention"><div class="card card-pad"><h3>Precisa de atenção</h3><div class="notice ${pending.length?'warning':'success'}">${pending.length?pending.length+' apontamento(s) pendente(s).':'Nenhum apontamento pendente.'}<br>O registro só fica atrasado após o prazo do apontamento. Não selecionar uma pessoa não registra falta.</div></div><div class="card card-pad"><h3>Conflitos</h3><div class="notice ${conflicts.length?'warning':'success'}">${conflicts.length?'<strong>'+conflicts.length+(conflicts.length===1?' tentativa bloqueada':' tentativas bloqueadas')+'</strong><details class="home-conflict-details"><summary>Ver colaboradores e responsáveis</summary>'+conflicts.map(x=>'<div class="conflict-summary-item"><strong>'+escapeHtml(x.colaboradorNome||colaboradorById(x.colaboradorId)?.nome)+'</strong><br>'+escapeHtml(x.supervisor)+' tentou convocar para '+escapeHtml(x.unidade)+' ('+escapeHtml(x.turno)+').<br>Já convocado por '+escapeHtml(x.supervisorExistente)+' para '+escapeHtml(x.unidadeExistente)+' ('+escapeHtml(x.turnoExistente)+').</div>').join('')+'</details>':'Nenhum conflito pendente.'}</div></div></div><details id="home-absences" class="card card-pad section"><summary>Faltas e atestados · ${absent.length}</summary>${absent.length?table(['Colaborador','Situação','Unidade','Supervisor','Turno','Observação'],absent.map(x=>[escapeHtml(x.p?.nome),`<span class="badge ${x.i.status==='Falta'?'danger':'warning'}">${escapeHtml(x.i.status)}</span>`,escapeHtml(x.c.unidade),escapeHtml(x.c.supervisor),escapeHtml(x.c.turno),escapeHtml(x.i.observacao||'Sem observação')])):'<div class="empty">Nenhuma falta ou atestado nos filtros selecionados.</div>'}</details><details class="card card-pad section"><summary>Ver apontamentos pendentes · ${pending.length}</summary>${table(['Colaborador','Unidade','Supervisor','Turno','Situação'],pending.map(x=>[escapeHtml(x.p?.nome),escapeHtml(x.c.unidade),x.c.supervisor,x.c.turno,now()>=deadlineApontamento(x.c.dataServico)?'Prazo vencido':'Pendente do dia']))}</details><h3 class="section">Ações rápidas</h3><div class="inline-actions">${[['convocacao','Nova convocação'],['apontamento','Apontamentos'],['disponibilidade','Disponibilidade'],['indicadores','Indicadores']].map(([v,t])=>`<button class="btn btn-outline" data-admin-go="${v}">${t}</button>`).join('')}</div>`;$('#home-absences-button').onclick=()=>{const panel=$('#home-absences');panel.open=!panel.open;$('#home-absences-button').setAttribute('aria-expanded',String(panel.open));if(panel.open)panel.scrollIntoView({behavior:'smooth',block:'nearest'});};$('#home-absences').ontoggle=()=>$('#home-absences-button').setAttribute('aria-expanded',String($('#home-absences').open));$$('[data-admin-go]').forEach(b=>b.onclick=()=>setView(b.dataset.adminGo));};$('#home-refresh').onclick=refresh;refresh();
  }
  function renderConvCompleta(){if(perfilAtual==='SUPERVISOR')return renderUnitConvocacao();if(perfilAtual!=='CONTROLADORIA')return renderConvCompletaBase();renderAdminConv(false);}
  let adminConvDate=calendarISO(nextBusinessDay(isoToday())),adminEditDate=isoToday();
  function adminUnits(){return [...new Set(OBRAS.map(o=>o.unidade))].sort();}
  function renderAdminConv(edit){const content=$('#main-content');content.innerHTML=head('Convocação','Monte a equipe e faça correções administrativas quando necessário. Os serviços são definidos no apontamento.')+`<div class="tabs"><button id="admin-new" class="tab-btn ${!edit?'active':''}">Nova convocação</button><button id="admin-edit" class="tab-btn ${edit?'active':''}">Correção / Exclusão administrativa</button></div><div id="admin-conv-body" class="section"></div>`;$('#admin-new').onclick=()=>renderAdminConv(false);$('#admin-edit').onclick=()=>renderAdminConv(true);const body=$('#admin-conv-body');
    if(!edit){body.innerHTML=`<form id="admin-conv-form"><div class="reference-filters">${field('Supervisor responsável',`<select class="control" id="ac-sup">${options(SUPERVISORES)}</select>`)}${field('Data da convocação',`<input class="control" type="date" id="ac-date" value="${adminConvDate}" required>`)}${field('Turno',`<select class="control" id="ac-turn">${options(['Integral','Manhã','Tarde','Noite'])}</select>`)}</div>${field('Unidade',`<select class="control" id="ac-unit">${options(adminUnits())}</select>`)}${field('Filtrar por função (opcional)',`<select class="control" id="ac-function">${options(['Todas',...[...new Set(COLABORADORES.filter(c=>!c.inativo).map(c=>c.funcao))]])}</select>`)}${field('Buscar colaboradores cadastrados','<input class="control" id="ac-search" placeholder="Nome ou função">')}<div id="ac-people" class="rect-list section"></div><details class="card card-pad section"><summary>Incluir nome digitado</summary><div class="form-grid">${field('Nome','<input class="control" id="ac-name">')}${field('Função','<input class="control" id="ac-role">')}</div><label><input type="checkbox" id="ac-loose"> É avulso?</label></details><div id="ac-panorama" class="card card-pad section"></div><div class="form-actions"><button class="btn btn-primary">Confirmar convocação</button></div></form>`;const selected=new Set();const people=()=>{$$('#ac-people input').forEach(x=>x.checked?selected.add(x.value):selected.delete(x.value));const term=clean($('#ac-search').value),role=$('#ac-function').value;$('#ac-people').innerHTML=COLABORADORES.filter(c=>!c.inativo&&clean(c.nome+' '+c.funcao).includes(term)&&(role==='Todas'||c.funcao===role)).map(c=>`<label class="check-card"><input type="checkbox" value="${c.id}" ${selected.has(c.id)?'checked':''}><span>${escapeHtml(c.nome)}<small style="display:block">${escapeHtml(c.funcao)}</small></span></label>`).join('');};const panorama=()=>{const cv=state.convocacoes.filter(c=>c.dataServico===$('#ac-date').value&&c.supervisor===$('#ac-sup').value);$('#ac-panorama').innerHTML='<strong>Panorama de '+$('#ac-sup').value+' · '+formatDate($('#ac-date').value)+' · '+$('#ac-turn').value+'</strong>'+table(['Colaborador','Unidade','Turno'],operationalRows(cv).map(x=>[escapeHtml(x.p?.nome),escapeHtml(x.c.unidade),x.c.turno]));};$('#ac-search').oninput=people;$('#ac-function').onchange=people;['ac-date','ac-sup','ac-turn'].forEach(id=>$('#'+id).onchange=panorama);people();panorama();$('#admin-conv-form').onsubmit=e=>{e.preventDefault();$$('#ac-people input').forEach(x=>x.checked?selected.add(x.value):selected.delete(x.value));const date=$('#ac-date').value,turno=$('#ac-turn').value,unit=$('#ac-unit').value,sup=$('#ac-sup').value;const ids=[...selected];const name=$('#ac-name').value.trim();let manual;if(name){manual=COLABORADORES.find(c=>clean(c.nome)===clean(name)&&!c.inativo)||{id:uid('c'),nome:name,funcao:$('#ac-role').value.trim()||'Avulso',avulso:$('#ac-loose').checked?'Sim':'Não',custo:0};if(!ids.includes(manual.id))ids.push(manual.id);}if(!ids.length)return toast('Selecione pelo menos um colaborador.',true);const conflict=ids.find(id=>blocked(id,date)||state.convocacoes.some(c=>c.dataServico===date&&c.colaboradores.includes(id)&&overlaps(c.turno,turno)));if(conflict){registerConvocationConflicts(ids,date,turno,unit,sup);return toast('Convocação bloqueada por conflito ou indisponibilidade: '+(colaboradorById(conflict)?.nome||name),true);}if(manual&&!colaboradorById(manual.id))COLABORADORES.push(manual);state.convocacoes.push({id:uid('cv'),supervisor:sup,dataServico:date,unidade:unit,obraId:'',turno,colaboradores:ids,criadoEm:now().toISOString(),executor:'CONTROLADORIA',origem:'administrativa'});adminConvDate=date;audit('Convocação administrativa',date);saveData();toast('Equipe convocada.');renderAdminConv(false);};
    }else{body.innerHTML=`<h3>Correção / Exclusão administrativa</h3><p>Realocar um colaborador para outra unidade ou excluir uma convocação lançada incorretamente.</p><div class="form-grid">${field('Data da convocação para corrigir',`<input class="control" id="ae-date" type="date" value="${adminEditDate}">`)}${field('Selecione o colaborador / convocação','<select class="control" id="ae-record"></select>')}</div><details class="card card-pad section"><summary>Excluir várias convocações de uma vez</summary><div id="ae-bulk" class="rect-list section"></div><label><input id="ae-confirm-bulk" type="checkbox"> Confirmo a exclusão dos registros selecionados</label><div class="form-actions"><button class="btn btn-secondary" id="ae-delete-bulk">Excluir selecionadas</button></div></details><div id="ae-editor" class="section"></div>`;let rows=[];const renderEditor=()=>{const x=rows[Number($('#ae-record').value)];if(!x){$('#ae-editor').innerHTML='<div class="empty">Nenhuma convocação nesta data.</div>';return;}$('#ae-editor').innerHTML=`<form id="ae-form"><p>Colaborador: <strong>${escapeHtml(x.p?.nome)}</strong></p><div class="reference-filters">${field('Unidade de destino',`<select class="control" id="ae-unit">${options(adminUnits())}</select>`)}${field('Obra / Serviço de destino','<select class="control" id="ae-work"></select>')}${field('Supervisor responsável',`<select class="control" id="ae-sup">${options(SUPERVISORES)}</select>`)}</div><div class="form-grid">${field('Data',`<input class="control" id="ae-target-date" type="date" value="${x.c.dataServico}" required>`)}${field('Turno',`<select class="control" id="ae-turn">${options(['Integral','Manhã','Tarde','Noite'])}</select>`)}</div><div class="form-actions"><button class="btn btn-primary">Salvar realocação</button><button type="button" id="ae-delete" class="btn btn-secondary">Excluir convocação deste colaborador</button></div></form>`;$('#ae-unit').value=x.c.unidade;$('#ae-sup').value=x.c.supervisor;$('#ae-turn').value=x.c.turno;const works=()=>{$('#ae-work').innerHTML='<option value="">A definir no apontamento</option>'+options(OBRAS.filter(o=>o.unidade===$('#ae-unit').value));};$('#ae-unit').onchange=works;works();$('#ae-work').value=x.c.obraId||'';$('#ae-delete').onclick=()=>{removeConvPerson(x.c.id,x.id);audit('Exclusão administrativa',x.id);saveData();refresh();};$('#ae-form').onsubmit=e=>{e.preventDefault();const date=$('#ae-target-date').value,turno=$('#ae-turn').value;if(blocked(x.id,date)||state.convocacoes.some(c=>c.id!==x.c.id&&c.dataServico===date&&c.colaboradores.includes(x.id)&&overlaps(c.turno,turno)))return toast('A realocação geraria conflito.',true);const ap=apForConv(x.c.id),item=ap?.itens.find(i=>i.colaboradorId===x.id);const newid=uid('cv');const next={...x.c,id:newid,colaboradores:[x.id],dataServico:date,supervisor:$('#ae-sup').value,unidade:$('#ae-unit').value,obraId:$('#ae-work').value,turno,corrigidoPor:'CONTROLADORIA'};removeConvPerson(x.c.id,x.id);state.convocacoes.push(next);if(item){if(next.unidade!==x.c.unidade||next.obraId!==x.c.obraId){item.servicos=next.obraId?[{obraId:next.obraId,periodo:turno}]:[];}state.apontamentos.push({...ap,id:uid('ap'),convocacaoId:newid,dataServico:date,supervisor:next.supervisor,itens:[item]});}audit('Realocação administrativa',x.id);saveData();toast('Realocação salva.');refresh();};};const refresh=()=>{adminEditDate=$('#ae-date').value;rows=operationalRows(state.convocacoes.filter(c=>c.dataServico===adminEditDate));$('#ae-record').innerHTML=rows.map((x,index)=>`<option value="${index}">${escapeHtml(x.p?.nome)} | ${escapeHtml(x.c.unidade)} | ${escapeHtml(obraById(x.c.obraId)?.nome||'Obra/Serviço a definir')} | Eng: ${x.c.supervisor}</option>`).join('');$('#ae-bulk').innerHTML=rows.map((x,index)=>`<label class="check-card"><input type="checkbox" class="ae-bulk-person" value="${index}"><span>${escapeHtml(x.p?.nome)} · ${escapeHtml(x.c.unidade)} · ${x.c.turno}</span></label>`).join('');renderEditor();};$('#ae-date').onchange=refresh;$('#ae-record').onchange=renderEditor;$('#ae-delete-bulk').onclick=()=>{if(!$('#ae-confirm-bulk').checked)return toast('Confirme a exclusão dos selecionados.',true);const indices=$$('.ae-bulk-person:checked').map(el=>Number(el.value));if(!indices.length)return toast('Selecione os registros.',true);indices.forEach(i=>removeConvPerson(rows[i].c.id,rows[i].id));audit('Exclusão administrativa em lote',String(indices.length));saveData();refresh();};refresh();}
  }
  function removeConvPerson(cvId,id){const c=state.convocacoes.find(c=>c.id===cvId);if(!c)return;c.colaboradores=c.colaboradores.filter(v=>v!==id);const ap=apForConv(cvId);if(ap)ap.itens=ap.itens.filter(i=>i.colaboradorId!==id);if(!c.colaboradores.length){state.convocacoes=state.convocacoes.filter(c=>c.id!==cvId);state.apontamentos=state.apontamentos.filter(a=>a.convocacaoId!==cvId);}}
  function renderSettings(){
    renderSettingsBase();const main=$('#main-content');const trello=main.querySelector('details.section');if(trello){trello.outerHTML=`<div class="card card-pad section"><h3>Sincronização com o Trello</h3><p>A lista principal é <strong>EM EXECUÇÃO</strong>. No sistema conectado, a sincronização ocorre a cada 12 horas.</p><div class="form-grid"><div><button id="trello-main" class="btn btn-primary">Sincronizar EM EXECUÇÃO agora</button></div>${field('Selecionar lista diretamente',`<select class="control" id="trello-list">${options(['SOLICITADOS - PENDÊNCIAS CLIENTE','EM EXECUÇÃO','CONCLUÍDOS'])}</select><button class="btn btn-primary section" id="trello-selected">Sincronizar lista selecionada</button>`)}</div><h3 class="section">Busca manual para medições retroativas</h3>${field('Buscar card ou lista por nome','<input class="control" id="trello-search" placeholder="Ex.: MEDIÇÃO JUNHO 2026, MARACANAÚ…">')}<div id="trello-results"></div><div class="notice info section">A sincronização consulta o Trello em tempo real e atualiza o Neon. Nenhuma obra existente é apagada.</div></div>`;
    const listSelect=$('#trello-list'),cardResults=$('#trello-results'),cardSearch=$('#trello-search');
    let remoteCards=[];
    async function runTrelloSync(payload){
      if(onlineSaving||onlineQueued)return showToast('Aguarde a gravação em andamento.',true);
      if(!onlineWritable||onlineSession?.role!=='CONTROLADORIA')return showToast('A sincronização só está disponível à Controladoria na homologação com gravação habilitada.',true);
      if(!window.confirm('Sincronizar as obras do Trello com o banco de homologação? Nenhuma obra será excluída.'))return;
      lockOnline(true);
      try{
        const result=await api('/api/trello/sync',{method:'POST',body:JSON.stringify(payload)});
        applyOnline(await api('/api/bootstrap'));render();
        showToast('Trello sincronizado: '+result.novas+' nova(s), '+result.atualizadas+' atualizada(s), '+result.jaExistentes+' sem alteração, '+(result.ignoradas?.length||0)+' para conferência.');
      }catch(e){showToast('Falha ao sincronizar Trello: '+e.message,true);}
      finally{lockOnline(false);}
    }
    $('#trello-main').onclick=()=>runTrelloSync({});
    $('#trello-selected').onclick=()=>runTrelloSync({listId:listSelect.value});
    const liveResults=()=>{
      const term=clean(cardSearch.value),matches=term?remoteCards.filter(c=>clean(c.name+' '+c.unidade).includes(term)).slice(0,30):[];
      cardResults.innerHTML=term?'<div class="section">'+(matches.length?matches.map(c=>'<div class="team-list-item"><strong>'+escapeHtml(c.name)+'</strong><small>'+escapeHtml(c.unidade||'NÃO IDENTIFICADA')+'</small><button type="button" class="link-btn" data-trello-card="'+escapeHtml(c.id)+'">Importar este card</button></div>').join(''):'Nenhum card correspondente no quadro.')+'</div>':'';
      $('[data-trello-card]').forEach(b=>b.onclick=()=>runTrelloSync({cardId:b.dataset.trelloCard}));
    };
    (async()=>{
      try{
        cardResults.innerHTML='<p>Consultando o Trello...</p>';
        const board=await api('/api/trello/lists');
        if(!document.body.contains(listSelect))return;
        const desired=listSelect.options[listSelect.selectedIndex]?.text||'EM EXECUÇÃO';
        listSelect.replaceChildren(...board.lists.map(l=>{const opt=document.createElement('option');opt.value=l.id;opt.textContent=l.name;opt.selected=l.name===desired;return opt;}));
        if(![...listSelect.options].some(o=>o.selected))listSelect.selectedIndex=Math.max(0,board.lists.findIndex(l=>clean(l.name)==='EM EXECUCAO'));
        remoteCards=board.cards||[];
        cardSearch.oninput=liveResults;liveResults();
      }catch(e){if(document.body.contains(listSelect))cardResults.innerHTML='<div class="notice warning">'+escapeHtml('O Trello não respondeu: '+e.message)+'</div>';}
    })();$('#trello-search').oninput=()=>{const term=clean($('#trello-search').value);$('#trello-results').innerHTML=term?table(['Obra','Unidade'],OBRAS.filter(o=>clean(o.nome+' '+o.unidade).includes(term)).map(o=>[escapeHtml(o.nome),escapeHtml(o.unidade)])):'';};}
    const body=$('#settings-body');
    if(settingsTab==='Colaboradores'){const form=$('#colab-form');const wrapper=document.createElement('details');wrapper.className='card card-pad';wrapper.innerHTML='<summary>Cadastrar novo funcionário / editar cadastro</summary>';form.before(wrapper);wrapper.appendChild(form);form.className='section';body.insertAdjacentHTML('afterbegin','<h3>Banco de funcionários</h3><p>Cadastre, consulte, edite ou retire colaboradores da base operacional. A exclusão inativa o cadastro para preservar o histórico.</p>');const search=$('#colab-search');search.parentElement.insertAdjacentHTML('beforeend',field('Moradia',`<select id="colab-home-filter" class="control">${options(['Todas','Não informado','Fortaleza','Maracanaú','Caucaia','Horizonte'])}</select>`));let page=0;const pendingHomes=new Map();const refresh=()=>{const term=clean(search.value),home=$('#colab-home-filter').value;const rows=COLABORADORES.filter(c=>!c.inativo&&clean(c.nome+' '+c.funcao).includes(term)&&(home==='Todas'||(c.moradia||'Não informado')===home));const pages=Math.max(1,Math.ceil(rows.length/12));page=Math.min(page,pages-1);$('#colab-table').innerHTML=`<div class="section-title"><strong>${rows.length} funcionário(s) encontrado(s)</strong><div class="inline-actions"><button class="btn btn-secondary" id="colab-prev" ${page===0?'disabled':''}>Anterior</button><span>${page+1} / ${pages}</span><button class="btn btn-secondary" id="colab-next" ${page===pages-1?'disabled':''}>Próxima</button></div></div>`+table(['Nome','Função','Valor diário','Moradia','Ações'],rows.slice(page*12,page*12+12).map(c=>[escapeHtml(c.nome),escapeHtml(c.funcao),money(dayCost(c)),`<select class="control" data-home-colab="${c.id}">${options(['Não informado','Fortaleza','Maracanaú','Caucaia','Horizonte',...(!['Fortaleza','Maracanaú','Caucaia','Horizonte'].includes(c.moradia)&&c.moradia?[c.moradia]:[])])}</select>`,`<button class="link-btn" data-new-edit="${c.id}">Editar</button> <button class="link-btn danger-link" data-inactivate="${c.id}">Excluir</button>`]))+`<div class="form-actions"><button class="btn btn-primary" id="save-homes">Salvar alterações de moradia</button></div><details class="card card-pad section"><summary>Funcionários excluídos · ${COLABORADORES.filter(c=>c.inativo).length}</summary>${table(['Nome','Função','Ação'],COLABORADORES.filter(c=>c.inativo).map(c=>[escapeHtml(c.nome),escapeHtml(c.funcao),`<button class="link-btn" data-reactivate="${c.id}">Reativar</button>`]))}</details>`;$('#colab-prev').onclick=()=>{page--;refresh();};$('#colab-next').onclick=()=>{page++;refresh();};$$('[data-home-colab]').forEach(el=>{el.value=pendingHomes.get(el.dataset.homeColab)||colaboradorById(el.dataset.homeColab).moradia||'Não informado';el.onchange=()=>pendingHomes.set(el.dataset.homeColab,el.value);});$('#save-homes').onclick=()=>{for(const [id,home] of pendingHomes)colaboradorById(id).moradia=home==='Não informado'?'':home;audit('Moradias alteradas em lote',String(pendingHomes.size));pendingHomes.clear();saveData();toast('Moradias salvas.');refresh();};$$('[data-new-edit]').forEach(b=>b.onclick=()=>{const c=colaboradorById(b.dataset.newEdit);wrapper.open=true;for(const k of ['nome','funcao','custo','moradia','categoria','avulso'])$('#colab-'+k).value=c[k]??(k==='custo'?dayCost(c):k==='categoria'?category(c):k==='avulso'?'Não':'');form.onsubmit=e=>{e.preventDefault();Object.assign(c,{nome:$('#colab-nome').value.trim(),funcao:$('#colab-funcao').value.trim(),custo:Number($('#colab-custo').value),moradia:$('#colab-moradia').value.trim(),categoria:$('#colab-categoria').value,avulso:$('#colab-avulso').value});audit('Edição de colaborador',c.id);saveData();renderSettings();};wrapper.scrollIntoView({behavior:'smooth',block:'start'});});$$('[data-inactivate]').forEach(b=>b.onclick=()=>{colaboradorById(b.dataset.inactivate).inativo=true;audit('Colaborador inativado',b.dataset.inactivate);saveData();refresh();});$$('[data-reactivate]').forEach(b=>b.onclick=()=>{colaboradorById(b.dataset.reactivate).inativo=false;audit('Colaborador reativado',b.dataset.reactivate);saveData();refresh();});};search.oninput=()=>{page=0;refresh();};$('#colab-home-filter').onchange=()=>{page=0;refresh();};refresh();
    }else if(settingsTab==='Importar Colaboradores'){renderImportSettings();}else if(settingsTab==='Cobranças Teams'){renderTeamsSettings(body);}else if(settingsTab==='Limpeza de Dados'){body.innerHTML=`<h3>Limpeza e manutenção de registros</h3><p>Use esta área apenas para corrigir registros operacionais incorretos.</p><div class="card card-pad"><h3>Excluir convocações de uma data</h3><div class="form-grid">${field('Data',`<input class="control" id="clean-date" type="date" value="${isoToday()}">`)}<div><label class="field-label">&nbsp;</label><button class="btn btn-secondary" id="clean-day">Excluir esta data</button></div></div><label><input type="checkbox" id="clean-day-confirm"> Confirmo que desejo excluir as convocações desta data e os apontamentos associados.</label></div><div class="card card-pad section"><h3>Limpar todos os dados operacionais</h3><p>Remove convocações, apontamentos, indisponibilidades, conflitos e histórico de alterações. Obras e colaboradores são mantidos.</p><div class="notice warning">Esta ação é permanente e deixa o sistema sem histórico operacional.</div><label class="section" style="display:block"><input id="clean-all-check" type="checkbox"> Entendo que os dados operacionais serão excluídos.</label>${field('Digite LIMPAR DADOS para confirmar','<input class="control" id="clean-confirm" placeholder="LIMPAR DADOS">')}<button class="btn btn-primary btn-block" id="clean-all" disabled>Limpar todos os dados operacionais</button></div>`;const enable=()=>$('#clean-all').disabled=!$('#clean-all-check').checked||$('#clean-confirm').value!=='LIMPAR DADOS';$('#clean-all-check').onchange=enable;$('#clean-confirm').oninput=enable;$('#clean-day').onclick=()=>{if(!$('#clean-day-confirm').checked)return toast('Confirme a exclusão da data.',true);const d=$('#clean-date').value;state.convocacoes=state.convocacoes.filter(c=>c.dataServico!==d);state.apontamentos=state.apontamentos.filter(a=>a.dataServico!==d);audit('Exclusão por data',d);saveData();toast('Registros da data excluídos.');};$('#clean-all').onclick=()=>{if($('#clean-all').disabled)return;state.convocacoes=[];state.apontamentos=[];state.indisponibilidades=[];state.conflitosTentados=[];state.auditoria=[];state.teamsHistory=[];saveData();toast('Dados operacionais excluídos.');renderSettings();};}
    main.insertAdjacentHTML('beforeend',`<details class="card card-pad section"><summary>Obras puxadas do Trello</summary><p>Registros armazenados no Neon e conferidos com o Trello.</p>${table(['Obra','Unidade'],OBRAS.map(o=>[escapeHtml(o.nome),escapeHtml(o.unidade)]))}</details>`);
  }
  function renderTeamsSettings(body){state.teamsConfig??={};const units=adminUnits();body.innerHTML=`<h3>Cobranças Teams</h3><p>Destinatários e prévia das pendências de apontamento. O envio externo depende da integração com o Teams.</p><form id="teams-config-form"><div class="form-grid">${field('Rotina automática','<label><input id="teams-automation" type="checkbox"> Ativar rotina de cobranças quando o Teams estiver conectado</label>')}${field('Texto da cobrança manual','<input id="teams-manual-message" class="control" placeholder="Regularize os apontamentos pendentes no Portal do Supervisor.">')}</div><h3 class="section">Destinatários por supervisor</h3>${table(['Supervisor','E-mail Teams','Ativo','Ação'],SUPERVISORES.map((s,index)=>[s,`<input class="control" type="email" id="teams-email-${index}" value="${escapeHtml(state.teamsConfig[s]?.email||'')}">`,`<input type="checkbox" id="teams-enabled-${index}" ${state.teamsConfig[s]?.ativo!==false?'checked':''}>`,`<button type="button" class="btn btn-primary" data-teams-now="${s}">Cobrar agora</button>`]))}<button class="btn btn-primary btn-block">Salvar destinatários e configuração</button></form><h3 class="section">Responsáveis cadastrados</h3><div id="teams-responsible"></div><div class="form-grid">${field('Unidade',`<select id="teams-owner-unit" class="control">${options(units)}</select>`)}${field('Supervisor',`<select id="teams-owner-sup" class="control">${options(SUPERVISORES)}</select>`)}</div><button class="btn btn-secondary section" id="teams-save-owner">Salvar responsável da unidade</button><h3 class="section">Pendências de apontamento e destinatários</h3><p>A pendência considera colaboradores ainda sem apontamento, inclusive em equipes parcialmente regularizadas.</p><div id="teams-pending"></div><h3 class="section">Histórico recente de cobranças</h3><div id="teams-history"></div><div class="notice info section">Demais unidades: 16:00 do dia do serviço e 09:30 do dia seguinte. SEBRAE: 21:00 do próprio dia. Prévia local; nenhuma cobrança é enviada por este HTML.</div>`;$('#teams-automation').checked=Boolean(state.teamsAutomation);$('#teams-manual-message').value=state.teamsMessage||'';const refresh=()=>{const pending=operationalRows(state.convocacoes.filter(c=>c.dataServico<=isoToday())).filter(x=>!x.i);const noDest=pending.filter(x=>!state.teamsConfig[x.c.supervisor]?.email||state.teamsConfig[x.c.supervisor]?.ativo===false);$('#teams-pending').innerHTML=`<div class="grid grid-4">${metric('Pendências',pending.length,'colaboradores')}${metric('Pendentes hoje',pending.filter(x=>x.c.dataServico===isoToday()).length,'dia atual')}${metric('Atrasados',pending.filter(x=>!isWeekend(x.c.dataServico)&&now()>=deadlineApontamento(x.c.dataServico)).length,'prazo vencido')}${metric('Sem destinatário',noDest.length,'e-mail ausente ou inativo')}</div><div class="limited-table section">`+table(['Data','Unidade','Colaborador','Turno','Situação','Automação','Responsável','Destinatário'],pending.map(x=>[formatDate(x.c.dataServico),escapeHtml(x.c.unidade),escapeHtml(x.p?.nome),x.c.turno,!isWeekend(x.c.dataServico)&&now()>=deadlineApontamento(x.c.dataServico)?'Atrasado':'Pendente',reminder(x.c),x.c.supervisor,escapeHtml(state.teamsConfig[x.c.supervisor]?.email||'Sem destinatário')]))+'</div>';$('#teams-responsible').innerHTML=table(['Supervisor','Unidades'],SUPERVISORES.map(s=>[s,escapeHtml(Object.entries(state.unitOwners||{}).filter(([u,v])=>v===s).map(([u])=>u).join(', ')||[...new Set(state.convocacoes.filter(c=>c.supervisor===s).map(c=>c.unidade))].join(', '))]));$('#teams-history').innerHTML=table(['Data','Supervisor','Pendências','Status','Detalhe'],(state.teamsHistory||[]).slice().reverse().map(x=>[formatDateTime(x.data),x.supervisor,x.quantidade,x.status,escapeHtml(x.detalhe)]));};$('#teams-config-form').onsubmit=e=>{e.preventDefault();SUPERVISORES.forEach((s,i)=>state.teamsConfig[s]={email:$('#teams-email-'+i).value.trim(),ativo:$('#teams-enabled-'+i).checked});state.teamsAutomation=$('#teams-automation').checked;state.teamsMessage=$('#teams-manual-message').value.trim();audit('Configuração de destinatários Teams');saveData();toast('Configuração salva.');refresh();};$('#teams-save-owner').onclick=()=>{state.unitOwners??={};state.unitOwners[$('#teams-owner-unit').value]=$('#teams-owner-sup').value;audit('Responsável da unidade alterado');saveData();refresh();};$$('[data-teams-now]').forEach(b=>b.onclick=()=>{const s=b.dataset.teamsNow,rows=operationalRows(state.convocacoes.filter(c=>c.supervisor===s&&c.dataServico<=isoToday())).filter(x=>!x.i);body.insertAdjacentHTML('beforeend',`<div class="card card-pad section"><h3>Prévia da cobrança · ${s}</h3><textarea class="control" id="teams-preview" readonly>${escapeHtml((state.teamsMessage||'Regularize os apontamentos pendentes no Portal do Supervisor.')+'\n'+rows.map(x=>formatDate(x.c.dataServico)+' · '+x.c.unidade+' · '+x.p?.nome).join('\n'))}</textarea><p>Prévia gerada. Envio não realizado: Teams não conectado.</p></div>`);state.teamsHistory??=[];state.teamsHistory.push({data:now().toISOString(),supervisor:s,quantidade:rows.length,status:'Não enviado',detalhe:'Prévia local; Teams não conectado'});saveData();refresh();});refresh();}
  const xmlSafe=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  function zipStore(files){const enc=new TextEncoder(),parts=[],central=[];let offset=0;const crc=data=>{let c=0xffffffff;for(const b of data){c^=b;for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xedb88320:0);}return (c^0xffffffff)>>>0;};for(const [name,content] of Object.entries(files)){const n=enc.encode(name),d=enc.encode(content),h=new Uint8Array(30+n.length),v=new DataView(h.buffer),sum=crc(d);v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint32(14,sum,true);v.setUint32(18,d.length,true);v.setUint32(22,d.length,true);v.setUint16(26,n.length,true);h.set(n,30);parts.push(h,d);const c=new Uint8Array(46+n.length),cv=new DataView(c.buffer);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint32(16,sum,true);cv.setUint32(20,d.length,true);cv.setUint32(24,d.length,true);cv.setUint16(28,n.length,true);cv.setUint32(42,offset,true);c.set(n,46);central.push(c);offset+=h.length+d.length;}const length=central.reduce((v,x)=>v+x.length,0),end=new Uint8Array(22),ev=new DataView(end.buffer);ev.setUint32(0,0x06054b50,true);ev.setUint16(8,central.length,true);ev.setUint16(10,central.length,true);ev.setUint32(12,length,true);ev.setUint32(16,offset,true);return new Blob([...parts,...central,end],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});}
  function downloadBlob(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
  function exportVisibleWorkbook(filename){const tables=$$('#main-content table');if(!tables.length)return toast('Sem dados para exportar.',true);exportWorkbook(tables.map((t,i)=>({name:'Tabela '+(i+1),center:[...t.rows[0].cells].map((c,j)=>/data|status|situação|turno|quantidade|dias|atrasado|prazo|posição|extra|percentual|%/i.test(c.innerText)?j:-1).filter(j=>j>=0),rows:[...t.rows].map(r=>[...r.cells].map(c=>c.innerText))})),filename);}
  function reportRowsForExport(rows){const fin=perfilAtual==='FINANCEIRO';return [['Data','Supervisor','Unidade','Obra','Colaborador','Período','Status',fin?'Financeiro':'Custo normal','Extra (R$)','Noturno','Acordos','Periculosidade','Total'],...rows.map(x=>[formatDate(x.c.dataServico),x.c.supervisor,x.c.unidade,fin?financialWorkNumber(x.c.obraId):obraById(x.c.obraId)?.nome||'',x.p?.nome||'',x.service.periodo,x.displayStatus||x.i.status,fin?x.finance:x.daily,fin?0:x.extra,x.night,x.bonus,fin?0:x.danger,fin?x.finance+x.night+x.bonus:x.daily+x.extra+x.danger+x.night+x.bonus])];}
  const excelCol=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
  function exportWorkbook(sheets,filename){
    const ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main',rel='http://schemas.openxmlformats.org/package/2006/relationships',files={};
    files['_rels/.rels']=`<Relationships xmlns="${rel}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`;
    files['xl/workbook.xml']=`<workbook xmlns="${ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${sheets.map((s,i)=>`<sheet name="${xmlSafe(s.name.slice(0,31))}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join('')}</sheets><calcPr calcMode="auto"/></workbook>`;
    files['xl/_rels/workbook.xml.rels']=`<Relationships xmlns="${rel}">`+sheets.map((s,i)=>`<Relationship Id="rId${i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join('')+`<Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`;
    files['[Content_Types].xml']='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+sheets.map((s,i)=>`<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')+'</Types>';
    const xf=(font,fill,num=0,align='left')=>`<xf numFmtId="${num}" fontId="${font}" fillId="${fill}" borderId="0" xfId="0" applyAlignment="1" applyNumberFormat="1"><alignment horizontal="${align}" vertical="center" wrapText="1"/></xf>`;
    files['xl/styles.xml']=`<styleSheet xmlns="${ns}"><numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;R$&quot; #,##0.00"/></numFmts><fonts count="3"><font><sz val="10"/><name val="Arial"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font><font><b/><sz val="12"/><name val="Arial"/><color rgb="FF1E293B"/></font></fonts><fills count="5"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1E293B"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF2563EB"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF1F5F9"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1">${xf(0,0)}</cellStyleXfs><cellXfs count="10">${xf(0,0)}${xf(1,2,0,'center')}${xf(2,0)}${xf(0,0,164,'right')}${xf(1,3,0,'center')}${xf(0,4)}${xf(0,4,164,'right')}${xf(2,4)}${xf(0,0,0,'center')}${xf(0,4,0,'center')}</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>`;
    sheets.forEach((s,i)=>{const cols=s.widths||Array.from({length:Math.max(...s.rows.map(r=>r.length),1)},()=>24),freeze=s.freeze||1;files[`xl/worksheets/sheet${i+1}.xml`]=`<worksheet xmlns="${ns}"><sheetViews><sheetView workbookViewId="0"><pane ySplit="${freeze}" topLeftCell="A${freeze+1}" state="frozen"/></sheetView></sheetViews><cols>${cols.map((w,j)=>`<col min="${j+1}" max="${j+1}" width="${w}" customWidth="1"/>`).join('')}</cols><sheetData>${s.rows.map((r,ri)=>`<row r="${ri+1}" ht="${(s.headers||[0]).includes(ri)?40:ri===0?30:26}" customHeight="1">${r.map((v,j)=>{const obj=v&&typeof v==='object',value=obj?v.value:v,style=obj&&v.style!=null?v.style:(s.headers||[0]).includes(ri)?(s.blue?4:1):(s.titles||[]).includes(ri)?2:(s.sections||[]).includes(ri)?7:(s.money||[]).includes(j)&&typeof value==='number'?(ri%2?3:6):(s.center||[]).includes(j)?(ri%2?8:9):(ri%2?0:5),ref=excelCol(j)+(ri+1);return obj&&v.formula?`<c r="${ref}" s="${style}"><f>${xmlSafe(v.formula)}</f><v>${Number(value)||0}</v></c>`:typeof value==='number'?`<c r="${ref}" s="${style}"><v>${value}</v></c>`:`<c r="${ref}" s="${style}" t="inlineStr"><is><t xml:space="preserve">${xmlSafe(value)}</t></is></c>`;}).join('')}</row>`).join('')}</sheetData>${s.merges?.length?`<mergeCells count="${s.merges.length}">${s.merges.map(m=>`<mergeCell ref="${m}"/>`).join('')}</mergeCells>`:''}<pageMargins left="0.25" right="0.25" top="0.4" bottom="0.4" header="0.2" footer="0.2"/><pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>`;});downloadBlob(filename+'.xlsx',zipStore(files));
  }
  function reportPeriod(){return formatDate(reportFilters.inicio)+' a '+formatDate(reportFilters.fim);}
  function controlValues(x){const multiplier=dangerEligible(x.p)?1.3:1;return [roundMoney(x.daily*multiplier),roundMoney(x.extra*multiplier),x.night,x.bonus];}
  function controlWorkbook(){
    const data=entries(),generalHeaders=['Data','Unidade','Colaborador','Função','Supervisor responsável','Status','Extra','Custo do Dia c/ Encargos (R$)','Extra c/ Encargos (R$)','Adicional Noturno (R$)','Acordos / Bonificações (R$)','Total (R$)','Observação'],dailyHeaders=generalHeaders.slice(2);
    function make(name,rows,general){return {name,rows,headers:[],titles:[0],sections:[],merges:[`A1:${general?'M':'K'}1`],freeze:4,money:general?[7,8,9,10,11]:[5,6,7,8,9],center:general?[0,5,6]:[3,4],widths:general?[16,18,38,26,22,22,13,32,25,25,30,19,30]:[38,26,22,22,13,32,25,25,30,19,30]};}
    function blocks(sheet,xs,general){const groups=new Map();xs.forEach(x=>{const key=x.c.unidade+'|'+x.c.obraId;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(x);});for(const group of groups.values()){const x=group[0],n=sheet.rows.length+1,last=general?'M':'K';sheet.sections.push(n-1);sheet.merges.push(`A${n}:${last}${n}`);sheet.rows.push([`UNIDADE: ${x.c.unidade} | OBRA: ${obraById(x.c.obraId)?.nome||'Sem obra'} | PERÍODO: ${[...new Set(group.map(x=>x.service.periodo))].join(', ')}`]);sheet.headers.push(sheet.rows.length);sheet.rows.push(general?generalHeaders:dailyHeaders);const start=sheet.rows.length+1;let total=0;for(const x of group){const v=controlValues(x),r=sheet.rows.length+1,sum=roundMoney(v.reduce((a,b)=>a+b,0));total+=sum;sheet.rows.push([...(general?[formatDate(x.c.dataServico),x.c.unidade]:[]),x.p?.nome||'',x.p?.funcao||'',x.c.supervisor,x.displayStatus||x.i.status,x.displayExtra||x.i.extra||'Não',...v,{formula:general?`H${r}+I${r}+J${r}+K${r}`:`F${r}+G${r}+H${r}+I${r}`,value:sum},x.i.observacao||x.i.obs||'']);}const row=Array(general?13:11).fill(''),totalCol=general?'L':'J';row[general?10:8]='TOTAL DA OBRA';row[general?11:9]={formula:`SUM(${totalCol}${start}:${totalCol}${sheet.rows.length})`,value:roundMoney(total)};sheet.rows.push(row,[]);}}
    const general=make('GERAL',[['APONTAMENTO DIÁRIO DE EQUIPES - PERÍODO: '+reportPeriod()],['Periculosidade de 30% aplicada na Controladoria para ELETRICISTA e AUXILIAR DE ELETRICISTA.'],[]],true);general.merges.push('A2:M2');blocks(general,data,true);return [general,...[...new Set(data.map(x=>x.c.dataServico))].sort().map(d=>{const sheet=make(d,[['APONTAMENTO DIÁRIO DE EQUIPES - DATA: '+d],[]],false);blocks(sheet,data.filter(x=>x.c.dataServico===d),false);return sheet;})];
  }
  function indicatorReportData(){const cv=state.convocacoes.filter(c=>c.dataServico>=reportFilters.inicio&&c.dataServico<=reportFilters.fim&&(indicatorUnit==='Todas'||c.unidade===indicatorUnit)),ids=new Set(cv.map(c=>c.id)),ap=state.apontamentos.filter(a=>ids.has(a.convocacaoId)),count=xs=>new Set(xs.map(x=>x.dataServico)).size;const summary=SUPERVISORES.map(s=>{const own=cv.filter(c=>c.supervisor===s&&(c.executor||s)===s),pointed=ap.filter(a=>a.supervisor===s&&(a.executor||s)===s),n=count(own),late=count(own.filter(convocacaoAtrasada));return [s,n,late,count(pointed),count(pointed.filter(apontamentoAtrasado)),n?roundMoney((n-late)/n*100):0];});const events=[];for(const c of cv){if(!SUPERVISORES.includes(c.supervisor))continue;for(const id of c.colaboradores)events.push([c.supervisor,formatDate(c.dataServico),colaboradorById(id)?.nome||id,'Convocação',formatDateTime(c.criadoEm),convocacaoAtrasada(c)?'SIM':'NÃO']);const a=apForConv(c.id);if(a)for(const i of a.itens)events.push([c.supervisor,formatDate(c.dataServico),colaboradorById(i.colaboradorId)?.nome||i.colaboradorId,'Apontamento',formatDateTime(a.apontadoEm),apontamentoAtrasado(a)?'SIM':'NÃO']);}const missing=indicatorUnit==='Todas'?diasSemConvocacao(SUPERVISORES,reportFilters.inicio,reportFilters.fim):[],gaps=SUPERVISORES.map(s=>{const dates=missing.filter(x=>x.supervisor===s).map(x=>x.dataServico),noAp=[...new Set(cv.filter(c=>c.supervisor===s&&!completeConv(c)&&now()>=deadlineApontamento(c.dataServico)).map(c=>c.dataServico))];return [s,indicatorUnit==='Todas'?dates.length:'—',noAp.length,dates.map(formatDate).join(', ')||(indicatorUnit==='Todas'?'Nenhum':'Somente com todas as unidades'),noAp.map(formatDate).join(', ')||'Nenhum'];});return {summary,events,gaps};}
  function indicatorWorkbook(){const d=indicatorReportData(),make=(name,title,headers,rows,widths)=>({name,rows:[[title],['Período: '+reportPeriod()+' | Unidade: '+indicatorUnit],[],headers,...rows],headers:[3],titles:[],blue:true,merges:['A1:F1','A2:F2'],freeze:4,center:[1,2,3,4,5],widths});const sheets=[make('Resumo','INDICADOR DE CUMPRIMENTO DE PRAZOS',['Supervisor','Convocações feitas','Convocações atrasadas','Apontamentos feitos','Apontamentos atrasados','No prazo (%)'],d.summary,[18,21,24,22,25,15]),make('Ocorrências','OCORRÊNCIAS DE CONVOCAÇÃO E APONTAMENTO',['Supervisor','Data do serviço','Colaborador','Tipo','Registrado em','Atrasado'],d.events,[18,18,42,18,24,11])];sheets[1].center=[1,3,4,5];sheets.forEach(s=>s.rows[0][0]={value:s.rows[0][0],style:4});return sheets;}
  function financialWorkNumber(id){const name=obraById(id)?.nome||'';const obra=name.match(/\bOBRA\s*(?:N[º°.]*\s*)?(\d+(?:[.,/-]\d+)*)/i),code=name.match(/\b(APR[A-Z]*\s*[-.]?\s*\d+(?:[./-]\d+)*)/i),number=name.match(/^\s*(\d+(?:[.,/-]\d+)*)(?=\s|$|\s*-)/);return obra?obra[1]:code?code[1].replace(/\s+/g,'').toUpperCase():number?number[1]:'Sem número cadastrado';}
  function financialWorkbook(){const data=entries().filter(x=>presence(x.i.status)&&x.finance+x.night+x.bonus>0.005);function sheet(name,xs){const rows=[['RELATÓRIO FINANCEIRO - '+reportPeriod()],[]],headers=[],sections=[],merges=['A1:L1'],groups=new Map();for(const x of xs){const k=x.c.unidade+'|'+x.c.obraId;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(x);}for(const group of groups.values()){const x=group[0],n=rows.length+1;sections.push(n-1);merges.push(`A${n}:L${n}`);rows.push([`UNIDADE: ${x.c.unidade} | OBRA: ${financialWorkNumber(x.c.obraId)}`]);headers.push(rows.length);rows.push(['Data','Supervisor','Unidade','Colaborador','Função','Período','Status','Financeiro (R$)','Noturno (R$)','Acordos (R$)','Total (R$)','Observação']);let total=0;const start=rows.length+1;for(const x of group){const r=rows.length+1,value=roundMoney(x.finance+x.night+x.bonus);total+=value;rows.push([formatDate(x.c.dataServico),x.c.supervisor,x.c.unidade,x.p?.nome||'',x.p?.funcao||'',x.service.periodo,x.displayStatus||x.i.status,x.finance,x.night,x.bonus,{formula:`H${r}+I${r}+J${r}`,value},x.i.observacao||x.i.obs||'']);}rows.push(['','','','','','','','','','TOTAL DA OBRA',{formula:`SUM(K${start}:K${rows.length})`,value:roundMoney(total)},''],[]);}return {name,rows,headers,sections,merges,titles:[0],freeze:4,center:[0,5,6],money:[7,8,9,10],widths:[16,22,20,38,26,22,22,22,22,22,22,30]};}return [sheet('GERAL',data),...[...new Set(data.map(x=>x.c.dataServico))].sort().map(d=>sheet(d,data.filter(x=>x.c.dataServico===d)))];}
  function exportReportsExcel(){exportWorkbook(perfilAtual==='FINANCEIRO'?financialWorkbook():controlWorkbook(),(perfilAtual==='FINANCEIRO'?'financeiro':'controladoria_rateada')+'_'+reportFilters.inicio+'_a_'+reportFilters.fim);}
  async function reportPDF(kind){try{const {PDFDocument,StandardFonts,rgb}=PDFLib,doc=await PDFDocument.create(),regular=await doc.embedFont(StandardFonts.Helvetica),bold=await doc.embedFont(StandardFonts.HelveticaBold),W=841.89,H=595.28,margin=36;let page,y;const navy=rgb(.118,.161,.231),blue=rgb(.145,.388,.922),gray=rgb(.94,.96,.98),black=rgb(.08,.09,.11);const safe=v=>String(v??'').replace(/[\u2014\u2013]/g,'-').replace(/[^\x20-\x7e\xa0-\xff\n]/g,'');
    const text=(v,x,yy,size=9,font=regular,color=black)=>page.drawText(safe(v),{x,y:yy,size,font,color});const title=kind==='absences'?'APROAR | FALTAS E ATESTADOS':kind==='executive'?'APROAR | RELATÓRIO DE RESULTADOS':kind==='financial'?'APROAR - RELATÓRIO FINANCEIRO':'APROAR | APONTAMENTO DIÁRIO DE EQUIPES';
    function newPage(){page=doc.addPage([W,H]);y=H-40;text(title,kind==='financial'?(W-bold.widthOfTextAtSize(title,16))/2:margin,y,16,bold,kind==='financial'?black:navy);y-=21;text('Período: '+reportPeriod()+(kind==='executive'?' | Unidade: '+indicatorUnit:''),margin,y,9);y-=25;}
    const wrap=(v,width,font=regular,size=8)=>{const result=[];for(const paragraph of safe(v).split('\n')){let line='';for(const word of paragraph.split(/\s+/)){if(font.widthOfTextAtSize((line?line+' ':'')+word,size)>width&&line){result.push(line);line='';}if(font.widthOfTextAtSize(word,size)>width){let chunk='';for(const ch of word){if(font.widthOfTextAtSize(chunk+ch,size)>width&&chunk){result.push(chunk);chunk='';}chunk+=ch;}line=chunk;}else line+=(line?' ':'')+word;}result.push(line);}return result;};
    function paragraph(v,size=9,font=regular){for(const line of wrap(v,W-2*margin,font,size)){if(y<55)newPage();text(line,margin,y,size,font);y-=size+4;}y-=7;}
    function grid(headers,rows,widths,financial=false){const sum=widths.reduce((a,b)=>a+b,0),ws=widths.map(w=>w/sum*(W-2*margin));function draw(values,header=false,index=0,prepared=null){const lines=prepared||values.map((v,i)=>wrap(v,ws[i]-10,header?bold:regular,8));const maxLines=Math.max(...lines.map(l=>l.length));if(maxLines>36){for(let offset=0;offset<maxLines;offset+=36)draw(values,header,index,lines.map(l=>l.slice(offset,offset+36)));return;}const height=Math.max(24,...lines.map(l=>l.length*11+10));if(y-height<45){newPage();if(!header)draw(headers,true);}let x=margin;values.forEach((v,i)=>{page.drawRectangle({x,y:y-height,width:ws[i],height,color:header?(financial?rgb(1,1,1):blue):financial||index%2?rgb(1,1,1):gray,borderWidth:financial?.4:0,borderColor:black});lines[i].forEach((line,k)=>{const font=header?bold:regular,right=!header&&/^R\$/.test(String(v));text(line,right?x+ws[i]-5-font.widthOfTextAtSize(line,8):x+5,y-14-k*11,8,font,header&&!financial?rgb(1,1,1):black);});x+=ws[i];});y-=height;}draw(headers,true);if(!rows.length)rows=[headers.map((_,i)=>i===0?'Nenhum registro no período':'')];rows.forEach((r,i)=>draw(r,false,i));y-=18;}
    function cards(values){if(y<110)newPage();const width=(W-2*margin-30)/values.length;values.forEach(([label,value],i)=>{const x=margin+i*(width+10);page.drawRectangle({x,y:y-62,width,height:62,color:gray});text(label,x+10,y-18,8,bold,navy);text(value,x+10,y-46,21,bold,navy);});y-=82;}
    newPage();if(kind==='executive'){const d=indicatorReportData(),total=d.summary.reduce((a,r)=>a+r[1],0),late=d.summary.reduce((a,r)=>a+r[2],0);cards([['CONVOCAÇÕES',total],['NO PRAZO',total-late],['ATRASADAS',late],['NÃO FEITAS',d.gaps.reduce((a,r)=>a+(Number(r[1])||0),0)]]);paragraph('1. Desempenho dos supervisores',12,bold);paragraph('Cada supervisor e dia de serviço conta como uma convocação, independentemente do tamanho da equipe.');grid(['Supervisor','Convocações','Atrasadas','No prazo','Apontamentos','Apt. atrasados'],d.summary.map(r=>[r[0],r[1],r[2],r[1]-r[2],r[3],r[4]]),[2,1,1,1,1,1]);paragraph('2. Convocações e apontamentos pendentes',12,bold);paragraph('Quantidade e datas dos registros não realizados no período selecionado.');grid(['Supervisor','Não feitas','Apt. não feitos','Dias sem convocação','Dias sem apontamento'],d.gaps,[1.3,1,1,3,3]);newPage();paragraph('3. Apontamentos',12,bold);cards([['TOTAL DE APONTAMENTOS',d.summary.reduce((a,r)=>a+r[3],0)],['APONTAMENTOS ATRASADOS',d.summary.reduce((a,r)=>a+r[4],0)]]);paragraph('Apontamentos por supervisor',12,bold);grid(['Supervisor','Apontamentos','Atrasados'],d.summary.map(r=>[r[0],r[3],r[4]]),[3,1,1]);paragraph('Critério: o indicador considera somente ações lançadas pelo próprio supervisor. Lançamentos administrativos não são atribuídos ao seu desempenho. Sábados e domingos não geram atraso automático.');
    }else if(kind==='absences'){const records=absenceRecords();paragraph('Faltas: '+records.filter(x=>x.i.status==='Falta').length+' | Atestados: '+records.filter(x=>x.i.status==='Atestado').length,11,bold);grid(absenceHeaders,absenceReportRows(),[1,1.3,2.5,1.6,1.6,1,2.7],true);
    }else if(kind==='financial'){const rows=financialEntries(),groups=new Map();for(const x of rows.filter(x=>presence(x.i.status)&&x.finance+x.night+x.bonus>0.005)){const key=x.c.supervisor+'|'+x.p.id;if(!groups.has(key))groups.set(key,{sup:x.c.supervisor,p:x.p,days:new Set(),units:new Set(),works:new Set(),finance:0,night:0,bonus:0});const g=groups.get(key);g.days.add(x.c.dataServico);x.units.forEach(u=>g.units.add(u));x.works.forEach(w=>g.works.add(financialWorkNumber(w)));g.finance+=x.finance;g.night+=x.night;g.bonus+=x.bonus;}const values=[...groups.values()];if(viewAtual==='pagamentos'&&selectedCycle!=='custom')paragraph('Pagamento previsto: '+formatDate(financialCycle(isoToday(),Number(selectedCycle)).pagamento));paragraph('TOTAL A PAGAR: '+money(values.reduce((a,x)=>a+x.finance+x.night+x.bonus,0)),12,bold);for(const sup of [...new Set(values.map(x=>x.sup))]){const xs=values.filter(x=>x.sup===sup);if(y<125)newPage();paragraph('SUPERVISOR: '+sup+' | SUBTOTAL: '+money(xs.reduce((a,x)=>a+x.finance+x.night+x.bonus,0)),10,bold);grid(['Colaborador','Função','Unidade(s)','Obra','Dias','Financeiro','Adic. not.','Acordos / Bonif.','Total'],xs.map(x=>[x.p.nome,x.p.funcao,[...x.units].join(', '),[...x.works].join(', '),x.days.size,money(x.finance),money(x.night),money(x.bonus),money(x.finance+x.night+x.bonus)]),[2.2,1.6,1.3,2.1,.5,1,1,1.2,1],true);}
    }else{grid(['Data','Unidade / Obra','Colaborador / Função','Supervisor','Status','Normal','Extra','Noturno','Acordos','Total'],entries().map(x=>{const v=controlValues(x);return [formatDate(x.c.dataServico),x.c.unidade+'\n'+(obraById(x.c.obraId)?.nome||''),x.p?.nome+'\n'+x.p?.funcao,x.c.supervisor,x.displayStatus,...v.map(money),money(v.reduce((a,b)=>a+b,0))];}),[1,2.5,2.5,1.2,1.2,1,1,1,1,1]);}
    doc.getPages().forEach((p,i)=>{const label='APROAR | '+(kind==='absences'?'Faltas e Atestados':kind==='executive'?'Relatório de Resultados':kind==='financial'?'Relatório Financeiro':'Controladoria')+' | Página '+(i+1);p.drawText(label,{x:(W-regular.widthOfTextAtSize(label,8))/2,y:22,size:8,font:regular,color:navy});});downloadBlob((kind==='absences'?'faltas_atestados':kind==='executive'?'relatorio_resultados':kind==='financial'?'financeiro_pagamentos':'controladoria')+'_'+reportFilters.inicio+'_a_'+reportFilters.fim+'.pdf',new Blob([await doc.save()],{type:'application/pdf'}));}catch(e){toast('Não foi possível gerar o PDF: '+e.message,true);}}
  async function xlsxRows(file){const bytes=new Uint8Array(await file.arrayBuffer()),view=new DataView(bytes.buffer);let end=bytes.length-22;while(end>=0&&view.getUint32(end,true)!==0x06054b50)end--;if(end<0)throw Error('Arquivo XLSX inválido.');let ptr=view.getUint32(end+16,true);const count=view.getUint16(end+10,true),files={};for(let j=0;j<count;j++){if(view.getUint32(ptr,true)!==0x02014b50)throw Error('Estrutura ZIP inválida.');const method=view.getUint16(ptr+10,true),size=view.getUint32(ptr+20,true),n=view.getUint16(ptr+28,true),extra=view.getUint16(ptr+30,true),comment=view.getUint16(ptr+32,true),off=view.getUint32(ptr+42,true),name=new TextDecoder().decode(bytes.slice(ptr+46,ptr+46+n));const start=off+30+view.getUint16(off+26,true)+view.getUint16(off+28,true);let data=bytes.slice(start,start+size);if(method===8)data=new Uint8Array(await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());else if(method!==0)throw Error('Compressão não suportada.');files[name]=new TextDecoder().decode(data);ptr+=46+n+extra+comment;}const parse=s=>new DOMParser().parseFromString(s,'application/xml'),strings=files['xl/sharedStrings.xml']?[...parse(files['xl/sharedStrings.xml']).getElementsByTagName('si')].map(si=>[...si.getElementsByTagName('t')].map(t=>t.textContent).join('')):[];const workbook=parse(files['xl/workbook.xml']),first=workbook.getElementsByTagName('sheet')[0],rid=first?.getAttribute('r:id'),rels=parse(files['xl/_rels/workbook.xml.rels']);const target=[...rels.getElementsByTagName('Relationship')].find(x=>x.getAttribute('Id')===rid)?.getAttribute('Target');const path=target?.startsWith('/')?target.slice(1):'xl/'+target;const sheet=files[path]||files['xl/worksheets/sheet1.xml'];if(!sheet)throw Error('Não foi possível ler a primeira aba.');return [...parse(sheet).getElementsByTagName('row')].map(row=>{const values=[];for(const c of row.getElementsByTagName('c')){const ref=c.getAttribute('r').replace(/[0-9]/g,''),index=[...ref].reduce((v,ch)=>v*26+ch.charCodeAt(0)-64,0)-1,t=c.getAttribute('t'),v=c.getElementsByTagName('v')[0]?.textContent||'';values[index]=t==='s'?strings[Number(v)]:t==='inlineStr'?[...c.getElementsByTagName('t')].map(t=>t.textContent).join(''):v;}return values;});}
  function parseCSV(text){text=text.replace(/^\uFEFF/,'');const delim=(text.split(/\r?\n/)[0].match(/;/g)||[]).length>=(text.split(/\r?\n/)[0].match(/,/g)||[]).length?';':',';const rows=[];let row=[],value='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){value+='"';i++;}else quoted=!quoted;}else if(c===delim&&!quoted){row.push(value);value='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(value);if(row.some(v=>v.trim()))rows.push(row);row=[];value='';}else value+=c;}row.push(value);if(row.some(v=>v.trim()))rows.push(row);return rows;}
  function renderImportSettings(){const body=$('#settings-body');body.innerHTML=`<h3>Importar planilha de colaboradores</h3><p>Adicione novos colaboradores ou atualize cadastros pelo nome. Nenhum colaborador ausente da planilha será excluído.</p><input class="control" id="import-file" type="file" accept=".xlsx,.csv"><p>XLSX ou CSV. A primeira aba deve conter nome, função e custo diário.</p><div id="import-mapping" class="section"></div><div id="import-preview" class="section"></div><div class="form-actions"><button class="btn btn-secondary" id="import-template">Baixar modelo Excel</button><button class="btn btn-primary" id="import-save" disabled>Importar prévia</button></div>`;let matrix=[],rows=[];$('#import-template').onclick=()=>exportWorkbook([{name:'Colaboradores',rows:[['Nome','Função','Custo diário','Moradia','Categoria','Avulso'],['Exemplo fictício','Pedreiro',241.74,'Fortaleza','Profissional','Não']]}],'modelo_colaboradores');const preview=()=>{const map=Object.fromEntries(['nome','funcao','custo','moradia','categoria','avulso'].map(k=>[k,Number($('#map-'+k).value)]));rows=matrix.slice(1).filter(r=>r.some(v=>String(v||'').trim())).map(r=>{const x=Object.fromEntries(Object.entries(map).map(([k,j])=>[k,j>=0?String(r[j]??'').trim():'']));let cost=x.custo.replace(/R\$\s*/g,'');if(cost.includes(','))cost=cost.replaceAll('.','').replace(',','.');x.custo=Number(cost);return x;});const invalid=rows.filter(x=>!x.nome||!x.funcao||!Number.isFinite(x.custo)||x.custo<=0);$('#import-preview').innerHTML=`<div class="notice ${invalid.length?'warning':'info'}">${rows.length} linha(s). ${invalid.length} linha(s) inválida(s). Preencha nome, função e um custo diário positivo para importar.</div>`+table(['Nome','Função','Custo','Moradia','Ação'],rows.map(x=>[escapeHtml(x.nome),escapeHtml(x.funcao),money(x.custo),escapeHtml(x.moradia),COLABORADORES.some(c=>clean(c.nome)===clean(x.nome))?'Atualizar':'Adicionar']));$('#import-save').disabled=!rows.length||Boolean(invalid.length)||map.nome<0||map.funcao<0||map.custo<0;};$('#import-file').onchange=async()=>{const f=$('#import-file').files[0];if(!f)return;try{matrix=f.name.toLowerCase().endsWith('.xlsx')?await xlsxRows(f):parseCSV(await f.text());if(matrix.length<2)throw Error('A planilha precisa de cabeçalho e dados.');const headers=matrix[0];const hints={nome:/NOME|COLABORADOR|FUNCIONARIO/,funcao:/FUNCAO|CARGO/,custo:/CUSTO|DIARIA|VALOR/,moradia:/MORADIA|RESIDENCIA/,categoria:/CATEGORIA/,avulso:/AVULSO/};$('#import-mapping').innerHTML='<h3>Conferir colunas</h3><div class="form-grid">'+Object.keys(hints).map(k=>field(k==='funcao'?'Função':readableName(k),`<select class="control" id="map-${k}"><option value="-1">Não usar</option>${headers.map((v,i)=>`<option value="${i}">${escapeHtml(v)}</option>`).join('')}</select>`)).join('')+'</div>';Object.keys(hints).forEach(k=>{$('#map-'+k).value=String(headers.findIndex(v=>hints[k].test(clean(v))));$('#map-'+k).onchange=preview;});preview();}catch(e){rows=[];$('#import-save').disabled=true;$('#import-preview').innerHTML='<div class="notice warning">'+escapeHtml(e.message)+'</div>';}};$('#import-save').onclick=()=>{if($('#import-save').disabled)return;let added=0,updated=0;for(const x of rows){const c=COLABORADORES.find(c=>clean(c.nome)===clean(x.nome));const data={nome:x.nome,funcao:x.funcao,custo:x.custo,...(x.moradia?{moradia:x.moradia}:{}),...(x.categoria?{categoria:x.categoria}:{}),...(x.avulso?{avulso:x.avulso}:{})};if(c){Object.assign(c,data);updated++;}else{COLABORADORES.push({id:uid('c'),...data});added++;}}audit('Importação de colaboradores',added+' novos / '+updated+' atualizados');saveData();toast(added+' adicionados e '+updated+' atualizados.');renderSettings();};}

  const extendedRenderers={convocacao:renderConvCompleta,apontamento:renderApCompleto,disponibilidade:renderDisponibilidade,indisponibilidade:renderIndisponibilidade,conflitos:renderConflitos,whatsapp:renderWhatsApp,dashboard:renderDashboard,relatorios:renderReports,financeiro:renderPayments,ausencias:renderAbsences,configuracoes:renderSettings,indicadores:renderIndicators};
  
  let onlineVersion='',onlineSession=null,onlineWritable=false,onlineConfirmed=null,onlineQueued=false,onlineSaving=false,onlineMessage='';
  const copy=v=>JSON.parse(JSON.stringify(v));
  async function api(path,options={}){const response=await fetch(path,{credentials:'same-origin',...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});const data=await response.json();if(!response.ok)throw Object.assign(new Error(data.error||'Falha na comunicação.'),{status:response.status});return data;}
  function applyOnline(result){state=result.state;OBRAS.splice(0,OBRAS.length,...state.obras);COLABORADORES.splice(0,COLABORADORES.length,...state.colaboradores);onlineVersion=result.version;onlineSession=result.session;onlineWritable=result.writesEnabled;onlineConfirmed=copy(state);perfilAtual=result.session.role;supervisorAtual=result.session.role==='SUPERVISOR'?result.session.user:'';}
  function lockOnline(locked){$('#app-view').inert=locked;$('#online-saving').classList.toggle('hidden',!locked);}
  function toast(message,error=false){if((onlineQueued||onlineSaving)&&!error){onlineMessage=message;return;}showToast(message,error);}
  function saveData(){
    if(!onlineSession||!onlineWritable||onlineSession.role==='VISUALIZAR'){if(onlineConfirmed){state=copy(onlineConfirmed);OBRAS.splice(0,OBRAS.length,...state.obras);COLABORADORES.splice(0,COLABORADORES.length,...state.colaboradores);}toast('Gravação não autorizada nesta sessão.',true);queueMicrotask(()=>render());return;}
    state.obras=OBRAS;state.colaboradores=COLABORADORES;if(onlineQueued)return;if(onlineSaving){showToast('Aguarde a gravação em andamento.',true);return;}onlineQueued=true;lockOnline(true);
    queueMicrotask(async()=>{onlineQueued=false;onlineSaving=true;const payload=JSON.stringify({requestId:crypto.randomUUID(),version:onlineVersion,state:copy(state)});try{
      let result;for(let attempt=0;attempt<2;attempt++){try{result=await api('/api/save',{method:'POST',body:payload});break;}catch(e){if(e.status||attempt===1)throw e;}}
      applyOnline(result);onlineSaving=false;render();showToast(onlineMessage||'Alterações salvas no Neon.');
    }catch(e){try{applyOnline(await api('/api/bootstrap'));}catch{if(onlineConfirmed){state=copy(onlineConfirmed);OBRAS.splice(0,OBRAS.length,...state.obras);COLABORADORES.splice(0,COLABORADORES.length,...state.colaboradores);}}onlineSaving=false;render();showToast(e.message,true);
    }finally{onlineQueued=false;onlineSaving=false;onlineMessage='';lockOnline(false);}});
  }
  function resetData(){toast('A restauração de dados de homologação está desativada na versão conectada.',true);}
  async function logout(){chooseLogin('CONTROLADORIA');if(onlineSaving||onlineQueued)return;try{await api('/api/logout',{method:'POST',body:'{}'});}catch(e){return showToast(e.message,true);}perfilAtual='';supervisorAtual='';onlineSession=null;onlineConfirmed=null;state=seedData();OBRAS.length=0;COLABORADORES.length=0;render();}
  const renderLocal=render;
  render=function(){renderLocal();if(!perfilAtual)return;const selector=$('#portal-sup');if(onlineSession?.role==='SUPERVISOR'&&selector){selector.value=onlineSession.user;selector.disabled=true;}const old=$('#live-status');if(old)old.remove();const status=document.createElement('div');status.id='live-status';status.className='notice '+(onlineWritable?'info':'warning');status.innerHTML=`<strong>Homologação · ${onlineWritable?'dados conectados ao Neon':'somente leitura'}</strong> <span>Confira os registros nesta cópia de testes.</span> <button type="button" class="link-btn" id="sync-online">Atualizar dados</button>`;$('#main-content').prepend(status);$('#sync-online').onclick=async()=>{if(onlineSaving||onlineQueued)return;lockOnline(true);try{applyOnline(await api('/api/bootstrap'));render();showToast('Dados atualizados.');}catch(e){showToast(e.message,true);}finally{lockOnline(false);}};};
  function chooseLogin(role){loginRole=role;const shortcut=['SUPERVISOR','VISUALIZAR'].includes(role);$('#login-access-wrap').classList.toggle('hidden',shortcut);$('#login-shortcut-mode').classList.toggle('hidden',!shortcut);$('#login-shortcut-label').textContent=role==='SUPERVISOR'?'Portal do Supervisor':'Somente visualizar';if(!shortcut)$('#login-access').value=role;$('#login-supervisor-wrap').classList.toggle('hidden',role!=='SUPERVISOR');$('#login-password').required=false;$('#login-password').closest('.password-wrap').classList.toggle('hidden',['SUPERVISOR','VISUALIZAR'].includes(role));document.querySelector('label[for="login-password"]').classList.toggle('hidden',['SUPERVISOR','VISUALIZAR'].includes(role));$('#login-error').textContent='';$('#login-password').value='';$(role==='SUPERVISOR'?'#login-supervisor':role==='VISUALIZAR'?'#login-button':'#login-password').focus();}
  async function initOnline(){
    init();$('#reset-demo').classList.add('hidden');$('#login-access').onchange=()=>chooseLogin($('#login-access').value);$('#enter-supervisor').onclick=()=>chooseLogin('SUPERVISOR');$('#enter-viewer').onclick=()=>chooseLogin('VISUALIZAR');$('#login-back').onclick=()=>chooseLogin($('#login-access').value);
    $('#login-form').onsubmit=async e=>{e.preventDefault();const button=$('#login-button');button.disabled=true;$('#login-error').textContent='';try{await api('/api/login',{method:'POST',body:JSON.stringify({role:loginRole,supervisor:$('#login-supervisor').value,password:$('#login-password').value})});$('#login-password').value='';applyOnline(await api('/api/bootstrap'));viewAtual=perfilAtual==='SUPERVISOR'?'apontamento':perfilAtual==='VISUALIZAR'?'dashboard':'inicio';portalUnit=state.convocacoes.find(c=>c.supervisor===supervisorAtual&&c.dataServico===portalDate)?.unidade||OBRAS[0]?.unidade||'Todas';render();}catch(err){$('#login-error').textContent=err.message;}finally{button.disabled=false;}};
    $('#login-button').disabled=true;try{await api('/api/logout',{method:'POST',body:'{}'});}catch(e){$('#login-error').textContent='Não foi possível iniciar um novo acesso. Atualize a página.';return;}finally{$('#login-password').value='';}$('#login-button').disabled=false;
    window.addEventListener('pageshow',event=>{if(event.persisted)window.location.reload();});
  }
  initOnline();

})();

