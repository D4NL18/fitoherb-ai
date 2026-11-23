"""
Exemplo Completo: Sistema Multiagente de Análise Financeira com LangGraph (Padrão ReAct)
Arquitetura: StateGraph + MemorySaver + @tool + Ciclo Thought -> Action -> Observation
Agentes: Pesquisador -> Analista -> Gerador de Relatório Executivo

Dependências:
    pip install langgraph langchain-core langchain-openai yfinance python-dotenv
"""

from datetime import datetime
from typing import Any, Dict, List, TypedDict

import yfinance as yf
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

load_dotenv()


class EstadoAnalise(TypedDict):
    """Estado compartilhado entre todos os agentes do grafo."""

    ticker: str
    dados_mercado: Dict[str, Any]
    analise_tecnica: str
    insights_analista: str
    relatorio_final: str
    etapa_atual: str
    historico_decisoes: List[str]
    erro: str


def criar_estado_inicial(ticker: str) -> EstadoAnalise:
    return EstadoAnalise(
        ticker=ticker,
        dados_mercado={},
        analise_tecnica="",
        insights_analista="",
        relatorio_final="",
        etapa_atual="inicio",
        historico_decisoes=[],
        erro="",
    )


@tool
def obter_dados_acao(ticker: str) -> Dict[str, Any]:
    """Coleta dados históricos (30 dias) e métricas fundamentais da ação via yfinance."""
    try:
        acao = yf.Ticker(ticker)
        hist = acao.history(period="30d")
        info = acao.info

        preco_atual = hist["Close"].iloc[-1]
        preco_30d_atras = hist["Close"].iloc[0]
        variacao_30d = ((preco_atual - preco_30d_atras) / preco_30d_atras) * 100
        volume_medio = hist["Volume"].mean()
        volatilidade = hist["Close"].pct_change().std() * 100

        return {
            "ticker": ticker,
            "preco_atual": round(float(preco_atual), 2),
            "variacao_30d": round(float(variacao_30d), 2),
            "volume_medio": int(volume_medio),
            "volatilidade": round(float(volatilidade), 2),
            "market_cap": info.get("marketCap", "N/A"),
            "setor": info.get("sector", "N/A"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return {"erro": f"Erro ao coletar dados: {exc}"}


@tool
def obter_noticias_mercado(ticker: str) -> List[Dict[str, str]]:
    """Coleta notícias recentes relacionadas ao ticker (substituir por NewsAPI/AlphaVantage em produção)."""
    return [
        {
            "titulo": f"Análise: {ticker} apresenta forte crescimento trimestral",
            "resumo": "Empresa supera expectativas com inovação em IA",
            "sentimento": "positivo",
        },
        {
            "titulo": f"Mercado: Setor de {ticker} enfrenta volatilidade",
            "resumo": "Fatores macroeconômicos afetam performance",
            "sentimento": "neutro",
        },
    ]


def agente_pesquisador(estado: EstadoAnalise) -> Dict[str, Any]:
    """Agente 1 (ReAct): coleta métricas de mercado e notícias recentes."""
    historico = list(estado["historico_decisoes"])
    historico.append(
        f"Pesquisador [Thought]: Coletar preço, volume, volatilidade e notícias de {estado['ticker']}."
    )

    try:
        dados_acao = obter_dados_acao.invoke({"ticker": estado["ticker"]})
        noticias = obter_noticias_mercado.invoke({"ticker": estado["ticker"]})

        if "erro" in dados_acao:
            return {"erro": dados_acao["erro"], "etapa_atual": "erro", "historico_decisoes": historico}

        historico.append(
            f"Pesquisador [Observation]: Preço=${dados_acao['preco_atual']}, "
            f"Var30d={dados_acao['variacao_30d']}%, {len(noticias)} notícias coletadas."
        )
        return {
            "dados_mercado": {
                "acao": dados_acao,
                "noticias": noticias,
                "timestamp_coleta": datetime.now().isoformat(),
            },
            "etapa_atual": "dados_coletados",
            "historico_decisoes": historico,
        }
    except Exception as exc:
        return {"erro": f"Erro no agente pesquisador: {exc}", "etapa_atual": "erro"}


def agente_analista(estado: EstadoAnalise) -> Dict[str, Any]:
    """Agente 2 (ReAct): analisa dimensões técnica, fundamentalista e de sentimento."""
    if not estado["dados_mercado"]:
        return {"erro": "Dados de mercado não disponíveis", "etapa_atual": "erro"}

    historico = list(estado["historico_decisoes"])
    historico.append("Analista [Thought]: Avaliar tendência técnica, fundamentos e sentimento.")

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        dados = estado["dados_mercado"]["acao"]
        noticias = estado["dados_mercado"]["noticias"]
        noticias_fmt = "\n".join(f"- {n['titulo']} (Sentimento: {n['sentimento']})" for n in noticias)

        prompt_analise = (
            f"Analise a ação {estado['ticker']}:\n"
            f"- Preço atual: ${dados['preco_atual']} | Variação 30d: {dados['variacao_30d']}%\n"
            f"- Volatilidade: {dados['volatilidade']}% | Market Cap: {dados['market_cap']} | Setor: {dados['setor']}\n\n"
            f"Notícias:\n{noticias_fmt}\n\n"
            "Forneça: 1) Análise Técnica, 2) Fundamentalista, 3) Sentimento, "
            "4) Recomendação (Compra/Venda/Manter) e 5) Riscos principais."
        )
        resposta = llm.invoke(
            [
                SystemMessage(content="Você é um analista financeiro experiente e objetivo."),
                HumanMessage(content=prompt_analise),
            ]
        )
        historico.append("Analista [Observation]: Insights e recomendação estruturados.")
        return {
            "insights_analista": resposta.content,
            "etapa_atual": "analise_concluida",
            "historico_decisoes": historico,
        }
    except Exception as exc:
        return {"erro": f"Erro no agente analista: {exc}", "etapa_atual": "erro"}


def agente_relatorio(estado: EstadoAnalise) -> Dict[str, Any]:
    """Agente 3 (ReAct): sintetiza os insights em um relatório executivo acionável."""
    if not estado["insights_analista"]:
        return {"erro": "Insights do analista não disponíveis", "etapa_atual": "erro"}

    historico = list(estado["historico_decisoes"])
    historico.append("Relatório [Thought]: Consolidar métricas-chave, recomendação e próximos passos.")

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        dados = estado["dados_mercado"]["acao"]
        prompt_relatorio = (
            f"Crie um RELATÓRIO EXECUTIVO conciso para {estado['ticker']} ({datetime.now():%d/%m/%Y %H:%M}).\n"
            f"Insights do analista:\n{estado['insights_analista']}\n\n"
            f"Métricas: Preço=${dados['preco_atual']}, Var30d={dados['variacao_30d']}%, "
            f"Volatilidade={dados['volatilidade']}%, Setor={dados['setor']}.\n"
            "Estrutura: RECOMENDAÇÃO, RESUMO EXECUTIVO, MÉTRICAS-CHAVE, ANÁLISE RISCO-RETORNO, PRÓXIMOS PASSOS."
        )
        resposta = llm.invoke(
            [
                SystemMessage(content="Você cria relatórios executivos claros e acionáveis."),
                HumanMessage(content=prompt_relatorio),
            ]
        )
        historico.append("Relatório [Observation]: Relatório executivo finalizado.")
        return {
            "relatorio_final": resposta.content,
            "etapa_atual": "concluido",
            "historico_decisoes": historico,
        }
    except Exception as exc:
        return {"erro": f"Erro no agente de relatório: {exc}", "etapa_atual": "erro"}


def criar_sistema_multiagente():
    def rotear(estado: EstadoAnalise) -> str:
        mapa = {
            "inicio": "pesquisador",
            "dados_coletados": "analista",
            "analise_concluida": "relatorio",
        }
        return mapa.get(estado["etapa_atual"], "fim")

    workflow = StateGraph(EstadoAnalise)
    workflow.add_node("pesquisador", agente_pesquisador)
    workflow.add_node("analista", agente_analista)
    workflow.add_node("relatorio", agente_relatorio)

    workflow.add_conditional_edges(START, rotear, {"pesquisador": "pesquisador", "fim": END})
    workflow.add_conditional_edges("pesquisador", rotear, {"analista": "analista", "fim": END})
    workflow.add_conditional_edges("analista", rotear, {"relatorio": "relatorio", "fim": END})
    workflow.add_conditional_edges("relatorio", rotear, {"fim": END})

    return workflow.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    app = criar_sistema_multiagente()
    config = {"configurable": {"thread_id": f"analise_AAPL_{datetime.now().isoformat()}"}}
    resultado = app.invoke(criar_estado_inicial("AAPL"), config=config)
    print(resultado["relatorio_final"])
