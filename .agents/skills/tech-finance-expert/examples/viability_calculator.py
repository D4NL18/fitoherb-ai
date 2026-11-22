"""Calculadora de Viabilidade Econômica e Unit Economics para Projetos de TI.

Calcula VPL (NPV), TIR (IRR), Payback Simples, Payback Descontado, TCO e
métricas de Unit Economics (LTV, LTV/CAC, CAC Payback) usando apenas a
biblioteca padrão do Python (sem dependências externas).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ViabilityResult:
    """Resultado consolidado da análise de viabilidade econômica."""

    npv: float
    irr: float | None
    simple_payback: float | None
    discounted_payback: float | None
    is_viable: bool


@dataclass(frozen=True)
class UnitEconomicsResult:
    """Resultado consolidado das métricas de Unit Economics."""

    ltv: float
    ltv_to_cac: float
    cac_payback_months: float
    healthy: bool


def calculate_npv(rate: float, cash_flows: Sequence[float]) -> float:
    """Calcula o Valor Presente Líquido (VPL/NPV).

    Args:
        rate: Taxa Mínima de Atratividade (TMA/WACC) por período (ex.: 0.12 para 12%).
        cash_flows: Sequência de fluxos [FC_0, FC_1, ..., FC_n], onde FC_0 normalmente é negativo (-I_0).
    """
    return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows))


def calculate_irr(
    cash_flows: Sequence[float],
    low: float = -0.99,
    high: float = 10.0,
    tolerance: float = 1e-7,
    max_iterations: int = 200,
) -> float | None:
    """Calcula a Taxa Interna de Retorno (TIR/IRR) via bisseção numérica.

    Retorna None caso não haja mudança de sinal no intervalo [low, high].
    """
    npv_low = calculate_npv(low, cash_flows)
    npv_high = calculate_npv(high, cash_flows)
    if npv_low * npv_high > 0:
        return None

    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        npv_mid = calculate_npv(mid, cash_flows)
        if abs(npv_mid) < tolerance or (high - low) / 2.0 < tolerance:
            return mid
        if npv_low * npv_mid < 0:
            high = mid
            npv_high = npv_mid
        else:
            low = mid
            npv_low = npv_mid
    return (low + high) / 2.0


def calculate_payback(cash_flows: Sequence[float], discount_rate: float = 0.0) -> float | None:
    """Calcula Payback Simples (discount_rate=0) ou Descontado (discount_rate>0).

    Retorna o número fracionário de períodos até recuperar o investimento inicial,
    ou None se o investimento não for recuperado no horizonte informado.
    """
    cumulative = 0.0
    for period, cf in enumerate(cash_flows):
        discounted_cf = cf / ((1.0 + discount_rate) ** period)
        prev_cumulative = cumulative
        cumulative += discounted_cf
        if period > 0 and cumulative >= 0.0:
            if discounted_cf == 0.0:
                return float(period)
            fraction = abs(prev_cumulative) / discounted_cf
            return (period - 1) + fraction
    return None


def analyze_viability(tma: float, cash_flows: Sequence[float]) -> ViabilityResult:
    """Executa a análise completa de viabilidade (VPL, TIR e Paybacks)."""
    npv = calculate_npv(tma, cash_flows)
    irr = calculate_irr(cash_flows)
    simple_pb = calculate_payback(cash_flows, discount_rate=0.0)
    discounted_pb = calculate_payback(cash_flows, discount_rate=tma)
    is_viable = npv > 0.0 and (irr is None or irr > tma)
    return ViabilityResult(
        npv=npv,
        irr=irr,
        simple_payback=simple_pb,
        discounted_payback=discounted_pb,
        is_viable=is_viable,
    )


def calculate_tco(
    acquisition_cost: float,
    annual_cloud_costs: Sequence[float],
    annual_maintenance_costs: Sequence[float],
    migration_and_training_cost: float = 0.0,
    estimated_downtime_loss: float = 0.0,
) -> float:
    """Calcula o Total Cost of Ownership (TCO) no horizonte de anos fornecido."""
    return (
        acquisition_cost
        + sum(annual_cloud_costs)
        + sum(annual_maintenance_costs)
        + migration_and_training_cost
        + estimated_downtime_loss
    )


def calculate_unit_economics(
    arpu_monthly: float,
    gross_margin_pct: float,
    monthly_churn_pct: float,
    cac: float,
) -> UnitEconomicsResult:
    """Calcula LTV, razão LTV/CAC e CAC Payback em meses.

    Args:
        arpu_monthly: Receita média mensal por cliente.
        gross_margin_pct: Margem bruta em decimal (ex.: 0.80 para 80%).
        monthly_churn_pct: Churn mensal em decimal (ex.: 0.02 para 2%).
        cac: Custo de Aquisição de Cliente.
    """
    if monthly_churn_pct <= 0.0:
        raise ValueError("monthly_churn_pct deve ser maior que zero.")
    if cac <= 0.0:
        raise ValueError("cac deve ser maior que zero.")

    monthly_contribution = arpu_monthly * gross_margin_pct
    ltv = monthly_contribution / monthly_churn_pct
    ltv_to_cac = ltv / cac
    cac_payback_months = cac / monthly_contribution
    healthy = ltv_to_cac >= 3.0 and cac_payback_months <= 12.0
    return UnitEconomicsResult(
        ltv=ltv,
        ltv_to_cac=ltv_to_cac,
        cac_payback_months=cac_payback_months,
        healthy=healthy,
    )


if __name__ == "__main__":
    # Exemplo: Projeto de plataforma de IA (Investimento inicial R$ 250k, TMA 15% a.a.)
    tma_anual = 0.15
    fluxos = [-250_000.0, 95_000.0, 130_000.0, 160_000.0, 180_000.0]
    viability = analyze_viability(tma_anual, fluxos)

    tco_3_anos = calculate_tco(
        acquisition_cost=250_000.0,
        annual_cloud_costs=[36_000.0, 42_000.0, 48_000.0],
        annual_maintenance_costs=[45_000.0, 45_000.0, 50_000.0],
        migration_and_training_cost=20_000.0,
    )

    unit = calculate_unit_economics(
        arpu_monthly=1_200.0,
        gross_margin_pct=0.80,
        monthly_churn_pct=0.025,
        cac=9_000.0,
    )

    print("=== Análise de Viabilidade Econômica ===")
    print(f"VPL (NPV):           R$ {viability.npv:,.2f}")
    print(f"TIR (IRR):           {viability.irr * 100:.2f}%" if viability.irr else "TIR: N/A")
    print(f"Payback Simples:     {viability.simple_payback:.2f} anos" if viability.simple_payback else "Payback Simples: N/A")
    print(f"Payback Descontado:  {viability.discounted_payback:.2f} anos" if viability.discounted_payback else "Payback Descontado: N/A")
    print(f"Projeto Viável?      {'SIM' if viability.is_viable else 'NÃO'}")
    print(f"\nTCO (3 anos):        R$ {tco_3_anos:,.2f}")
    print("\n=== Unit Economics ===")
    print(f"LTV:                 R$ {unit.ltv:,.2f}")
    print(f"LTV / CAC:           {unit.ltv_to_cac:.2f}x")
    print(f"CAC Payback:         {unit.cac_payback_months:.1f} meses")
    print(f"Modelo Saudável?     {'SIM' if unit.healthy else 'NÃO'}")
