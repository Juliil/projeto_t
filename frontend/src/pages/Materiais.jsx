import { useEffect, useState } from "react";
import { api, brl } from "../api";
import { IcPlus, IcTrash, IcEdit, IcAlert } from "../components/Icons";

const CATEGORIAS = ["Agulhas", "Cartuchos", "Tintas", "Biqueiras", "Descartáveis", "Biossegurança", "Outros"];
const UNIDADES = ["un", "ml", "g", "caixa", "sessão"];

const VAZIO = { nome: "", categoria: "Agulhas", unidade: "un", custo_unitario: "", estoque: "", estoque_minimo: "" };

const emFalta = (m) => Number(m.estoque_minimo) > 0 && Number(m.estoque) <= Number(m.estoque_minimo);

export default function Materiais() {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [aberto, setAberto] = useState(false);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(VAZIO);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  const carregar = async () => {
    setCarregando(true);
    try {
      setItens(await api.materiais());
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => { carregar(); }, []);

  const abrirNovo = () => { setEditando(null); setForm(VAZIO); setErro(""); setAberto(true); };
  const abrirEdicao = (m) => {
    setEditando(m);
    setForm({
      nome: m.nome, categoria: m.categoria || "Outros", unidade: m.unidade,
      custo_unitario: m.custo_unitario, estoque: m.estoque, estoque_minimo: m.estoque_minimo,
    });
    setErro(""); setAberto(true);
  };

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const salvar = async (e) => {
    e.preventDefault();
    setSalvando(true); setErro("");
    const payload = {
      nome: form.nome.trim(),
      categoria: form.categoria,
      unidade: form.unidade,
      custo_unitario: Number(form.custo_unitario) || 0,
      estoque: Number(form.estoque) || 0,
      estoque_minimo: Number(form.estoque_minimo) || 0,
    };
    try {
      if (editando) await api.atualizarMaterial(editando.id, payload);
      else await api.criarMaterial(payload);
      setAberto(false);
      await carregar();
    } catch (err) {
      setErro(err.message);
    } finally {
      setSalvando(false);
    }
  };

  const remover = async (m) => {
    if (!window.confirm(`Excluir "${m.nome}"?`)) return;
    try { await api.removerMaterial(m.id); await carregar(); }
    catch (err) { setErro(err.message); }
  };

  const totalFalta = itens.filter(emFalta).length;
  const valorEstoque = itens.reduce((s, m) => s + Number(m.custo_unitario) * Number(m.estoque), 0);

  return (
    <div className="content">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h2 style={{ fontFamily: "var(--display)", fontSize: 28, letterSpacing: "-.02em" }}>Materiais</h2>
          <p className="muted" style={{ marginTop: 4 }}>Sua base de custo — usada na precificação dos trabalhos.</p>
        </div>
        <button className="btn btn-primary" onClick={abrirNovo}><IcPlus style={{ width: 18 }} /> Novo material</button>
      </div>

      <div className="cards">
        <div className="stat"><div className="k">Materiais cadastrados</div><div className="v">{itens.length}</div></div>
        <div className="stat"><div className="k">Valor em estoque</div><div className="v" style={{ fontSize: 26 }}>{brl(valorEstoque)}</div></div>
        <div className="stat" style={totalFalta ? { borderColor: "var(--crimson)" } : null}>
          <div className="k">Precisam de reposição</div>
          <div className="v" style={{ color: totalFalta ? "var(--crimson)" : "inherit", display: "flex", alignItems: "center", gap: 8 }}>
            {totalFalta > 0 && <IcAlert style={{ width: 22 }} />}{totalFalta}
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel__head"><h3>Seus materiais</h3></div>
        {carregando ? (
          <div className="empty">Carregando…</div>
        ) : itens.length === 0 ? (
          <div className="empty">
            Nenhum material ainda.<br />
            <button className="btn btn-ghost" style={{ marginTop: 14 }} onClick={abrirNovo}>
              <IcPlus style={{ width: 18 }} /> Cadastrar o primeiro
            </button>
          </div>
        ) : (
          <table>
            <thead>
              <tr><th>Material</th><th>Categoria</th><th>Custo unit.</th><th>Estoque</th><th></th></tr>
            </thead>
            <tbody>
              {itens.map((m) => (
                <tr key={m.id}>
                  <td>
                    <b>{m.nome}</b>
                    {emFalta(m) && (
                      <span className="tag tag-alerta" style={{ marginLeft: 8 }}>
                        <IcAlert style={{ width: 12, verticalAlign: "-2px", marginRight: 3 }} />repor
                      </span>
                    )}
                  </td>
                  <td className="muted">{m.categoria || "—"}</td>
                  <td className="price">{brl(m.custo_unitario)}</td>
                  <td>
                    {Number(m.estoque)} {m.unidade}
                    {Number(m.estoque_minimo) > 0 && (
                      <span className="muted" style={{ fontSize: 12 }}> &nbsp;(mín. {Number(m.estoque_minimo)})</span>
                    )}
                  </td>
                  <td>
                    <div className="right-actions" style={{ justifyContent: "flex-end" }}>
                      <button className="icon-btn" title="Editar" onClick={() => abrirEdicao(m)}><IcEdit /></button>
                      <button className="icon-btn" title="Excluir" onClick={() => remover(m)}><IcTrash /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {aberto && (
        <div className="overlay" onClick={(e) => e.target === e.currentTarget && setAberto(false)}>
          <form className="modal" onSubmit={salvar}>
            <h3>{editando ? "Editar material" : "Novo material"}</h3>
            {erro && <div className="err">{erro}</div>}
            <div className="field">
              <label>Nome</label>
              <input className="input" value={form.nome} onChange={set("nome")} required placeholder="Ex.: Agulha 1203RL" autoFocus />
            </div>
            <div className="row2">
              <div className="field">
                <label>Categoria</label>
                <select className="input" value={form.categoria} onChange={set("categoria")}>
                  {CATEGORIAS.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Unidade</label>
                <select className="input" value={form.unidade} onChange={set("unidade")}>
                  {UNIDADES.map((u) => <option key={u} value={u}>{u}</option>)}
                </select>
              </div>
            </div>
            <div className="row2">
              <div className="field">
                <label>Custo unitário (R$)</label>
                <input className="input" type="number" step="0.01" min="0" value={form.custo_unitario} onChange={set("custo_unitario")} placeholder="0,00" />
              </div>
              <div className="field">
                <label>Estoque atual</label>
                <input className="input" type="number" step="0.01" min="0" value={form.estoque} onChange={set("estoque")} placeholder="0" />
              </div>
            </div>
            <div className="field">
              <label>Estoque mínimo <span className="muted">(avisa quando atingir — 0 desliga)</span></label>
              <input className="input" type="number" step="0.01" min="0" value={form.estoque_minimo} onChange={set("estoque_minimo")} placeholder="0" />
            </div>
            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button type="button" className="btn btn-ghost btn-block" onClick={() => setAberto(false)}>Cancelar</button>
              <button type="submit" className="btn btn-primary btn-block" disabled={salvando}>
                {salvando ? "Salvando…" : "Salvar"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
