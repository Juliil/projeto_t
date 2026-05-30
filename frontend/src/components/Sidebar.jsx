import { useAuth } from "../context/AuthContext";
import { IcHome, IcBox, IcCalc, IcStore, IcLogout } from "./Icons";

const ITEMS = [
  { id: "home", label: "Início", Icon: IcHome },
  { id: "materiais", label: "Materiais", Icon: IcBox },
  { id: "precificacao", label: "Precificação", Icon: IcCalc },
  { id: "loja", label: "Loja", Icon: IcStore },
];

export default function Sidebar({ active, onNav }) {
  const { user, empresa, logout } = useAuth();
  const inicial = (user?.nome || "?").trim().charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="dot" /> {empresa}
      </div>
      <nav className="nav">
        {ITEMS.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`nav__item ${active === id ? "active" : ""}`}
            onClick={() => onNav(id)}
          >
            <Icon /> {label}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button className="nav__item" onClick={logout}>
          <IcLogout /> Sair
        </button>
      </nav>
      <div className="sidebar__user">
        <div className="avatar">{inicial}</div>
        <div className="meta">
          <b>{user?.nome}</b>
          <span>{user?.perfil?.nome_estudio || "Tatuador(a)"}</span>
        </div>
      </div>
    </aside>
  );
}
