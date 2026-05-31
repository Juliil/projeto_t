import { useState } from "react";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Onboarding from "./pages/Onboarding";
import Dashboard from "./pages/Dashboard";
import Materiais from "./pages/Materiais";
import Precificacao from "./pages/Precificacao";
import Agenda from "./pages/Agenda";
import Contabilidade from "./pages/Contabilidade";
import Sidebar from "./components/Sidebar";
import Loading from "./components/Loading";
import { IcBell } from "./components/Icons";

const TITULOS = {
  home: "Início",
  materiais: "Materiais",
  precificacao: "Precificação",
  agenda: "Agenda",
  contabilidade: "Contabilidade",
  loja: "Loja",
};

function EmBreve({ parte }) {
  return (
    <div className="content">
      <div className="empty" style={{ padding: "80px 20px" }}>
        <div style={{ fontFamily: "var(--display)", fontSize: 26, color: "var(--ink)" }}>Em breve</div>
        <p style={{ marginTop: 8 }}>Esta seção chega na <b>Parte {parte}</b> do projeto.</p>
      </div>
    </div>
  );
}

function Shell() {
  const { user } = useAuth();
  const [active, setActive] = useState("home");
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("sidebar:collapsed") === "1");
  const inicial = (user?.nome || "?").trim().charAt(0).toUpperCase();

  const toggleSidebar = () =>
    setCollapsed((c) => {
      const next = !c;
      localStorage.setItem("sidebar:collapsed", next ? "1" : "0");
      return next;
    });

  const render = () => {
    switch (active) {
      case "home": return <Dashboard onNav={setActive} />;
      case "materiais": return <Materiais />;
      case "precificacao": return <Precificacao />;
      case "agenda": return <Agenda onNav={setActive} />;
      case "contabilidade": return <Contabilidade />;
      case "loja": return <EmBreve parte={4} />;
      default: return null;
    }
  };

  return (
    <div className={`shell ${collapsed ? "collapsed" : ""}`}>
      <Sidebar active={active} onNav={setActive} collapsed={collapsed} onToggle={toggleSidebar} />
      <div className="main">
        <div className="topbar">
          <h1>{TITULOS[active]}</h1>
          <div className="right">
            <button className="icon-btn"><IcBell /></button>
            <div className="avatar">{inicial}</div>
          </div>
        </div>
        {render()}
      </div>
    </div>
  );
}

export default function App() {
  const { user, ready, empresa } = useAuth();
  const [transicao, setTransicao] = useState(false);

  if (!ready) return null;

  let view;
  if (!user) view = <Login setLoading={setTransicao} />;
  else if (user.status === "pre_registro") view = <Onboarding setLoading={setTransicao} />;
  else view = <Shell />;

  return (
    <>
      {view}
      {transicao && <Loading empresa={empresa} onDone={() => setTransicao(false)} />}
    </>
  );
}
