# Motor fiscal ZFM / SEFAZ-AM (Fase 1).
#
# Princípios (ver docs/architecture.md):
#  - Regras parametrizáveis e versionadas por vigência (NUNCA hardcoded).
#  - Suporta coexistência ICMS <-> IBS/CBS (transição LC 214/2025).
#  - Todo parâmetro tributário deve ser validado por contador.
