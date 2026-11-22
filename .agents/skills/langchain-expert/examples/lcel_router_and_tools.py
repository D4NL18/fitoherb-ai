"""
Exemplos Práticos LangChain:
1. Router Chain Dinâmico com LCEL + Structured Output
2. Tool Customizada com Pydantic + Credenciais via ENV
3. Consulta Segura ao PostgreSQL com Bind Parameters (anti-SQLi)
4. Busca Web em Tempo Real com Tavily
"""

import os
import statistics
from operator import itemgetter
from typing import Literal

import psycopg2
import requests
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()


# ---------------------------------------------------------------------------
# 1. Router Chain Dinâmico com LCEL
# ---------------------------------------------------------------------------
def build_investment_router():
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.0)

    chain_acoes = (
        ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um especialista em investimentos em ações."),
                ("human", "{query}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    chain_renda_fixa = (
        ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um especialista em investimentos de renda fixa."),
                ("human", "{query}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    class RouteQuery(TypedDict):
        destination: Literal["acoes", "renda_fixa"]

    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Roteie a pergunta do usuário para 'acoes' ou 'renda_fixa'."),
            ("human", "{query}"),
        ]
    )
    route_chain = route_prompt | llm.with_structured_output(RouteQuery) | itemgetter("destination")

    return {
        "destination": route_chain,
        "query": itemgetter("query"),
    } | RunnableLambda(lambda x: chain_acoes if x["destination"] == "acoes" else chain_renda_fixa)


# ---------------------------------------------------------------------------
# 2. Tool Customizada com Pydantic (credenciais sempre via ENV)
# ---------------------------------------------------------------------------
class DadosAcaoArgs(BaseModel):
    simbolo: str = Field(description="Ticker da ação (ex: AAPL, MSFT)")


@tool(args_schema=DadosAcaoArgs)
def buscar_media_fechamento_acao(simbolo: str) -> str:
    """Consulta a série diária na API Alpha Vantage e calcula a média de fechamento."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return "ALPHA_VANTAGE_API_KEY não configurada."

    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "TIME_SERIES_DAILY", "symbol": simbolo, "apikey": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    serie = resp.json().get("Time Series (Daily)")
    if not serie:
        return f"Sem dados disponíveis para {simbolo}."

    precos = [float(detalhes["4. close"]) for detalhes in serie.values()]
    return f"A média dos preços de fechamento para {simbolo} é {statistics.mean(precos):.2f}"


# ---------------------------------------------------------------------------
# 3. Consulta Segura ao PostgreSQL (Bind Parameters — zero concatenação SQL)
# ---------------------------------------------------------------------------
def obter_dados_acoes_postgres(termo_busca: str):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
    try:
        with conn.cursor() as cur:
            query = """
                SELECT s.ticker, s.name, sp.date, sp.open, sp.high, sp.low, sp.close, sp.volume
                FROM stocks s
                JOIN stock_prices sp ON s.id = sp.stock_id
                WHERE s.name ILIKE %s OR s.ticker ILIKE %s
                ORDER BY sp.date DESC
                LIMIT 30;
            """
            cur.execute(query, (f"%{termo_busca}%", f"%{termo_busca}%"))
            return cur.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 4. Busca Web com Tavily
# ---------------------------------------------------------------------------
def criar_tool_tavily():
    from langchain_community.tools.tavily_search import TavilySearchResults

    return TavilySearchResults(max_results=3)
