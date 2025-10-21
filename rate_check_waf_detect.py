#!/usr/bin/env python3
"""
rate_check_waf_detect.py

Teste controlado de comportamento de bloqueio (WAF + rate) para RODA-LOCAL ou alvos autorizados.
Detecta:
 - 429, 403, 401
 - respostas 200 que contenham texto de bloqueio tipo:
   "The requested URL was rejected" ou "Your support ID"

Instalação:
    pip install requests

Uso:
    python rate_check_waf_detect.py --url "https://google.com/" \
        --start 10 --min 0.5 --factor 0.8 --max-requests 200
        

AVISO:
    NÃO USE contra domínios públicos sem permissão. Você é o responsável pelo uso.
"""
import argparse
import time
import random
import sys
import requests
from datetime import datetime

BLOCK_PATTERNS = [
    "The requested URL was rejected",
    "Your support ID",
    "Request blocked",
    "Access Denied",
]

def log(msg):
    print(f"{datetime.now().isoformat()}  {msg}", flush=True)

def looks_like_waf_block(body_text):
    if not body_text:
        return False
    body_lower = body_text.lower()
    for p in BLOCK_PATTERNS:
        if p.lower() in body_lower:
            return True
    return False

def single_request(session, url, timeout):
    try:
        r = session.get(url, timeout=timeout)
        return r.status_code, r.headers, r.text, r.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        return None, None, str(e), None

def parse_args():
    p = argparse.ArgumentParser(description="Teste controlado para detectar bloqueio por WAF/rate (use com permissão).")
    p.add_argument("--url", required=True, help="URL alvo")
    p.add_argument("--start", type=float, default=10.0, help="Intervalo inicial entre requisições (segundos)")
    p.add_argument("--min", type=float, default=0.5, help="Intervalo mínimo (segundos)")
    p.add_argument("--factor", type=float, default=0.8, help="Fator multiplicativo para diminuir o intervalo (0.8 = reduz 20%)")
    p.add_argument("--timeout", type=float, default=10.0, help="Timeout por requisição (segundos)")
    p.add_argument("--max-requests", type=int, default=200, help="Máximo de requisições totais do teste")
    p.add_argument("--jitter", type=float, default=0.1, help="Jitter máximo (segundos) adicionado ao sleep")
    p.add_argument("--dry-run", action="store_true", help="Não execute requisições, apenas mostre o plano")
    p.add_argument("--save-body", type=str, default=None, help="Salvar corpo da última resposta detectada em arquivo")
    return p.parse_args()

def main():
    args = parse_args()

    if args.factor <= 0 or args.factor >= 1:
        log("ERRO: factor deve estar entre 0 e 1 (ex: 0.8).")
        sys.exit(1)
    if args.start <= args.min:
        log("ERRO: start deve ser maior que min.")
        sys.exit(1)

    log(f"Alvo: {args.url}")
    log(f"start={args.start}s min={args.min}s factor={args.factor} timeout={args.timeout}s max_requests={args.max_requests} jitter=±{args.jitter}s")

    if args.dry_run:
        log("DRY RUN. Encerrando.")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "rate-check-waf-detect/1.0 (+authorized-testing)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })

    interval = args.start
    total = 0
    last_body = None

    log("Iniciando teste. Pare imediatamente se detectar degradação do serviço.")

    while total < args.max_requests and interval >= args.min:
        total += 1
        log(f"[#{total}] Enviando requisição. intervalo atual = {interval:.3f}s")
        status, headers, body_or_error, elapsed = single_request(session, args.url, args.timeout)

        if status is None:
            log(f"[#{total}] Erro de requisição: {body_or_error}")
            break
        else:
            last_body = body_or_error
            log(f"[#{total}] Status: {status} | tempo: {elapsed:.3f}s")

            if headers:
                if "Retry-After" in headers:
                    log(f"[#{total}] Encontrado Retry-After: {headers['Retry-After']}")
                rate_keys = [k for k in headers.keys() if k.lower().startswith("x-ratelimit")]
                for k in rate_keys:
                    log(f"[#{total}] Header {k}: {headers[k]}")

            if status == 429:
                log(f"[#{total}] RECEBEU 429 - limite alcançado. Parando teste.")
                break
            if status in (403, 401):
                log(f"[#{total}] Status {status} - possível bloqueio/autenticação necessária. Parando teste.")
                break

            if status == 200 and looks_like_waf_block(body_or_error):
                log(f"[#{total}] BLOQUEIO DETECTADO: corpo contém padrão de WAF.")
                if args.save_body:
                    try:
                        with open(args.save_body, "w", encoding="utf-8") as f:
                            f.write(body_or_error)
                        log(f"[#{total}] Corpo salvo em: {args.save_body}")
                    except Exception as e:
                        log(f"[#{total}] Falha ao salvar corpo: {e}")
                break

        next_interval = interval * args.factor
        if next_interval < args.min:
            next_interval = args.min

        jitter = random.uniform(-args.jitter, args.jitter)
        sleep_for = max(0.0, next_interval + jitter)
        log(f"[#{total}] Dormindo {sleep_for:.3f}s antes da próxima requisição.")
        try:
            time.sleep(sleep_for)
        except KeyboardInterrupt:
            log("Interrompido pelo usuário.")
            break
        interval = next_interval

    log("Teste finalizado.")
    log(f"Total de requisições enviadas: {total}")
    if last_body and args.save_body and not looks_like_waf_block(last_body):
        log("Nota: último corpo salvo pode não conter a página de bloqueio.")

if __name__ == "__main__":
    main()
