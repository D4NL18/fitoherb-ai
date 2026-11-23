"""Calculadora de EVM (Earned Value Management) e Métricas de Fluxo (Lei de Little).

Calcula SPI, CPI, SV, CV, EAC, ETC, VAC, além de Lead Time médio, Cycle Time
e previsão pela Lei de Little usando apenas a biblioteca padrão do Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EvmReport:
    """Relatório consolidado de Análise de Valor Agregado (EVM)."""

    sv: float
    cv: float
    spi: float
    cpi: float
    eac: float
    etc: float
    vac: float
    schedule_status: str
    cost_status: str


@dataclass(frozen=True)
class FlowMetricsReport:
    """Relatório consolidado de Métricas de Fluxo e Lei de Little."""

    avg_lead_time_days: float
    throughput_per_day: float
    implied_wip_little_law: float


def calculate_evm(bac: float, pv: float, ev: float, ac: float) -> EvmReport:
    """Calcula os principais indicadores de EVM.

    Args:
        bac: Budget at Completion (orçamento total planejado).
        pv: Planned Value (valor planejado até a data).
        ev: Earned Value (valor agregado entregue até a data).
        ac: Actual Cost (custo real incorrido até a data).
    """
    if pv <= 0.0 or ac <= 0.0:
        raise ValueError("PV e AC devem ser maiores que zero.")

    sv = ev - pv
    cv = ev - ac
    spi = ev / pv
    cpi = ev / ac
    eac = bac / cpi
    etc = max(0.0, eac - ac)
    vac = bac - eac

    if spi > 1.02:
        schedule_status = "ADIANTADO"
    elif spi < 0.98:
        schedule_status = "ATRASADO"
    else:
        schedule_status = "NO PRAZO"

    if cpi > 1.02:
        cost_status = "ABAIXO DO ORÇAMENTO"
    elif cpi < 0.98:
        cost_status = "ACIMA DO ORÇAMENTO"
    else:
        cost_status = "NO ORÇAMENTO"

    return EvmReport(
        sv=sv,
        cv=cv,
        spi=spi,
        cpi=cpi,
        eac=eac,
        etc=etc,
        vac=vac,
        schedule_status=schedule_status,
        cost_status=cost_status,
    )


def calculate_flow_metrics(
    lead_times_days: Sequence[float],
    observation_window_days: float,
) -> FlowMetricsReport:
    """Calcula Lead Time médio, Throughput diário e WIP implícito (Lei de Little).

    Lei de Little: WIP = Throughput * Lead Time  <=>  Lead Time = WIP / Throughput.
    """
    if not lead_times_days:
        raise ValueError("lead_times_days não pode ser vazio.")
    if observation_window_days <= 0.0:
        raise ValueError("observation_window_days deve ser maior que zero.")

    avg_lead_time = sum(lead_times_days) / len(lead_times_days)
    throughput = len(lead_times_days) / observation_window_days
    implied_wip = throughput * avg_lead_time
    return FlowMetricsReport(
        avg_lead_time_days=avg_lead_time,
        throughput_per_day=throughput,
        implied_wip_little_law=implied_wip,
    )


def predict_lead_time_little_law(wip: float, throughput_per_day: float) -> float:
    """Estima o Lead Time médio (em dias) pela Lei de Little dado WIP e Throughput."""
    if throughput_per_day <= 0.0:
        raise ValueError("throughput_per_day deve ser maior que zero.")
    return wip / throughput_per_day


if __name__ == "__main__":
    # Exemplo EVM: Projeto híbrido com orçamento de R$ 500k
    evm = calculate_evm(
        bac=500_000.0,
        pv=250_000.0,
        ev=220_000.0,
        ac=240_000.0,
    )

    # Exemplo Fluxo: 12 stories entregues em janela de 14 dias
    lead_times = [3.0, 4.5, 2.0, 5.0, 3.5, 4.0, 6.0, 2.5, 3.0, 4.0, 5.5, 3.0]
    flow = calculate_flow_metrics(lead_times, observation_window_days=14.0)
    reduced_lt = predict_lead_time_little_law(wip=2.0, throughput_per_day=flow.throughput_per_day)

    print("=== Relatório EVM (Earned Value Management) ===")
    print(f"SV (Variação Prazo):  R$ {evm.sv:,.2f}")
    print(f"CV (Variação Custo):  R$ {evm.cv:,.2f}")
    print(f"SPI (Índice Prazo):   {evm.spi:.2f} ({evm.schedule_status})")
    print(f"CPI (Índice Custo):   {evm.cpi:.2f} ({evm.cost_status})")
    print(f"EAC (Custo Final):    R$ {evm.eac:,.2f}")
    print(f"ETC (Falta Gastar):   R$ {evm.etc:,.2f}")
    print(f"VAC (Variação Final): R$ {evm.vac:,.2f}")

    print("\n=== Métricas de Fluxo & Lei de Little ===")
    print(f"Lead Time Médio:      {flow.avg_lead_time_days:.2f} dias")
    print(f"Throughput:           {flow.throughput_per_day:.2f} itens/dia")
    print(f"WIP Implícito:        {flow.implied_wip_little_law:.2f} itens")
    print(f"Lead Time se WIP=2:   {reduced_lt:.2f} dias")
