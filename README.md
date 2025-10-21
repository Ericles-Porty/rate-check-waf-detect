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

The requested URL was rejected. Please consult with your administrator.
Your support ID is: <id>


---

## 🧩 Instalação

Requer Python 3.8+.

```bash
git clone https://github.com/<seu-usuario>/rate-check-waf-detect.git
cd rate-check-waf-detect
pip install requests
```

---

## ⚙️ Uso

Exemplo básico

python rate_check_waf_detect.py \
  --url "https://seu-servidor/ResumoVisualizar?NrSolicitacao=123" \
  --start 10 \
  --min 0.5 \
  --factor 0.95 \
  --max-requests 200

Parâmetros principais

| Parâmetro      	| Descrição                                                       	| Padrão      	|
|----------------	|-----------------------------------------------------------------	|-------------	|
| --url          	| URL alvo a ser testada (use apenas com permissão)               	| obrigatório 	|
| --start        	| Intervalo inicial entre requisições (segundos)                  	| 10.0        	|
| --min          	| Intervalo mínimo (limite inferior)                              	| 0.5         	|
| --factor       	| Fator multiplicativo para reduzir o intervalo (0.8 = reduz 20%) 	| 0.8         	|
| --timeout      	| Timeout por requisição                                          	| 10.0        	|
| --max-requests 	| Número máximo de requisições antes de parar                     	| 200         	|
| --jitter       	| Variação aleatória para evitar padrão rígido                    	| 0.1         	|
| --save-body    	| Caminho de arquivo para salvar o corpo da resposta bloqueada    	| nenhum      	|
| --dry-run      	| Exibe o plano de execução sem enviar requisições                	| off         	|

---

## 🧠 Lógica de detecção

O script:

Envia requisições periódicas, reduzindo o intervalo entre elas.

Monitora status HTTP e cabeçalhos (Retry-After, X-RateLimit-*).

Detecta respostas HTTP 200 cujo corpo contenha indicadores de bloqueio WAF.

Interrompe o teste automaticamente ao encontrar:

HTTP 429 (rate limit atingido)

HTTP 401/403 (bloqueio/autenticação)

HTML com texto de bloqueio detectado

---

## 🧾 Exemplo de saída

2025-10-20T13:25:10  [#1] Status: 200 | tempo: 0.120s

2025-10-20T13:25:20  [#2] BLOQUEIO DETECTADO: corpo contém padrão de WAF.

2025-10-20T13:25:20  Corpo salvo em: bloqueio.html
