import { useAuth } from "../context/AuthContext";
import { IcHome, IcBox, IcCalc, IcStore, IcLogout, IcChevron, IcCalendar, IcReceipt } from "./Icons";

const ITEMS = [
  { id: "home", label: "Início", Icon: IcHome },
  { id: "materiais", label: "Materiais", Icon: IcBox },
  { id: "precificacao", label: "Precificação", Icon: IcCalc },
  { id: "agenda", label: "Agenda", Icon: IcCalendar },
  { id: "contabilidade", label: "Contabilidade", Icon: IcReceipt },
  { id: "loja", label: "Loja", Icon: IcStore },
];

export default function Sidebar({ active, onNav, collapsed, onToggle }) {
  const { user, empresa, logout } = useAuth();
  const inicial = (user?.nome || "?").trim().charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="dot" />
        <span className="label brand-name">{empresa}</span>
        <button
          className="sidebar__toggle"
          onClick={onToggle}
          aria-label={collapsed ? "Expandir menu" : "Recolher menu"}
          title={collapsed ? "Expandir menu" : "Recolher menu"}
        >
          <IcChevron />
        </button>
      </div>
      <nav className="nav">
        {ITEMS.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`nav__item ${active === id ? "active" : ""}`}
            onClick={() => onNav(id)}
            title={collapsed ? label : undefined}
          >
            <Icon /> <span className="label">{label}</span>
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button className="nav__item" onClick={logout} title={collapsed ? "Sair" : undefined}>
          <IcLogout /> <span className="label">Sair</span>
        </button>
      </nav>
      <div className="sidebar__user">
        <div className="avatar">{inicial}</div>
        <div className="meta label">
          <b>{user?.nome}</b>
          <span>{user?.perfil?.nome_estudio || "Tatuador(a)"}</span>
        </div>
      </div>
    </aside>
  );
}
