import { useEffect, useState } from "react";
import { api, brl } from "../api";
import { useAuth } from "../context/AuthContext";
import { IcReceipt, IcLogout } from "../components/Icons";

const ESCOPO_LABEL = { faturamento: "Faturamento", estoque: "Estoque", regime_fiscal: "Regime fiscal" };

export default function ContadorPortal() {
  const { user, empresa, logout } = useAuth();
  const [me, setMe] = useState(null);
  const [aba, setAba] = useState("mural");
  const [leads, setLeads] = useState([]);
  const [vinculos, setVinculos] = useState([]);
  const [erro, setErro] = useState("");

  // modal de interesse
  const [leadSel, setLeadSel] = useState(null);
  const [mensagem, setMensagem] = useState("");

  const carregar = async () => {
    try {
      const [m, l, v] = await Promise.all([api.contadorMe(), api.contadorLeads(), api.contadorVinculos()]);
      setMe(m); setLeads(l); setVinculos(v);
    } catch (e) { setErro(e.message); }
  };
  useEffect(() => { carregar(); }, []);

  const manifestar = async () => {
    try {
      await api.manifestarInteresse(leadSel.sinalizacao_id, mensagem.trim() || "Tenho interesse em ajudar.");
      setLeadSel(null); setMensagem("");
      await carregar();
    } catch (e) { setErro(e.message); }
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--paper)" }}>
      <div className="topbar" style={{ position: "sticky", top: 0 }}>
        <h1 style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="dot" style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--crimson)", display: "inline-block" }} />
          {empresa} · <span style={{ color: "var(--muted)", fontSize: 16 }}>Portal do Contador</span>
        </h1>
        <div className="right" style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {me && <span className="tag tag-aceito">CRC {me.crc} · {me.status_crc}</span>}
          <span className="muted">{user?.nome}</span>
          <button className="icon-btn" title="Sair" onClick={logout}><IcLogout /></button>
        </div>
      </div>

      <div className="content" style={{ maxWidth: 1100 }}>
        <div className="tabs" style={{ maxWidth: 360, marginBottom: 20 }}>
          <button className={aba === "mural" ? "active" : ""} onClick={() => setAba("mural")}>Mural de leads</button>
          <button className={aba === "clientes" ? "active" : ""} onClick={() => setAba("clientes")}>Meus clientes</button>
        </div>

        {erro && <div className="err" style={{ marginBottom: 14 }}>{erro}</div>}

        {aba === "mural" && (
          <>
            <p className="muted" style={{ marginBottom: 16 }}>
              Estúdios que sinalizaram necessidade. Dados anonimizados até o aceite — sem nome, CNPJ ou PII.
            </p>
            {leads.length === 0 ? (
              <div className="panel"><div className="empty">Nenhum lead disponível no momento.</div></div>
            ) : (
              <div className="store-grid">
                {leads.map((l) => (
                  <div key={l.sinalizacao_id} className="listing">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <h4>{l.segmento}</h4>
                      <span className="tag tag-pendente">{(l.pct_teto * 100).toFixed(0)}% do teto</span>
                    </div>
                    <div className="desc">
                      Faturamento: <b>{l.faixa_faturamento}</b><br />
                      Região: {l.regiao}<br />
                      Gatilho: {l.gatilho}
                    </div>
                    <div className="foot">
                      <span className="by">{new Date(l.criado_em).toLocaleDateString("pt-BR")}</span>
                      {l.ja_manifestei ? (
                        <span className="tag tag-aceito">Interesse enviado</span>
                      ) : (
                        <button className="btn btn-primary btn-sm" onClick={() => { setLeadSel(l); setMensagem(""); }}>Tenho interesse</button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {aba === "clientes" && (
          <ClientesContador vinculos={vinculos} />
        )}
      </div>

      {leadSel && (
        <div className="overlay" onClick={(e) => e.target === e.currentTarget && setLeadSel(null)}>
          <div className="modal">
            <h3>Manifestar interesse</h3>
            <p className="muted" style={{ margin: "-6px 0 14px" }}>
              Sua mensagem inicial vai para o estúdio. Os dados completos só após o aceite dele.
            </p>
            <div className="field">
              <label>Mensagem inicial</label>
              <textarea className="input" rows={4} value={mensagem} onChange={(e) => setMensagem(e.target.value)}
                placeholder="Ex.: Sou especialista em MEI→ME no AM e posso organizar sua virada." />
            </div>
            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button className="btn btn-ghost btn-block" onClick={() => setLeadSel(null)}>Cancelar</button>
              <button className="btn btn-primary btn-block" onClick={manifestar}>Enviar interesse</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ClientesContador({ vinculos }) {
  const [sel, setSel] = useState(null);
  const [dados, setDados] = useState(null);
  const [msgs, setMsgs] = useState([]);
  const [corpo, setCorpo] = useState("");
  const [erro, setErro] = useState("");

  const abrir = async (v) => {
    setSel(v); setErro(""); setDados(null); setMsgs([]);
    try {
      const [d, m] = await Promise.all([api.contadorDados(v.id), api.contadorMensagens(v.id)]);
      setDados(d); setMsgs(m);
    } catch (e) { setErro(e.message); }
  };

  const enviar = async () => {
    if (!corpo.trim()) return;
    try {
      await api.enviarMensagemContador(sel.id, corpo.trim());
      setCorpo("");
      setMsgs(await api.contadorMensagens(sel.id));
    } catch (e) { setErro(e.message); }
  };

  if (vinculos.length === 0) {
    return <div className="panel"><div className="empty">Nenhum cliente vinculado ainda. Manifeste interesse num lead do mural.</div></div>;
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 20, alignItems: "start" }} className="prec-grid">
      <div className="panel">
        <div className="panel__head"><h3>Clientes</h3></div>
        <div style={{ display: "grid" }}>
          {vinculos.map((v) => (
            <button key={v.id} className="opt" style={{ borderRadius: 0, border: "none", borderBottom: "1px solid var(--line)" }} onClick={() => abrir(v)}>
              <b>{v.estudio_nome}</b>
              <span className="muted" style={{ display: "block", marginTop: 2, fontSize: 12.5 }}>
                Liberou: {v.escopo_dados.map((e) => ESCOPO_LABEL[e] || e).join(", ") || "—"}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div>
        {erro && <div className="err" style={{ marginBottom: 12 }}>{erro}</div>}
        {!sel ? (
          <div className="panel"><div className="empty">Selecione um cliente para ver os dados e conversar.</div></div>
        ) : (
          <>
            <div className="panel" style={{ marginBottom: 16 }}>
              <div className="panel__head"><h3>{sel.estudio_nome} · dados consentidos</h3></div>
              <div className="panel__body">
                {!dados ? <span className="muted">Carregando…</span> : <PacoteDados dados={dados.dados} />}
              </div>
            </div>
            <div className="panel">
              <div className="panel__head"><h3>Conversa</h3></div>
              <div className="panel__body">
                <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 260, overflowY: "auto", marginBottom: 12 }}>
                  {msgs.length === 0 && <span className="muted">Sem mensagens ainda.</span>}
                  {msgs.map((m) => (
                    <div key={m.id} style={{ alignSelf: m.autor === "contador" ? "flex-end" : "flex-start", maxWidth: "80%",
                      background: m.autor === "contador" ? "var(--crimson)" : "var(--cream)", color: m.autor === "contador" ? "#fff" : "var(--ink)",
                      padding: "8px 12px", borderRadius: 12, fontSize: 14 }}>
                      {m.corpo}
                    </div>
                  ))}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <input className="input" value={corpo} onChange={(e) => setCorpo(e.target.value)} onKeyDown={(e) => e.key === "Enter" && enviar()} placeholder="Escreva uma mensagem…" />
                  <button className="btn btn-primary" onClick={enviar}>Enviar</button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function PacoteDados({ dados }) {
  if (!dados || Object.keys(dados).length === 0) return <span className="muted">Nenhum dado no escopo liberado.</span>;
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {dados.faturamento && (
        <div className="stat">
          <div className="k">Faturamento 12 meses</div>
          <div className="v" style={{ fontSize: 24 }}>{brl(dados.faturamento.faturamento_12m)}</div>
          <span className="muted" style={{ fontSize: 12.5 }}>
            {(dados.faturamento.pct_teto * 100).toFixed(0)}% do teto · ~{brl(dados.faturamento.media_mensal)}/mês
            {dados.faturamento.projecao_estouro ? ` · estouro ≈ ${new Date(dados.faturamento.projecao_estouro + "T00:00:00").toLocaleDateString("pt-BR")}` : ""}
          </span>
        </div>
      )}
      {dados.estoque && (
        <div className="stat">
          <div className="k">Estoque</div>
          <div className="v" style={{ fontSize: 24 }}>{brl(dados.estoque.valor_total)}</div>
          <span className="muted" style={{ fontSize: 12.5 }}>{dados.estoque.itens} itens</span>
        </div>
      )}
      {dados.regime_fiscal && (
        <div className="stat"><div className="k">Regime fiscal</div><div className="v" style={{ fontSize: 20 }}>{dados.regime_fiscal}</div></div>
      )}
    </div>
  );
}
