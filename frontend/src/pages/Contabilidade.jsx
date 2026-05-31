import { useEffect, useState } from "react";
import { api, brl } from "../api";
import { IcTrash, IcPlus, IcAlert } from "../components/Icons";

const hojeIso = new Date().toISOString().slice(0, 10);

export default function Contabilidade() {
  const [saude, setSaude] = useState(null);
  const [receitas, setReceitas] = useState([]);
  const [form, setForm] = useState({ descricao: "", valor: "", data: hojeIso });
  const [msg, setMsg] = useState("");
  const [erro, setErro] = useState("");

  const carregar = async () => {
    try {
      const [s, r] = await Promise.all([api.saudeContabil(), api.receitas()]);
      setSaude(s); setReceitas(r);
    } catch (e) { setErro(e.message); }
  };
  useEffect(() => { carregar(); }, []);

  const addReceita = async (e) => {
    e.preventDefault();
    setErro(""); setMsg("");
    try {
      await api.criarReceita({ descricao: form.descricao.trim(), valor: Number(form.valor) || 0, data: form.data });
      setForm({ descricao: "", valor: "", data: hojeIso });
      await carregar();
    } catch (err) { setErro(err.message); }
  };

  const removerReceita = async (id) => {
    try { await api.removerReceita(id); await carregar(); } catch (e) { setErro(e.message); }
  };

  const sinalizar = async () => {
    setErro(""); setMsg("");
    try {
      await api.sinalizarContador({ origem: "manual", gatilho: "manual" });
      setMsg("Sinalização enviada — contadores parceiros poderão se apresentar.");
      await carregar();
    } catch (e) { setErro(e.message); }
  };

  if (!saude) return <div className="content"><div className="empty">Carregando…</div></div>;

  const pct = Math.min(saude.pct_teto * 100, 100);
  const cor = pct >= 85 ? "var(--crimson)" : pct >= 60 ? "#9a6700" : "#2f7a3a";
  const temGatilho = saude.gatilhos.includes("teto");
  const procurando = saude.sinalizacao_status === "procurando" || saude.sinalizacao_status === "interesse_manifestado";

  return (
    <div className="content">
      <div style={{ marginBottom: 22 }}>
        <h2 style={{ fontFamily: "var(--display)", fontSize: 28, letterSpacing: "-.02em" }}>Contabilidade</h2>
        <p className="muted" style={{ marginTop: 4 }}>
          Saúde contábil derivada do seu faturamento. A plataforma organiza e conecta — o parecer é do contador.
        </p>
      </div>

      {/* Saúde contábil / teto MEI */}
      <div className="panel" style={{ marginBottom: 20, borderColor: temGatilho ? "var(--crimson)" : "var(--line)" }}>
        <div className="panel__head">
          <h3>Faturamento dos últimos 12 meses</h3>
          <span className={`tag ${temGatilho ? "tag-alerta" : "tag-aceito"}`}>{pct.toFixed(0)}% do teto MEI</span>
        </div>
        <div className="panel__body">
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
            <span className="price" style={{ fontFamily: "var(--display)", fontSize: 40 }}>{brl(saude.faturamento_12m)}</span>
            <span className="muted">de {brl(saude.teto_mei)} (teto do MEI)</span>
          </div>
          <div style={{ height: 10, background: "var(--cream)", borderRadius: 99, overflow: "hidden", marginTop: 14 }}>
            <div style={{ width: `${pct}%`, height: "100%", background: cor, transition: "width .3s ease" }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginTop: 8 }} className="muted">
            <span>Vindo de orçamentos: {brl(saude.fonte_orcamentos)} · avulso: {brl(saude.fonte_avulsa)}</span>
            <span>Faltam {brl(saude.restante)}</span>
          </div>

          <p style={{ marginTop: 14, fontSize: 14.5 }}>
            {saude.meses_ate_teto != null
              ? <>No ritmo atual (~{brl(saude.media_mensal)}/mês), você atinge o teto em <b>~{saude.meses_ate_teto} meses</b>{saude.projecao_estouro ? <> (≈ {new Date(saude.projecao_estouro + "T00:00:00").toLocaleDateString("pt-BR")})</> : null}.</>
              : <>Sem faturamento suficiente para projetar o teto ainda.</>}
            {" "}<span className="muted" style={{ fontSize: 12 }}># validar com contador</span>
          </p>
        </div>
      </div>

      {/* Gatilho + ponte com contador */}
      <div className="panel" style={{ marginBottom: 20 }}>
        <div className="panel__body">
          {temGatilho && (
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 14, color: "var(--crimson-deep)" }}>
              <IcAlert style={{ width: 20, flexShrink: 0, marginTop: 2 }} />
              <div>
                <b>Você passou de 75% do teto do MEI.</b>
                <div className="muted" style={{ fontSize: 13.5 }}>É hora de avaliar a virada para ME — um contador organiza isso por você.</div>
              </div>
            </div>
          )}
          {procurando ? (
            <div className="tag tag-pendente" style={{ padding: "8px 12px" }}>
              Procurando contador… seu caso entrou no mural (anonimizado). Você será avisado quando alguém se apresentar.
            </div>
          ) : (
            <button className="btn btn-primary" onClick={sinalizar}>Encontrar um contador</button>
          )}
          {msg && <div style={{ color: "#2f7a3a", fontSize: 13.5, marginTop: 10 }}>{msg}</div>}
          {erro && <div className="err" style={{ marginTop: 10 }}>{erro}</div>}
        </div>
      </div>

      {/* Faturamento avulso */}
      <div className="panel">
        <div className="panel__head"><h3>Lançar faturamento avulso</h3></div>
        <div className="panel__body">
          <p className="muted" style={{ marginBottom: 14 }}>
            Trabalhos que não passaram pela precificação (ex.: no dinheiro). Mantém a projeção do teto realista.
          </p>
          <form onSubmit={addReceita} style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr auto", gap: 10, alignItems: "end" }} className="row2">
            <div className="field" style={{ margin: 0 }}>
              <label>Descrição</label>
              <input className="input" value={form.descricao} onChange={(e) => setForm({ ...form, descricao: e.target.value })} required placeholder="Ex.: Tatuagem avulsa" />
            </div>
            <div className="field" style={{ margin: 0 }}>
              <label>Valor (R$)</label>
              <input className="input" type="number" min="0" step="0.01" value={form.valor} onChange={(e) => setForm({ ...form, valor: e.target.value })} required placeholder="0,00" />
            </div>
            <div className="field" style={{ margin: 0 }}>
              <label>Data</label>
              <input className="input" type="date" value={form.data} onChange={(e) => setForm({ ...form, data: e.target.value })} required />
            </div>
            <button className="btn btn-primary" type="submit"><IcPlus style={{ width: 16 }} /> Lançar</button>
          </form>

          {receitas.length > 0 && (
            <table style={{ marginTop: 18 }}>
              <thead><tr><th>Descrição</th><th>Valor</th><th>Data</th><th></th></tr></thead>
              <tbody>
                {receitas.map((r) => (
                  <tr key={r.id}>
                    <td><b>{r.descricao}</b></td>
                    <td className="price">{brl(r.valor)}</td>
                    <td className="muted">{new Date(r.data + "T00:00:00").toLocaleDateString("pt-BR")}</td>
                    <td style={{ textAlign: "right" }}>
                      <button className="icon-btn" title="Remover" onClick={() => removerReceita(r.id)}><IcTrash /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
