import { useEffect, useMemo, useState } from "react";
import { api, brl } from "../api";
import { IcChevron, IcTrash } from "../components/Icons";

const DIAS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
const STATUS_CLS = { aceito: "tag-aceito", pendente: "tag-pendente", reprovado: "tag-reprovado" };

const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const hojeIso = iso(new Date());

export default function Agenda({ onNav }) {
  const [orcamentos, setOrcamentos] = useState([]);
  const [ref, setRef] = useState(() => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), 1); });
  const [diaSel, setDiaSel] = useState(null); // string iso
  const [escolha, setEscolha] = useState("");
  const [erro, setErro] = useState("");

  const carregar = async () => {
    try { setOrcamentos(await api.orcamentos()); } catch (e) { setErro(e.message); }
  };
  useEffect(() => { carregar(); }, []);

  // Mapa diaIso -> orçamentos agendados
  const porDia = useMemo(() => {
    const m = {};
    for (const o of orcamentos) {
      if (!o.agendado_em) continue;
      (m[o.agendado_em] = m[o.agendado_em] || []).push(o);
    }
    return m;
  }, [orcamentos]);

  // Grade de 6 semanas
  const celulas = useMemo(() => {
    const ano = ref.getFullYear(), mes = ref.getMonth();
    const inicio = new Date(ano, mes, 1);
    const offset = inicio.getDay(); // 0=Dom
    const base = new Date(ano, mes, 1 - offset);
    return Array.from({ length: 42 }, (_, i) => {
      const d = new Date(base.getFullYear(), base.getMonth(), base.getDate() + i);
      return { d, iso: iso(d), doMes: d.getMonth() === mes };
    });
  }, [ref]);

  const mesAtual = `${MESES[ref.getMonth()]} ${ref.getFullYear()}`;
  const navMes = (delta) => setRef(new Date(ref.getFullYear(), ref.getMonth() + delta, 1));
  const irHoje = () => { const d = new Date(); setRef(new Date(d.getFullYear(), d.getMonth(), 1)); };

  // Resumo do mês visível
  const doMesEventos = useMemo(
    () => orcamentos.filter((o) => o.agendado_em && o.agendado_em.slice(0, 7) === `${ref.getFullYear()}-${String(ref.getMonth() + 1).padStart(2, "0")}`),
    [orcamentos, ref]
  );
  const faturamentoMes = doMesEventos.filter((o) => o.status === "aceito").reduce((s, o) => s + Number(o.preco_final), 0);

  const naoAgendados = useMemo(() => orcamentos.filter((o) => !o.agendado_em && o.status !== "reprovado"), [orcamentos]);

  const agendar = async (id, data) => {
    setErro("");
    try { await api.agendarOrcamento(id, data); await carregar(); }
    catch (e) { setErro(e.message); }
  };

  const abrirDia = (iso) => { setDiaSel(iso); setEscolha(""); };
  const eventosDoDia = diaSel ? (porDia[diaSel] || []) : [];

  return (
    <div className="content" style={{ maxWidth: 1200 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h2 style={{ fontFamily: "var(--display)", fontSize: 28, letterSpacing: "-.02em" }}>Agenda</h2>
          <p className="muted" style={{ marginTop: 4 }}>
            {doMesEventos.length} trabalho(s) no mês · <b style={{ color: "#2f7a3a" }}>{brl(faturamentoMes)}</b> agendados (aceitos)
          </p>
        </div>
        <div className="cal-nav">
          <button className="icon-btn" onClick={() => navMes(-1)} title="Mês anterior"><IcChevron /></button>
          <span className="cal-title">{mesAtual}</span>
          <button className="icon-btn" onClick={() => navMes(1)} title="Próximo mês"><IcChevron style={{ transform: "rotate(180deg)" }} /></button>
          <button className="btn btn-ghost btn-sm" onClick={irHoje}>Hoje</button>
        </div>
      </div>

      {erro && <div className="err" style={{ marginBottom: 14 }}>{erro}</div>}

      <div className="cal">
        <div className="cal-head">
          {DIAS.map((d) => <div key={d} className="cal-dow">{d}</div>)}
        </div>
        <div className="cal-grid">
          {celulas.map((c) => {
            const evs = porDia[c.iso] || [];
            return (
              <button
                key={c.iso}
                className={`cal-cell ${c.doMes ? "" : "fora"} ${c.iso === hojeIso ? "hoje" : ""}`}
                onClick={() => abrirDia(c.iso)}
              >
                <span className="cal-num">{c.d.getDate()}</span>
                <span className="cal-evs">
                  {evs.slice(0, 3).map((o) => (
                    <span key={o.id} className={`cal-ev tag ${STATUS_CLS[o.status] || ""}`} title={`${o.titulo} — ${brl(o.preco_final)}`}>
                      {o.titulo}
                    </span>
                  ))}
                  {evs.length > 3 && <span className="muted" style={{ fontSize: 11 }}>+{evs.length - 3}</span>}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {diaSel && (
        <div className="overlay" onClick={(e) => e.target === e.currentTarget && setDiaSel(null)}>
          <div className="modal">
            <h3>{new Date(diaSel + "T00:00:00").toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long" })}</h3>

            {eventosDoDia.length === 0 ? (
              <p className="muted" style={{ margin: "4px 0 16px" }}>Nenhum trabalho agendado neste dia.</p>
            ) : (
              <div style={{ display: "grid", gap: 8, margin: "6px 0 16px" }}>
                {eventosDoDia.map((o) => (
                  <div key={o.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, border: "1px solid var(--line)", borderRadius: 10, padding: "10px 12px" }}>
                    <div>
                      <b>{o.titulo}</b> <span className={`tag ${STATUS_CLS[o.status] || ""}`}>{o.status}</span>
                      <div className="muted" style={{ fontSize: 13 }}>{brl(o.preco_final)}</div>
                    </div>
                    <button className="icon-btn" title="Desagendar" onClick={() => agendar(o.id, null)}><IcTrash /></button>
                  </div>
                ))}
              </div>
            )}

            <div className="field" style={{ margin: 0 }}>
              <label>Agendar um orçamento neste dia</label>
              <div style={{ display: "flex", gap: 8 }}>
                <select className="input" value={escolha} onChange={(e) => setEscolha(e.target.value)}>
                  <option value="">Selecione…</option>
                  {naoAgendados.map((o) => (
                    <option key={o.id} value={o.id}>{o.titulo} — {brl(o.preco_final)} ({o.status})</option>
                  ))}
                </select>
                <button className="btn btn-primary" disabled={!escolha} onClick={() => agendar(Number(escolha), diaSel).then(() => setEscolha(""))}>Agendar</button>
              </div>
              {naoAgendados.length === 0 && (
                <p className="muted" style={{ fontSize: 12.5, marginTop: 8 }}>
                  Sem orçamentos livres. Crie um em <button className="linklike" onClick={() => onNav("precificacao")}>Precificação</button>.
                </p>
              )}
            </div>

            <div style={{ marginTop: 18 }}>
              <button className="btn btn-ghost btn-block" onClick={() => setDiaSel(null)}>Fechar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
