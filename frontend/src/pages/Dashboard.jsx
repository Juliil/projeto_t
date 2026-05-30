import { useEffect, useMemo, useState } from "react";
import { api, brl } from "../api";
import { useAuth } from "../context/AuthContext";
import { IcBox, IcCalc, IcAlert } from "../components/Icons";

const emFalta = (m) => Number(m.estoque_minimo) > 0 && Number(m.estoque) <= Number(m.estoque_minimo);

export default function Dashboard({ onNav }) {
  const { user } = useAuth();
  const [materiais, setMateriais] = useState([]);
  const [orcamentos, setOrcamentos] = useState([]);
  const [limiteMei, setLimiteMei] = useState(81000);

  useEffect(() => {
    (async () => {
      const [m, o, cfg] = await Promise.all([
        api.materiais().catch(() => []),
        api.orcamentos().catch(() => []),
        api.config().catch(() => ({})),
      ]);
      setMateriais(m); setOrcamentos(o);
      if (cfg?.limite_mei_anual) setLimiteMei(cfg.limite_mei_anual);
    })();
  }, []);

  const perfil = user?.perfil || {};
  const isMEI = perfil.regime === "MEI";
  const ano = new Date().getFullYear();

  const aceitosAno = useMemo(
    () => orcamentos.filter((o) => o.status === "aceito" && new Date(o.criado_em).getFullYear() === ano),
    [orcamentos, ano]
  );
  const faturamentoAno = useMemo(() => aceitosAno.reduce((s, o) => s + Number(o.preco_final), 0), [aceitosAno]);
  const ticketMedio = aceitosAno.length ? faturamentoAno / aceitosAno.length : 0;
  const pendentes = useMemo(() => orcamentos.filter((o) => o.status === "pendente").length, [orcamentos]);
  const aRepor = useMemo(() => materiais.filter(emFalta), [materiais]);
  const valorEstoque = useMemo(
    () => materiais.reduce((s, m) => s + Number(m.custo_unitario) * Number(m.estoque), 0),
    [materiais]
  );

  const pctLimite = limiteMei ? Math.min((faturamentoAno / limiteMei) * 100, 100) : 0;
  const corLimite = pctLimite >= 85 ? "var(--crimson)" : pctLimite >= 60 ? "#9a6700" : "#2f7a3a";
  const contexto = [perfil.nome_estudio, perfil.cidade].filter(Boolean).join(" · ");

  return (
    <div className="content">
      <div style={{ marginBottom: 22 }}>
        <h2 style={{ fontFamily: "var(--display)", fontSize: 30, letterSpacing: "-.02em" }}>
          Olá, {user?.nome?.split(" ")[0]} 👋
        </h2>
        <p className="muted" style={{ marginTop: 4 }}>
          {contexto || "Bem-vindo ao seu painel."} · {isMEI ? "MEI" : perfil.regime || "Regime não informado"} — aqui está a saúde do seu estúdio em {ano}.
        </p>
      </div>

      {/* Faturamento + limite MEI */}
      <div className="panel" style={{ marginBottom: 20 }}>
        <div className="panel__head"><h3>Faturamento em {ano}</h3>{isMEI && <span className="tag tag-pendente">MEI</span>}</div>
        <div className="panel__body">
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
            <span className="price" style={{ fontFamily: "var(--display)", fontSize: 40, color: "var(--ink)" }}>{brl(faturamentoAno)}</span>
            <span className="muted">de orçamentos aceitos ({aceitosAno.length})</span>
          </div>

          {isMEI && (
            <div style={{ marginTop: 18 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 6 }}>
                <span className="muted">Limite anual do MEI · {brl(limiteMei)}</span>
                <span style={{ fontWeight: 600, color: corLimite }}>{pctLimite.toFixed(0)}% usado</span>
              </div>
              <div style={{ height: 10, background: "var(--cream)", borderRadius: 99, overflow: "hidden" }}>
                <div style={{ width: `${pctLimite}%`, height: "100%", background: corLimite, transition: "width .3s ease" }} />
              </div>
              <p className="muted" style={{ fontSize: 12.5, marginTop: 8 }}>
                {faturamentoAno >= limiteMei
                  ? "⚠️ Você atingiu o limite anual do MEI — avalie a migração de regime com seu contador."
                  : `Faltam ${brl(limiteMei - faturamentoAno)} para o limite anual.`}
                {" "}# FISCAL: validar com contador.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Atividade */}
      <div className="cards">
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("precificacao")}>
          <div className="k">Orçamentos aceitos ({ano})</div><div className="v">{aceitosAno.length}</div>
        </button>
        <div className="stat"><div className="k">Ticket médio</div><div className="v" style={{ fontSize: 26 }}>{brl(ticketMedio)}</div></div>
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("precificacao")}>
          <div className="k">Orçamentos pendentes</div><div className="v">{pendentes}</div>
        </button>
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("materiais")}>
          <div className="k">Valor em estoque</div><div className="v" style={{ fontSize: 26 }}>{brl(valorEstoque)}</div>
        </button>
      </div>

      {/* Alerta de reposição */}
      {aRepor.length > 0 && (
        <div className="panel" style={{ marginTop: 8, marginBottom: 24, borderColor: "var(--crimson)" }}>
          <div className="panel__head" style={{ borderBottomColor: "#f6d7d2" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--crimson-deep)" }}>
              <IcAlert style={{ width: 18 }} /> {aRepor.length} material(is) precisam de reposição
            </h3>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("materiais")}>Ver materiais</button>
          </div>
          <div className="panel__body" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {aRepor.map((m) => (
              <span key={m.id} className="tag tag-alerta">{m.nome} — {Number(m.estoque)}{m.unidade} (mín. {Number(m.estoque_minimo)})</span>
            ))}
          </div>
        </div>
      )}

      {/* Comece por aqui */}
      <div className="panel">
        <div className="panel__head"><h3>Comece por aqui</h3></div>
        <div className="panel__body" style={{ display: "grid", gap: 12 }}>
          <button className="opt" onClick={() => onNav("materiais")}>
            <b style={{ display: "flex", alignItems: "center", gap: 10 }}><IcBox style={{ width: 18 }} /> Materiais e estoque</b>
            <span className="muted" style={{ display: "block", marginTop: 4 }}>Cadastre insumos, controle estoque e veja a economia ZFM.</span>
          </button>
          <button className="opt" onClick={() => onNav("precificacao")}>
            <b style={{ display: "flex", alignItems: "center", gap: 10 }}><IcCalc style={{ width: 18 }} /> Precificar um trabalho</b>
            <span className="muted" style={{ display: "block", marginTop: 4 }}>Aceitar um orçamento dá baixa no estoque e soma no faturamento.</span>
          </button>
        </div>
      </div>
    </div>
  );
}
