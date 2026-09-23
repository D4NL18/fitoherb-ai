import io
import base64
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether
)
from app.domains.routing.schemas.routing_dto import ExportPdfRequest

class PdfReportService:
    @staticmethod
    def generate_route_manifest(request: ExportPdfRequest) -> bytes:
        """
        Gera o documento PDF do roteiro de visitas da Fitoherb (Regra P-105).
        Não exibe coordenadas latitude/longitude, exibindo apenas dados legíveis de endereço.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'FitoTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1E3A8A'), # Navy Fitoherb
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'FitoSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4B5563')
        )
        cell_header_style = ParagraphStyle(
            'CellHeader',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )
        cell_text_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1F2937')
        )
        cell_bold_style = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#111827')
        )

        elements = []

        # 1. Cabeçalho Institucional
        elements.append(Paragraph("FITOHERB NORDESTE", title_style))
        elements.append(Paragraph(f"<b>Roteiro Oficial de Visitas Comerciais</b> | Emissão: {request.date}", subtitle_style))
        elements.append(Paragraph(f"<b>Vendedor:</b> {request.seller_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Total de Paradas:</b> {len(request.ordered_stops)}", subtitle_style))
        elements.append(Spacer(1, 10))

        # 2. Resumo de Métricas (KPI Cards)
        hours = int(request.total_time_minutes // 60)
        mins = int(round(request.total_time_minutes % 60))
        time_str = f"{hours}h {mins}min" if hours > 0 else f"{mins} min"

        kpi_data = [
            [
                Paragraph(f"<b>Distância Total:</b><br/>{request.total_distance_km:.1f} km", cell_text_style),
                Paragraph(f"<b>Tempo Estimado de Viagem:</b><br/>{time_str}", cell_text_style),
                Paragraph(f"<b>Paradas Previstas:</b><br/>{len(request.ordered_stops) - 1 if len(request.ordered_stops) > 1 else len(request.ordered_stops)} visitas", cell_text_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # 3. Imagem do Mapa (se fornecida via base64)
        if request.map_image_base64:
            try:
                # Remove header de data URL se presente
                b64_clean = request.map_image_base64
                if "," in b64_clean:
                    b64_clean = b64_clean.split(",", 1)[1]
                img_data = base64.b64decode(b64_clean)
                img_buffer = io.BytesIO(img_data)
                
                # Largura útil da página letter com margens de 36pt = 612 - 72 = 540pt
                map_img = RLImage(img_buffer, width=540, height=220)
                elements.append(Paragraph("<b>Visualização da Rota Otimizada no Mapa:</b>", subtitle_style))
                elements.append(Spacer(1, 4))
                elements.append(map_img)
                elements.append(Spacer(1, 12))
            except Exception as e:
                print(f"[PdfReportService] Erro ao renderizar screenshot do mapa: {e}")

        # 4. Tabela de Sequência de Visitas (Sem expor lat/lon)
        elements.append(Paragraph("<b>Itinerário Sequencial de Visitas:</b>", subtitle_style))
        elements.append(Spacer(1, 4))

        table_rows = [
            [
                Paragraph("<b>#</b>", cell_header_style),
                Paragraph("<b>Local / Cliente</b>", cell_header_style),
                Paragraph("<b>Endereço Completo</b>", cell_header_style),
                Paragraph("<b>Chegada Est.</b>", cell_header_style),
                Paragraph("<b>Status</b>", cell_header_style)
            ]
        ]

        for s in request.ordered_stops:
            step_label = "Partida" if s.action == "DEPARTURE" else ("Retorno" if s.action == "RETURN" else f"#{s.step}")
            
            # Monta endereço amigável
            addr_str = "-"
            if s.address:
                parts = []
                if s.address.street:
                    p = s.address.street
                    if s.address.number:
                        p += f", {s.address.number}"
                    parts.append(p)
                if s.address.neighborhood:
                    parts.append(s.address.neighborhood)
                if s.address.city:
                    parts.append(s.address.city)
                addr_str = " - ".join(parts) if parts else (s.address.full_address or "-")

            status_str = "🔒 Ordem Fixa" if s.is_fixed else "⚡ IA Otimizado"
            if s.traffic_condition and s.traffic_condition != "LIVRE":
                status_str += f"<br/><font color='#b91c1c' size='7'>({s.traffic_condition})</font>"

            if s.estimated_arrival_clock:
                if s.action == "VISIT" and s.estimated_departure_clock:
                    arr_time_str = f"<b>{s.estimated_arrival_clock}</b><br/><font size='7' color='#6b7280'>Até {s.estimated_departure_clock}</font>"
                else:
                    arr_time_str = f"<b>{s.estimated_arrival_clock}</b>"
            else:
                arr_time_str = f"+{s.arrival_time_minutes:.0f} min" if s.arrival_time_minutes > 0 else "0 min"

            table_rows.append([
                Paragraph(step_label, cell_bold_style),
                Paragraph(s.name, cell_bold_style),
                Paragraph(addr_str, cell_text_style),
                Paragraph(arr_time_str, cell_text_style),
                Paragraph(status_str, cell_text_style)
            ])

        route_table = Table(table_rows, colWidths=[50, 130, 220, 75, 65])
        route_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(route_table)
        elements.append(Spacer(1, 14))

        # 5. Rodapé
        footer_text = "Fitoherb Nordeste | Rua Itaeté, 434 - Pitangueiras, Lauro de Freitas - BA | Tel: (71) 3379-7717 | comercial@fitoherb.com.br"
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor('#9CA3AF'), alignment=1)))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

pdf_service = PdfReportService()
