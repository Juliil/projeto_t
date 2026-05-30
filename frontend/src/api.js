const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("pt_token");
}
export function setToken(t) {
  localStorage.setItem("pt_token", t);
}
export function clearToken() {
  localStorage.removeItem("pt_token");
}

async function req(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && getToken()) headers.Authorization = `Bearer ${getToken()}`;
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let msg = "Algo deu errado";
    try {
      const j = await res.json();
      if (typeof j.detail === "string") msg = j.detail;
    } catch (_) {}
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  config: () => req("/api/config", { auth: false }),
  preRegistro: (d) => req("/api/auth/pre-registro", { method: "POST", body: d, auth: false }),
  login: (d) => req("/api/auth/login", { method: "POST", body: d, auth: false }),
  me: () => req("/api/auth/me"),
  perguntas: () => req("/api/onboarding/perguntas"),
  concluirOnboarding: (perfil) => req("/api/onboarding/concluir", { method: "POST", body: { perfil } }),

  materiais: () => req("/api/materiais"),
  criarMaterial: (d) => req("/api/materiais", { method: "POST", body: d }),
  atualizarMaterial: (id, d) => req(`/api/materiais/${id}`, { method: "PUT", body: d }),
  removerMaterial: (id) => req(`/api/materiais/${id}`, { method: "DELETE" }),

  calcular: (d) => req("/api/precificacao/calcular", { method: "POST", body: d }),
  salvarOrcamento: (d) => req("/api/precificacao/salvar", { method: "POST", body: d }),
  atualizarOrcamento: (id, d) => req(`/api/precificacao/orcamentos/${id}`, { method: "PUT", body: d }),
  statusOrcamento: (id, status) => req(`/api/precificacao/orcamentos/${id}/status`, { method: "PATCH", body: { status } }),
  orcamentos: () => req("/api/precificacao/orcamentos"),

  loja: () => req("/api/loja"),
  criarAnuncio: (d) => req("/api/loja", { method: "POST", body: d }),
  ofertar: (id, valor) => req(`/api/loja/${id}/oferta`, { method: "POST", body: { valor } }),
  comprar: (id) => req(`/api/loja/${id}/comprar`, { method: "POST" }),
};

export const brl = (v) =>
  Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
