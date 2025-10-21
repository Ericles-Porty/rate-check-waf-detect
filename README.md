# rate-check-waf-detect

Script em Python para **testes controlados** de detecção de bloqueio por **rate limit** ou **WAF (Web Application Firewall)**.  
Feito para uso **somente em ambientes sob sua administração ou com permissão explícita do proprietário**.

---

## ⚠️ Aviso Legal

Este código **não deve ser usado** para realizar testes contra domínios públicos, governamentais ou privados sem autorização.  
Executar requisições automatizadas contra sistemas de terceiros sem consentimento pode violar termos de uso e legislação vigente.  

O autor **não se responsabiliza** por uso indevido.  
Use **apenas em servidores de teste, ambientes internos ou com permissão documentada**.

---

## 📘 Objetivo

O script auxilia na identificação de:
- Bloqueios de requisições por **limite de taxa (HTTP 429)**.  
- Bloqueios silenciosos de **WAF**, que retornam HTTP 200 com corpo de erro, como:  
