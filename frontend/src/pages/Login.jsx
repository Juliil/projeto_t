import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import TattooMachine from "../components/TattooMachine";

export default function Login({ setLoading }) {
  const { login, preRegistro, empresa } = useAuth();
  const [tab, setTab] = useState("login"); // login | primeiro
  const [form, setForm] = useState({ nome: "", email: "", senha: "", tipo: "estudio", crc: "", uf_crc: "" });
  const [err, setErr] = useState(null);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const ehContador = form.tipo === "contador";

  const submit = async () => {
    setErr(null);
    setLoading(true);
    try {
      if (tab === "login") {
        await login(form.email, form.senha);
      } else {
        if (!form.nome.trim()) throw new Error("Informe seu nome");
        if (ehContador && !form.crc.trim()) throw new Error("Informe seu CRC");
        await preRegistro({
          nome: form.nome, email: form.email, senha: form.senha, tipo: form.tipo,
          crc: ehContador ? form.crc : null, uf_crc: ehContador ? form.uf_crc : null,
        });
      }
    } catch (e) {
      setLoading(false);
      setErr(e.message);
    }
  };

  const onKey = (e) => e.key === "Enter" && submit();

  return (
    <div className="login">
      <div className="login__left">
        <div className="brand-mark">
          <span className="dot" /> {empresa}
        </div>

        <div className="login__benchmark">
          <div className="bench-tag">Benchmark · Gestão</div>
          <h1 className="bench-title">Projeto T</h1>
          <div className="login__phrase">
            <p>
              Quem não <span>mede</span> a própria arte, <br />
              acaba <span>cobrando</span> pelo medo. <br />
              Aqui, cada risco tem <span>preço</span> certo.
            </p>
            <span className="author">— a régua do tatuador profissional</span>
          </div>
        </div>

        <div className="machine-wrap">
          <TattooMachine />
        </div>
      </div>

      <div className="login__right">
        <div className="login__card">
          <h2>{tab === "login" ? "Bem-vindo de volta" : "Vamos começar"}</h2>
          <p className="sub">
            {tab === "login"
              ? "Entre para acessar seu painel."
              : "Faça seu pré-cadastro em segundos."}
          </p>

          <div className="tabs">
            <button className={tab === "primeiro" ? "active" : ""} onClick={() => { setTab("primeiro"); setErr(null); }}>
              Primeiro acesso
            </button>
            <button className={tab === "login" ? "active" : ""} onClick={() => { setTab("login"); setErr(null); }}>
              Login
            </button>
          </div>

          {err && <div className="err">{err}</div>}

          {tab === "primeiro" && (
            <>
              <div className="field">
                <label>Você é…</label>
                <div className="tabs" style={{ marginBottom: 0 }}>
                  <button type="button" className={!ehContador ? "active" : ""} onClick={() => setForm({ ...form, tipo: "estudio" })}>
                    Tatuador / Estúdio
                  </button>
                  <button type="button" className={ehContador ? "active" : ""} onClick={() => setForm({ ...form, tipo: "contador" })}>
                    Contador
                  </button>
                </div>
              </div>
              <div className="field">
                <label>Nome</label>
                <input className="input" value={form.nome} onChange={set("nome")} onKeyDown={onKey} placeholder="Como podemos te chamar?" />
              </div>
              {ehContador && (
                <div className="row2">
                  <div className="field">
                    <label>CRC</label>
                    <input className="input" value={form.crc} onChange={set("crc")} onKeyDown={onKey} placeholder="Ex.: AM-012345/O" />
                  </div>
                  <div className="field">
                    <label>UF</label>
                    <input className="input" value={form.uf_crc} onChange={set("uf_crc")} onKeyDown={onKey} placeholder="AM" maxLength={2} />
                  </div>
                </div>
              )}
            </>
          )}
          <div className="field">
            <label>E-mail</label>
            <input className="input" type="email" value={form.email} onChange={set("email")} onKeyDown={onKey} placeholder="voce@estudio.com" />
          </div>
          <div className="field">
            <label>Senha</label>
            <input className="input" type="password" value={form.senha} onChange={set("senha")} onKeyDown={onKey} placeholder="••••••••" />
          </div>

          <button className="btn btn-primary btn-block" onClick={submit} style={{ marginTop: 6 }}>
            {tab === "login" ? "Entrar" : "Criar acesso"}
          </button>
        </div>
      </div>
    </div>
  );
}
