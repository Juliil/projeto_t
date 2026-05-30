import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { IcBox, IcCalc, IcStore } from "../components/Icons";

export default function Dashboard({ onNav }) {
  const { user } = useAuth();
  const [stats, setStats] = useState({ materiais: 0, orcamentos: 0, anuncios: 0 });

  useEffect(() => {
    (async () => {
      const [m, o, l] = await Promise.all([
        api.materiais().catch(() => []),
        api.orcamentos().catch(() => []),
        api.loja().catch(() => []),
      ]);
      setStats({ materiais: m.length, orcamentos: o.length, anuncios: l.length });
    })();
  }, []);

  const perfil = user?.perfil || {};
  const contexto = [perfil.nome_estudio, perfil.cidade].filter(Boolean).join(" · ");

  return (
    <div className="content">
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ fontFamily: "var(--display)", fontSize: 30, letterSpacing: "-.02em" }}>
          Olá, {user?.nome?.split(" ")[0]} 👋
        </h2>
        <p className="muted" style={{ marginTop: 4 }}>
          {contexto || "Bem-vindo ao seu painel."} Aqui você organiza materiais, precifica trabalhos e negocia na loja.
        </p>
      </div>

      <div className="cards">
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("materiais")}>
          <div className="k">Materiais cadastrados</div>
          <div className="v">{stats.materiais}</div>
        </button>
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("precificacao")}>
          <div className="k">Orçamentos salvos</div>
          <div className="v">{stats.orcamentos}</div>
        </button>
        <button className="stat" style={{ textAlign: "left", cursor: "pointer" }} onClick={() => onNav("loja")}>
          <div className="k">Anúncios na loja</div>
          <div className="v">{stats.anuncios}</div>
        </button>
      </div>

      <div className="panel">
        <div className="panel__head"><h3>Comece por aqui</h3></div>
        <div className="panel__body" style={{ display: "grid", gap: 12 }}>
          <button className="opt" onClick={() => onNav("materiais")}>
            <b style={{ display: "flex", alignItems: "center", gap: 10 }}><IcBox style={{ width: 18 }} /> Cadastrar materiais</b>
            <span className="muted" style={{ display: "block", marginTop: 4 }}>A base de custo para precificar cada trabalho.</span>
          </button>
          <button className="opt" onClick={() => onNav("precificacao")}>
            <b style={{ display: "flex", alignItems: "center", gap: 10 }}><IcCalc style={{ width: 18 }} /> Precificar um trabalho</b>
            <span className="muted" style={{ display: "block", marginTop: 4 }}>Materiais + horas + margem = preço sugerido.</span>
          </button>
          <button className="opt" onClick={() => onNav("loja")}>
            <b style={{ display: "flex", alignItems: "center", gap: 10 }}><IcStore style={{ width: 18 }} /> Vender na loja</b>
            <span className="muted" style={{ display: "block", marginTop: 4 }}>Preço fixo ou leilão, compartilhado por todos.</span>
          </button>
        </div>
      </div>
    </div>
  );
}
