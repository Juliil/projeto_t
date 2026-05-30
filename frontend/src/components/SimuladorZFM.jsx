import { useEffect, useState } from "react";
import { api, brl } from "../api";

export default function SimuladorZFM() {
  const [ncms, setNcms] = useState([]);
  const [ncm, setNcm] = useState("");
  const [valor, setValor] = useState(1000);
  const [sim, setSim] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.ncms().then((n) => {
      setNcms(n);
      const elegivel = n.find((x) => x.elegivel_zfm && !x.excluido_beneficio);
      if (elegivel) setNcm(elegivel.codigo);
    }).catch((e) => setErro(e.message));
  }, []);

  const simular = async () => {
    setErro("");
    try { setSim(await api.simularEntrada({ ncm, valor: Number(valor) || 0, origem: "nacional" })); }
    catch (e) { setErro(e.message); setSim(null); }
  };
  useEffect(() => { if (ncm) simular(); /* eslint-disable-next-line */ }, [ncm]);

  const economiaPct = sim && sim.valor_bruto ? (sim.valor_desonerado / sim.valor_bruto) * 100 : 0;

  return (
    <div>
      <p className="muted" style={{ marginBottom: 16 }}>
        Veja quanto a compra de insumos rende de desoneração entrando pela Zona Franca de Manaus —
        a vantagem que a distribuidora do Norte repassa.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr auto", gap: 10, alignItems: "end" }} className="row2">
        <div className="field" style={{ margin: 0 }}>
          <label>Insumo (NCM)</label>
          <select className="input" value={ncm} onChange={(e) => setNcm(e.target.value)}>
            {ncms.map((n) => <option key={n.codigo} value={n.codigo}>{n.descricao} ({n.codigo})</option>)}
          </select>
        </div>
        <div className="field" style={{ margin: 0 }}>
          <label>Valor da compra (R$)</label>
          <input className="input" type="number" min="0" step="50" value={valor} onChange={(e) => setValor(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={simular}>Simular</button>
      </div>

      {erro && <div className="err" style={{ marginTop: 14 }}>{erro}</div>}

      {sim && !erro && (
        <>
          <div style={{ marginTop: 18, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }} className="cards">
            <div className="stat"><div className="k">Custo cheio</div><div className="v" style={{ fontSize: 24 }}>{brl(sim.valor_bruto)}</div></div>
            <div className="stat" style={{ borderColor: sim.valor_desonerado > 0 ? "#2f7a3a" : "var(--line)" }}>
              <div className="k">Você economiza</div>
              <div className="v" style={{ fontSize: 24, color: sim.valor_desonerado > 0 ? "#2f7a3a" : "inherit" }}>
                {brl(sim.valor_desonerado)} <small>({economiaPct.toFixed(0)}%)</small>
              </div>
            </div>
            <div className="stat"><div className="k">Custo via ZFM</div><div className="v" style={{ fontSize: 24, color: "var(--crimson)" }}>{brl(sim.custo_liquido)}</div></div>
          </div>
          <p className="muted" style={{ fontSize: 12.5, marginTop: 12 }}>
            {sim.elegivel ? `Regime ${sim.regime} · ${sim.base_legal}` : sim.observacao} — {sim.disclaimer}
          </p>
        </>
      )}
    </div>
  );
}
