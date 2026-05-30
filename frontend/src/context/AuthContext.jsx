import { createContext, useContext, useEffect, useState } from "react";
import { api, setToken, clearToken } from "../api";

const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [empresa, setEmpresa] = useState("Projeto T");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const cfg = await api.config();
        if (cfg?.empresa_nome) setEmpresa(cfg.empresa_nome);
      } catch (_) {}
      try {
        if (localStorage.getItem("pt_token")) setUser(await api.me());
      } catch (_) {
        clearToken();
      }
      setReady(true);
    })();
  }, []);

  const login = async (email, senha) => {
    const r = await api.login({ email, senha });
    setToken(r.access_token);
    setUser(await api.me());
  };

  const preRegistro = async (nome, email, senha) => {
    const r = await api.preRegistro({ nome, email, senha });
    setToken(r.access_token);
    setUser(await api.me());
  };

  const concluirOnboarding = async (perfil) => {
    setUser(await api.concluirOnboarding(perfil));
  };

  const logout = () => {
    clearToken();
    setUser(null);
  };

  return (
    <AuthCtx.Provider
      value={{ user, empresa, ready, login, preRegistro, concluirOnboarding, logout }}
    >
      {children}
    </AuthCtx.Provider>
  );
}
