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
  agendarOrcamento: (id, data) => req(`/api/precificacao/orcamentos/${id}/agenda`, { method: "PATCH", body: { data } }),
  orcamentos: () => req("/api/precificacao/orcamentos"),

  ncms: () => req("/api/fiscal/ncm"),
  simularEntrada: (d) => req("/api/fiscal/simular-entrada", { method: "POST", body: d }),

  saudeContabil: () => req("/api/contabilidade/saude"),
  receitas: () => req("/api/contabilidade/receitas"),
  criarReceita: (d) => req("/api/contabilidade/receitas", { method: "POST", body: d }),
  removerReceita: (id) => req(`/api/contabilidade/receitas/${id}`, { method: "DELETE" }),
  sinalizarContador: (d = {}) => req("/api/contabilidade/sinalizar", { method: "POST", body: d }),
  // estúdio ↔ contador
  interesses: () => req("/api/contabilidade/interesses"),
  aceitarInteresse: (id, escopo) => req(`/api/contabilidade/interesses/${id}/aceitar`, { method: "POST", body: { escopo } }),
  vinculoContabil: () => req("/api/contabilidade/vinculo"),
  encerrarVinculo: () => req("/api/contabilidade/vinculo/encerrar", { method: "POST" }),
  mensagensVinculo: () => req("/api/contabilidade/vinculo/mensagens"),
  enviarMensagemEstudio: (corpo) => req("/api/contabilidade/vinculo/mensagens", { method: "POST", body: { corpo } }),
  // portal do contador
  contadorMe: () => req("/api/contador/me"),
  contadorLeads: () => req("/api/contador/leads"),
  manifestarInteresse: (sid, mensagem) => req(`/api/contador/leads/${sid}/interesse`, { method: "POST", body: { mensagem } }),
  contadorVinculos: () => req("/api/contador/vinculos"),
  contadorDados: (vid) => req(`/api/contador/vinculos/${vid}/dados`),
  contadorMensagens: (vid) => req(`/api/contador/vinculos/${vid}/mensagens`),
  enviarMensagemContador: (vid, corpo) => req(`/api/contador/vinculos/${vid}/mensagens`, { method: "POST", body: { corpo } }),

  loja: () => req("/api/loja"),
  criarAnuncio: (d) => req("/api/loja", { method: "POST", body: d }),
  ofertar: (id, valor) => req(`/api/loja/${id}/oferta`, { method: "POST", body: { valor } }),
  comprar: (id) => req(`/api/loja/${id}/comprar`, { method: "POST" }),
};

export const brl = (v) =>
  Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
