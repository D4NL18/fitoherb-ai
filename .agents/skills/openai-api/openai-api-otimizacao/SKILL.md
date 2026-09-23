---
name: openai-api-otimizacao
description: Otimização de custos e performance na OpenAI API — rate limiting, exponential backoff, contagem de tokens, caching, monitoramento e escolha inteligente de modelos.
pages: 332-337
---

# OpenAI API — Otimização de Custos e Performance

## Objetivo

Dominar técnicas de otimização para uso da OpenAI API em produção: controlar rate limits com exponential backoff, contar tokens antes de enviar, implementar caching de respostas, monitorar custos em tempo real e escolher o modelo ideal por tarefa.

---

## Conceitos Fundamentais

### 1. Rate Limits da OpenAI

| Limite | Descrição | Código de Erro |
|---|---|---|
| **RPM** (Requests Per Minute) | Número máximo de chamadas por minuto | `429 Too Many Requests` |
| **TPM** (Tokens Per Minute) | Total de tokens processados por minuto | `429 Too Many Requests` |
| **TPD** (Tokens Per Day) | Limite diário de tokens | `429 Too Many Requests` |

Os limites variam por **tier** da conta e por modelo:

| Tier | GPT-4o RPM | GPT-4o-mini RPM |
|---|---|---|
| Free | 3 | 3 |
| Tier 1 | 500 | 500 |
| Tier 2 | 5.000 | 5.000 |
| Tier 5 | 10.000 | 30.000 |

### 2. Exponential Backoff

Estratégia de retry que dobra o tempo de espera a cada tentativa falha, evitando sobrecarregar a API.

```
Tentativa 1: aguardar 1s
Tentativa 2: aguardar 2s
Tentativa 3: aguardar 4s
Tentativa 4: aguardar 8s
Tentativa 5: aguardar 16s
```

```python
import time
import random
from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError

client = OpenAI()

def chamar_api_com_retry(
    messages: list[dict],
    modelo: str = "gpt-4o-mini",
    max_retries: int = 5,
    base_delay: float = 1.0
) -> str:
    """Chamada à API com exponential backoff manual."""
    for tentativa in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=modelo,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content

        except RateLimitError:
            if tentativa == max_retries - 1:
                raise
            delay = base_delay * (2 ** tentativa) + random.uniform(0, 1)
            print(f"[Rate Limit] Aguardando {delay:.1f}s (tentativa {tentativa + 1}/{max_retries})")
            time.sleep(delay)

        except (APITimeoutError, APIConnectionError) as e:
            if tentativa == max_retries - 1:
                raise
            delay = base_delay * (2 ** tentativa)
            print(f"[Conexão] Erro: {e}. Aguardando {delay:.1f}s")
            time.sleep(delay)

    raise RuntimeError("Máximo de tentativas atingido")
```

#### Usando `tenacity` (biblioteca de retry)

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def chamar_api_tenacity(messages: list[dict], modelo: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=modelo,
        messages=messages
    )
    return response.choices[0].message.content
```

---

## Padrões e Boas Práticas

### 3. Contagem de Tokens com `tiktoken`

```python
import tiktoken

def contar_tokens(texto: str, modelo: str = "gpt-4o-mini") -> int:
    """Conta tokens de uma string antes de enviar à API."""
    try:
        enc = tiktoken.encoding_for_model(modelo)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(texto))


def contar_tokens_messages(messages: list[dict], modelo: str = "gpt-4o-mini") -> int:
    """Conta tokens de uma lista de mensagens (overhead incluído)."""
    try:
        enc = tiktoken.encoding_for_model(modelo)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")

    # Overhead por mensagem: 4 tokens (role + separadores)
    num_tokens = 3  # Tokens de início/fim da lista
    for message in messages:
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(enc.encode(str(value)))

    return num_tokens


def validar_contexto(messages: list[dict], modelo: str = "gpt-4o-mini", max_tokens: int = 4096) -> bool:
    """Valida se as mensagens cabem dentro do limite do modelo."""
    tokens = contar_tokens_messages(messages, modelo)
    if tokens > max_tokens:
        print(f"[AVISO] {tokens} tokens excedem o limite de {max_tokens}")
        return False
    print(f"[OK] {tokens}/{max_tokens} tokens ({tokens/max_tokens:.1%} do limite)")
    return True
```

### 4. Caching de Respostas

```python
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta

