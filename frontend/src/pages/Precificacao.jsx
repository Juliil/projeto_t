import { useEffect, useMemo, useState } from "react";
import { api, brl } from "../api";
import { IcPlus, IcTrash, IcEdit } from "../components/Icons";

const r2 = (n) => Math.round((Number(n) || 0) * 100) / 100;
const VAZIO = { titulo: "", itens: [{ material_id: "", quantidade: 1 }], horas: "", valorHora: "", margem: "" };

const BADGE = {
  pendente: ["tag-pendente", "Pendente"],
  aceito: ["tag-aceito", "Aceito"],
  reprovado: ["tag-reprovado", "Reprovado"],
};

export default function Precificacao() {
  const [materiais, setMateriais] = useState([]);
  const [orcamentos, setOrcamentos] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [titulo, setTitulo] = useState("");
  const [itens, setItens] = useState(VAZIO.itens);
  const [horas, setHoras] = useState("");
  const [valorHora, setValorHora] = useState("");
  const [margem, setMargem] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [msg, setMsg] = useState("");
  const [erro, setErro] = useState("");

  const carregar = async () => {
    try {
      const [m, o] = await Promise.all([api.materiais(), api.orcamentos()]);
      setMateriais(m);
      setOrcamentos(o);
    } catch (e) { setErro(e.message); }
  };
  useEffect(() => { carregar(); }, []);

  const mapaMat = useMemo(
    () => Object.fromEntries(materiais.map((m) => [String(m.id), m])),
    [materiais]
  );

  const calc = useMemo(() => {
    const itensCalc = itens
      .filter((i) => i.material_id)
      .map((i) => {
        const mat = mapaMat[String(i.material_id)];
        const custo = mat ? Number(mat.custo_unitario) : 0;
        return { nome: mat?.nome || "—", quantidade: Number(i.quantidade) || 0, subtotal: r2(custo * (Number(i.quantidade) || 0)) };
      });
    const custoMateriais = r2(itensCalc.reduce((s, i) => s + i.subtotal, 0));
    const custoMaoObra = r2((Number(horas) || 0) * (Number(valorHora) || 0));
    const base = custoMateriais + custoMaoObra;
    const precoFinal = r2(base * (1 + (Number(margem) || 0) / 100));
    return { itensCalc, custoMateriais, custoMaoObra, base, precoFinal };
  }, [itens, horas, valorHora, margem, mapaMat]);

  const setItem = (idx, k) => (e) =>
    setItens((arr) => arr.map((it, i) => (i === idx ? { ...it, [k]: e.target.value } : it)));
  const addItem = () => setItens((arr) => [...arr, { material_id: "", quantidade: 1 }]);
  const delItem = (idx) => setItens((arr) => arr.filter((_, i) => i !== idx));

  const resetForm = () => {
    setEditandoId(null); setTitulo(""); setItens([{ material_id: "", quantidade: 1 }]);
    setHoras(""); setValorHora(""); setMargem("");
  };

  const editar = (o) => {
    setEditandoId(o.id);
    setTitulo(o.titulo);
    setItens(o.itens.length ? o.itens.map((i) => ({ material_id: String(i.material_id), quantidade: i.quantidade })) : [{ material_id: "", quantidade: 1 }]);
    setHoras(String(o.horas || ""));
    setValorHora(String(o.valor_hora || ""));
    setMargem(String(o.margem_pct || ""));
    setMsg(""); setErro("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const payload = () => ({
    titulo: titulo.trim() || "Orçamento",
    itens: itens.filter((i) => i.material_id).map((i) => ({ material_id: Number(i.material_id), quantidade: Number(i.quantidade) || 0 })),
    horas: Number(horas) || 0,
    valor_hora: Number(valorHora) || 0,
    margem_pct: Number(margem) || 0,
  });

  const salvar = async () => {
    setSalvando(true); setMsg(""); setErro("");
    try {
      if (editandoId) {
        await api.atualizarOrcamento(editandoId, payload());
        setMsg("Orçamento atualizado." + (orcAceito(editandoId) ? " Estoque ajustado pela diferença." : ""));
      } else {
        await api.salvarOrcamento(payload());
        setMsg("Orçamento salvo!");
      }
      resetForm();
      await carregar();
    } catch (e) { setErro(e.message); }
    finally { setSalvando(false); }
  };

  const orcAceito = (id) => orcamentos.find((o) => o.id === id)?.status === "aceito";

  const mudarStatus = async (o, status) => {
    setMsg(""); setErro("");
    try {
      await api.statusOrcamento(o.id, status);
      if (status === "aceito") setMsg(`"${o.titulo}" aceito — baixa no estoque feita.`);
      else if (status === "reprovado") setMsg(`"${o.titulo}" reprovado.`);
      await carregar();
    } catch (e) { setErro(e.message); }
  };

  const copiarResumo = async () => {
    const linhas = calc.itensCalc.map((i) => `• ${i.nome} x${i.quantidade} = ${brl(i.subtotal)}`).join("\n");
    const txt =
      `*${titulo.trim() || "Orçamento"}*\n` + (linhas ? `${linhas}\n` : "") +
      `Materiais: ${brl(calc.custoMateriais)}\nMão de obra: ${brl(calc.custoMaoObra)}\n` +
      `Margem: ${Number(margem) || 0}%\n*Preço final: ${brl(calc.precoFinal)}*`;
    try { await navigator.clipboard.writeText(txt); setMsg("Resumo copiado — é só colar no WhatsApp."); }
    catch (_) { setErro("Não consegui copiar."); }
  };

  return (
    <div className="content">
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontFamily: "var(--display)", fontSize: 28, letterSpacing: "-.02em" }}>Precificação</h2>
        <p className="muted" style={{ marginTop: 4 }}>Materiais + horas + margem = preço sugerido. Aceitar um orçamento dá baixa no estoque.</p>
      </div>

      {materiais.length === 0 && (
        <div className="err" style={{ marginBottom: 18 }}>
          Você ainda não tem materiais cadastrados — cadastre em <b>Materiais</b> para somar no orçamento.
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 20, alignItems: "start" }} className="prec-grid">
        <div className="panel">
          <div className="panel__head">
            <h3>{editandoId ? "Editar orçamento" : "Montar orçamento"}</h3>
            {editandoId && <button className="btn btn-ghost btn-sm" onClick={resetForm}>Cancelar edição</button>}
          </div>
          <div className="panel__body" style={{ display: "grid", gap: 16 }}>
            <div className="field" style={{ margin: 0 }}>
              <label>Título</label>
              <input className="input" value={titulo} onChange={(e) => setTitulo(e.target.value)} placeholder="Ex.: Tatuagem braço fechado" />
            </div>

            <div>
              <label style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-soft)" }}>Materiais usados</label>
              <div style={{ display: "grid", gap: 8, marginTop: 6 }}>
                {itens.map((it, idx) => {
                  const mat = mapaMat[String(it.material_id)];
                  const subtotal = mat ? r2(Number(mat.custo_unitario) * (Number(it.quantidade) || 0)) : 0;
                  return (
                    <div key={idx} style={{ display: "grid", gridTemplateColumns: "1fr 90px auto auto", gap: 8, alignItems: "center" }}>
                      <select className="input" value={it.material_id} onChange={setItem(idx, "material_id")}>
                        <option value="">Selecione…</option>
                        {materiais.map((m) => (
                          <option key={m.id} value={m.id}>{m.nome} ({brl(m.custo_unitario)}/{m.unidade})</option>
                        ))}
                      </select>
                      <input className="input" type="number" min="0" step="0.01" value={it.quantidade} onChange={setItem(idx, "quantidade")} />
                      <span className="price" style={{ minWidth: 80, textAlign: "right" }}>{brl(subtotal)}</span>
                      <button className="icon-btn" title="Remover" onClick={() => delItem(idx)}><IcTrash /></button>
                    </div>
                  );
                })}
              </div>
              <button className="btn btn-ghost btn-sm" style={{ marginTop: 10 }} onClick={addItem}><IcPlus style={{ width: 16 }} /> Adicionar material</button>
            </div>

            <div className="row2">
              <div className="field" style={{ margin: 0 }}>
                <label>Horas de trabalho</label>
                <input className="input" type="number" min="0" step="0.5" value={horas} onChange={(e) => setHoras(e.target.value)} placeholder="0" />
              </div>
              <div className="field" style={{ margin: 0 }}>
                <label>Valor por hora (R$)</label>
                <input className="input" type="number" min="0" step="0.01" value={valorHora} onChange={(e) => setValorHora(e.target.value)} placeholder="0,00" />
              </div>
            </div>
            <div className="field" style={{ margin: 0 }}>
              <label>Margem (%) <span className="muted">— lucro sobre o custo</span></label>
              <input className="input" type="number" min="0" step="1" value={margem} onChange={(e) => setMargem(e.target.value)} placeholder="0" />
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel__head"><h3>Resultado</h3></div>
          <div className="panel__body" style={{ display: "grid", gap: 10 }}>
            <Linha k="Materiais" v={brl(calc.custoMateriais)} />
            <Linha k="Mão de obra" v={brl(calc.custoMaoObra)} />
            <Linha k="Custo total" v={brl(calc.base)} />
            <Linha k={`Margem (${Number(margem) || 0}%)`} v={brl(calc.precoFinal - calc.base)} />
            <div style={{ borderTop: "1px solid var(--line)", margin: "6px 0" }} />
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <span style={{ fontWeight: 600 }}>Preço final</span>
              <span className="price" style={{ fontFamily: "var(--display)", fontSize: 30, color: "var(--crimson)" }}>{brl(calc.precoFinal)}</span>
            </div>
            {msg && <div style={{ color: "#2f7a3a", fontSize: 13.5 }}>{msg}</div>}
            {erro && <div className="err">{erro}</div>}
            <div style={{ display: "flex", gap: 10, marginTop: 6 }}>
              <button className="btn btn-ghost btn-block" onClick={copiarResumo}>Copiar resumo</button>
              <button className="btn btn-primary btn-block" onClick={salvar} disabled={salvando}>
                {salvando ? "Salvando…" : editandoId ? "Atualizar" : "Salvar"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="panel" style={{ marginTop: 24 }}>
        <div className="panel__head"><h3>Orçamentos salvos</h3></div>
        {orcamentos.length === 0 ? (
          <div className="empty">Nenhum orçamento salvo ainda.</div>
        ) : (
          <table>
            <thead><tr><th>Título</th><th>Preço</th><th>Status</th><th>Quando</th><th></th></tr></thead>
            <tbody>
              {orcamentos.map((o) => {
                const [cls, label] = BADGE[o.status] || BADGE.pendente;
                return (
                  <tr key={o.id} style={editandoId === o.id ? { background: "var(--paper-2)" } : null}>
                    <td><b>{o.titulo}</b></td>
                    <td className="price">{brl(o.preco_final)}</td>
                    <td><span className={`tag ${cls}`}>{label}</span></td>
                    <td className="muted">{new Date(o.criado_em).toLocaleDateString("pt-BR")}</td>
                    <td>
                      <div className="right-actions" style={{ justifyContent: "flex-end" }}>
                        {o.status !== "aceito" && (
                          <button className="btn btn-primary btn-sm" onClick={() => mudarStatus(o, "aceito")}>Aceitar</button>
                        )}
                        {(o.status === "pendente" || o.status === "aceito") && (
                          <button className="btn btn-ghost btn-sm" title="Editar" onClick={() => editar(o)}><IcEdit style={{ width: 15 }} /></button>
                        )}
                        {o.status !== "reprovado" && (
                          <button className="btn btn-ghost btn-sm" onClick={() => mudarStatus(o, "reprovado")}>Reprovar</button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function Linha({ k, v }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14.5 }}>
      <span className="muted">{k}</span>
      <span>{v}</span>
    </div>
  );
}
