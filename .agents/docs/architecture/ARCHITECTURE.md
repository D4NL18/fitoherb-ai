# Arquitetura do Microserviço: Fitoherb AI

## 1. Visão Geral
Microserviço em Python 3.11/3.12 estruturado com **FastAPI** e **Domain-Driven Design (DDD)** para resolução de problemas de inteligência artificial e otimização logística da Fitoherb.

---

## 2. Estrutura de Diretórios (DDD)
```
fitoherb-ai/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── routing_router.py       # Endpoints REST de otimização de rota e PDF
│   │           └── health_router.py        # Probes de liveness e readiness
│   ├── core/
│   │   └── config.py                       # Configurações centralizadas Pydantic
│   ├── domains/
│   │   └── routing/
│   │       ├── models/
│   │       │   └── point.py                # Entidades e Value Objects (Address, Stop)
│   │       ├── schemas/
│   │       │   └── routing_dto.py          # DTOs de entrada e saída
│   │       ├── services/
│   │       │   ├── routing_chromosome.py   # Cromossomo de permutação com travas
│   │       │   ├── routing_operators.py    # Locked-OX, Locked Mutation, Tournament
│   │       │   ├── routing_fitness.py      # Avaliador de tempo viário e penalidades
│   │       │   ├── routing_solver.py       # Orquestrador do AG (Vendedor Único)
│   │       │   └── pdf_service.py          # Gerador ReportLab de manifestos de visita
│   │       └── infrastructure/
│   │           └── osrm_provider.py        # Conexão OSRM com cache SQLite e fallback Haversine
│   └── main.py                             # Inicialização FastAPI, CORS e Lifespan
├── tests/
│   └── test_routing_solver.py              # Suíte de testes unitários
├── Dockerfile                              # Multi-stage build com usuário não-root
└── requirements.txt
```

---

## 3. Padrões Algorítmicos e Técnicos
- **Locked-OX Crossover:** Garante matematicamente 100% de respeito a paradas manuais fixadas.
- **Cache Viário e Fallback:** Reduz requisições de rede ao OSRM em ~80% e assegura disponibilidade total mesmo sem internet (fallback geodésico calibrado para trânsito urbano de Salvador e Região Metropolitana).
- **Sem Vazamento de Coordenadas:** Apenas logradouros, bairros e cidades são expostos nas saídas visuais e PDFs, em estrito acordo com a LGPD e a Regra P-105.
