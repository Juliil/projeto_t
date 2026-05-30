import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Onboarding({ setLoading }) {
  const { concluirOnboarding, user } = useAuth();
  const [perguntas, setPerguntas] = useState([]);
  const [idx, setIdx] = useState(0);
  const [respostas, setRespostas] = useState({});
  const [valor, setValor] = useState("");
  const [err, setErr] = useState(null);

  useEffect(() => {
    api.perguntas().then((r) => setPerguntas(r.perguntas)).catch(() => {});
  }, []);

  if (!perguntas.length) return <div className="onb" />;

  const q = perguntas[idx];
  const ultima = idx === perguntas.length - 1;
  const progresso = Math.round(((idx) / perguntas.length) * 100);

  const gravar = (resp) => {
    const novas = { ...respostas, [q.id]: resp };
    setRespostas(novas);
    return novas;
  };

  const avancar = (novas) => {
    setValor("");
    setErr(null);
    if (ultima) finalizar(novas);
    else setIdx(idx + 1);
  };

  const escolher = (opt) => avancar(gravar(opt));

  const proximo = () => {
    if (valor === "" || valor === null) {
      setErr("Responda para continuar");
      return;
    }
    const v = q.tipo === "numero" ? Number(valor) : valor;
    avancar(gravar(v));
  };

  const finalizar = async (novas) => {
    setLoading(true);
    try {
      await concluirOnboarding({ ...novas, nome: user?.nome });
    } catch (e) {
      setLoading(false);
      setErr(e.message);
    }
  };

  return (
    <div className="onb">
      <div className="onb__card">
        <div className="onb__progress"><i style={{ width: `${progresso}%` }} /></div>
        <div className="onb__anim" key={idx}>
          <div className="onb__step">Pergunta {idx + 1} de {perguntas.length}</div>
          <h2 className="onb__q">{q.label}</h2>

          {err && <div className="err">{err}</div>}

          {q.tipo === "opcao" ? (
            <div className="opt-grid">
              {q.opcoes.map((opt) => (
                <button key={opt} className="opt" onClick={() => escolher(opt)}>{opt}</button>
              ))}
            </div>
          ) : (
            <input
              className="input"
              autoFocus
              type={q.tipo === "numero" ? "number" : "text"}
              value={valor}
              placeholder={q.placeholder || ""}
              onChange={(e) => setValor(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && proximo()}
            />
          )}
        </div>

        <div className="onb__nav">
          <button className="btn btn-ghost" disabled={idx === 0} onClick={() => { setErr(null); setIdx(idx - 1); }}>
            Voltar
          </button>
          {q.tipo !== "opcao" && (
            <button className="btn btn-primary" onClick={proximo}>
              {ultima ? "Concluir" : "Próximo"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
