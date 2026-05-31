import { useEffect, useState } from "react";
import { api, brl } from "../api";
import { IcTrash, IcPlus, IcAlert } from "../components/Icons";

const hojeIso = new Date().toISOString().slice(0, 10);
const ESCOPOS = [
  { id: "faturamento", label: "Faturamento (12 meses, projeção)" },
  { id: "estoque", label: "Estoque (itens e valor)" },
  { id: "regime_fiscal", label: "Regime fiscal (MEI/ME…)" },
];

export default function Contabilidade() {
  const [saude, setSaude] = useState(null);
  const [receitas, setReceitas] = useState([]);
  const [interesses, setInteresses] = useState([]);
  const [vinculo, setVinculo] = useState(null);
  const [chat, setChat] = useState([]);
  const [chatCorpo, setChatCorpo] = useState("");
  const [escopoAlvo, setEscopoAlvo] = useState(null); // manifestação sendo aceita
  const [escopoSel, setEscopoSel] = useState(["faturamento"]);
  const [form, setForm] = useState({ descricao: "", valor: "", data: hojeIso });
  const [msg, setMsg] = useState("");
  const [erro, setErro] = useState("");

  const carregar = async () => {
    try {
      const [s, r, i, v] = await Promise.all([
        api.saudeContabil(), api.receitas(), api.interesses().catch(() => []), api.vinculoContabil().catch(() => null),
      ]);
      setSaude(s); setReceitas(r); setInteresses(i); setVinculo(v);
      if (v) setChat(await api.mensagensVinculo().catch(() => []));
    } catch (e) { setErro(e.message); }
  };
  useEffect(() => { carregar(); }, []);

  const toggleEscopo = (id) =>
    setEscopoSel((arr) => (arr.includes(id) ? arr.filter((x) => x !== id) : [...arr, id]));

  const confirmarAceite = async () => {
    try {
      await api.aceitarInteresse(escopoAlvo.id, escopoSel);
      setEscopoAlvo(null); setMsg("Contador vinculado! Os dados liberados já estão disponíveis para ele.");
      await carregar();
    } catch (e) { setErro(e.message); }
  };

  const enviarChat = async () => {
    if (!chatCorpo.trim()) return;
    try {
      await api.enviarMensagemEstudio(chatCorpo.trim());
      setChatCorpo("");
      setChat(await api.mensagensVinculo());
    } catch (e) { setErro(e.message); }
  };

  const encerrar = async () => {
    if (!window.confirm("Encerrar o vínculo? O acesso do contador aos seus dados é cortado na hora.")) return;
    try { await api.encerrarVinculo(); await carregar(); } catch (e) { setErro(e.message); }
  };

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

      {msg && <div style={{ color: "#2f7a3a", fontSize: 13.5, marginBottom: 14 }}>{msg}</div>}
      {erro && <div className="err" style={{ marginBottom: 14 }}>{erro}</div>}

      {/* Ponte com contador */}
      {vinculo ? (
        <>
          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel__head">
              <h3>Seu contador</h3>
              <button className="btn btn-ghost btn-sm" onClick={encerrar}>Encerrar vínculo</button>
            </div>
            <div className="panel__body">
              <b>{vinculo.contador_nome}</b>{" "}
              <span className="tag tag-aceito">CRC {vinculo.crc}{vinculo.uf_crc ? `/${vinculo.uf_crc}` : ""}</span>
              <p className="muted" style={{ fontSize: 13, marginTop: 6 }}>
                Dados liberados: {vinculo.escopo_dados.length ? vinculo.escopo_dados.join(", ") : "nenhum"}. Você pode encerrar quando quiser — o acesso é cortado na hora.
              </p>
            </div>
          </div>
          <div className="panel" style={{ marginBottom: 20 }}>
            <div className="panel__head"><h3>Conversa com o contador</h3></div>
            <div className="panel__body">
              <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 240, overflowY: "auto", marginBottom: 12 }}>
                {chat.length === 0 && <span className="muted">Sem mensagens ainda.</span>}
                {chat.map((m) => (
                  <div key={m.id} style={{ alignSelf: m.autor === "estudio" ? "flex-end" : "flex-start", maxWidth: "80%",
                    background: m.autor === "estudio" ? "var(--crimson)" : "var(--cream)", color: m.autor === "estudio" ? "#fff" : "var(--ink)",
                    padding: "8px 12px", borderRadius: 12, fontSize: 14 }}>{m.corpo}</div>
                ))}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <input className="input" value={chatCorpo} onChange={(e) => setChatCorpo(e.target.value)} onKeyDown={(e) => e.key === "Enter" && enviarChat()} placeholder="Escreva uma mensagem…" />
                <button className="btn btn-primary" onClick={enviarChat}>Enviar</button>
              </div>
            </div>
          </div>
        </>
      ) : (
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
                Procurando contador… seu caso entrou no mural (anonimizado).
              </div>
            ) : (
              <button className="btn btn-primary" onClick={sinalizar}>Encontrar um contador</button>
            )}

            {interesses.filter((i) => i.status === "pendente").length > 0 && (
              <div style={{ marginTop: 16, display: "grid", gap: 10 }}>
                <b>Contadores interessados</b>
                {interesses.filter((i) => i.status === "pendente").map((i) => (
                  <div key={i.id} style={{ border: "1px solid var(--line)", borderRadius: 10, padding: "12px 14px", display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
                    <div>
                      <b>{i.contador_nome}</b>{" "}
                      <span className="tag tag-aceito">CRC {i.crc}{i.uf_crc ? `/${i.uf_crc}` : ""}</span>
                      <div className="muted" style={{ fontSize: 13.5, marginTop: 4 }}>{i.mensagem_inicial}</div>
                    </div>
                    <button className="btn btn-primary btn-sm" onClick={() => { setEscopoAlvo(i); setEscopoSel(["faturamento"]); }}>Aceitar</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

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

      {escopoAlvo && (
        <div className="overlay" onClick={(e) => e.target === e.currentTarget && setEscopoAlvo(null)}>
          <div className="modal">
            <h3>Liberar dados para {escopoAlvo.contador_nome}</h3>
            <p className="muted" style={{ margin: "-6px 0 14px" }}>
              Escolha o que o contador poderá ver. Só o marcado é compartilhado — você pode encerrar e cortar o acesso a qualquer momento (LGPD).
            </p>
            <div style={{ display: "grid", gap: 10 }}>
              {ESCOPOS.map((e) => (
                <label key={e.id} className="opt" style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}>
                  <input type="checkbox" checked={escopoSel.includes(e.id)} onChange={() => toggleEscopo(e.id)} />
                  {e.label}
                </label>
              ))}
            </div>
            <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
              <button className="btn btn-ghost btn-block" onClick={() => setEscopoAlvo(null)}>Cancelar</button>
              <button className="btn btn-primary btn-block" onClick={confirmarAceite}>Aceitar e liberar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