class CacheRespostas:
    """Cache persistente de respostas da API usando SQLite."""

    def __init__(self, db_path: str = "cache_openai.db", ttl_horas: int = 24):
        self.db_path = db_path
        self.ttl = timedelta(hours=ttl_horas)
        self._inicializar_db()

    def _inicializar_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    chave TEXT PRIMARY KEY,
                    resposta TEXT NOT NULL,
                    criado_em TEXT NOT NULL
                )
            """)

    def _gerar_chave(self, messages: list[dict], modelo: str) -> str:
        conteudo = json.dumps({"messages": messages, "modelo": modelo}, sort_keys=True)
        return hashlib.sha256(conteudo.encode()).hexdigest()

    def get(self, messages: list[dict], modelo: str) -> str | None:
        chave = self._gerar_chave(messages, modelo)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT resposta, criado_em FROM cache WHERE chave = ?",
                (chave,)
            ).fetchone()

        if row:
            criado_em = datetime.fromisoformat(row[1])
            if datetime.now() - criado_em < self.ttl:
                print(f"[CACHE HIT] Chave: {chave[:16]}...")
                return row[0]
            else:
                print(f"[CACHE EXPIRADO] Renovando...")
        return None

    def set(self, messages: list[dict], modelo: str, resposta: str):
        chave = self._gerar_chave(messages, modelo)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
                (chave, resposta, datetime.now().isoformat())
            )


def chamar_api_com_cache(
    messages: list[dict],
    modelo: str = "gpt-4o-mini",
    cache: CacheRespostas | None = None
) -> str:
    """Chamada à API com cache de respostas idênticas."""
    if cache:
        cached = cache.get(messages, modelo)
        if cached:
            return cached

    response = client.chat.completions.create(
        model=modelo,
        messages=messages,
        temperature=0  # Cache só funciona bem com temperature=0
    )
    resposta = response.choices[0].message.content

    if cache:
        cache.set(messages, modelo, resposta)

    return resposta
```

### 5. Monitoramento de Custos

```python
# Preços por 1M tokens (setembro 2024 — verifique sempre em platform.openai.com/pricing)
PRECOS = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}

def calcular_custo(modelo: str, tokens_entrada: int, tokens_saida: int) -> float:
    """Calcula o custo em USD de uma chamada à API."""
    precos = PRECOS.get(modelo, PRECOS["gpt-4o-mini"])
    custo_entrada = (tokens_entrada / 1_000_000) * precos["input"]
    custo_saida = (tokens_saida / 1_000_000) * precos["output"]
    return custo_entrada + custo_saida


class MonitorCustos:
    """Monitora e registra o custo de todas as chamadas à API."""

    def __init__(self):
        self.historico = []
        self.custo_total = 0.0

    def registrar(self, modelo: str, tokens_entrada: int, tokens_saida: int, latencia_ms: float):
        custo = calcular_custo(modelo, tokens_entrada, tokens_saida)
        self.custo_total += custo
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "modelo": modelo,
            "tokens_entrada": tokens_entrada,
            "tokens_saida": tokens_saida,
            "tokens_total": tokens_entrada + tokens_saida,
            "custo_usd": round(custo, 6),
            "latencia_ms": round(latencia_ms, 1)
        }
        self.historico.append(entrada)
        print(f"[CUSTO] ${custo:.6f} | {tokens_entrada}→{tokens_saida} tokens | {latencia_ms:.0f}ms | {modelo}")

    def relatorio(self):
        print(f"\n{'='*50}")
        print(f"Total de chamadas: {len(self.historico)}")
        print(f"Custo total: ${self.custo_total:.4f}")
        if self.historico:
            avg_latencia = sum(h['latencia_ms'] for h in self.historico) / len(self.historico)
            total_tokens = sum(h['tokens_total'] for h in self.historico)
            print(f"Total de tokens: {total_tokens:,}")
            print(f"Latência média: {avg_latencia:.0f}ms")
        print(f"{'='*50}\n")


# Uso integrado
monitor = MonitorCustos()

def chamar_api_monitorado(messages: list[dict], modelo: str = "gpt-4o-mini") -> str:
    import time
    inicio = time.time()

    response = client.chat.completions.create(model=modelo, messages=messages)

    latencia_ms = (time.time() - inicio) * 1000
    monitor.registrar(
        modelo=response.model,
        tokens_entrada=response.usage.prompt_tokens,
        tokens_saida=response.usage.completion_tokens,
        latencia_ms=latencia_ms
    )
    return response.choices[0].message.content
```

---

## Exemplos de Uso

### Seleção de Modelo por Complexidade e Custo

```python
def processar_tarefa_otimizado(tarefa: str, texto: str) -> str:
    """Seleciona automaticamente o modelo mais econômico para a tarefa."""
    # Classificar complexidade
    tokens_estimados = contar_tokens(texto)

    if tokens_estimados < 200 and tarefa in ["classificar", "extrair", "formatar"]:
        modelo = "gpt-3.5-turbo"
    elif tokens_estimados < 1000 and tarefa in ["resumir", "traduzir", "corrigir"]:
        modelo = "gpt-4o-mini"
    else:
        modelo = "gpt-4o"

    messages = [{"role": "user", "content": f"Tarefa: {tarefa}\n\nTexto:\n{texto}"}]
    return chamar_api_monitorado(messages, modelo)
```

---

## Checklist de Qualidade

- [ ] Exponential backoff implementado com jitter aleatório
- [ ] Máximo de 5 tentativas antes de propagar o erro
- [ ] `tiktoken` usado para contar tokens antes de grandes chamadas
- [ ] Contexto validado para não exceder o limite do modelo
- [ ] Cache implementado para respostas determinísticas (`temperature=0`)
- [ ] TTL de cache configurado adequadamente (não cachear por tempo indeterminado)
- [ ] Custo calculado e logado a cada chamada
- [ ] Modelo selecionado com base na complexidade da tarefa
- [ ] Relatório de custos gerado periodicamente
- [ ] `gpt-3.5-turbo` usado para tarefas simples de alto volume
- [ ] `gpt-4o` reservado para tarefas que exigem raciocínio avançado
- [ ] Timeout configurado nas chamadas à API (`timeout=30`)
