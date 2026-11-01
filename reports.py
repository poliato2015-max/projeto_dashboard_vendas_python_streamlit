"""Geração do relatório executivo em PDF."""

from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from formatting import formatar_moeda_br, formatar_numero_br


def gera_pdf_report(df_filtrado, total_faturamento, total_quantidade, avg_ticket) -> bytes:
    """Gera o relatório PDF com resumo de KPIs e Top 15 vendas."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        0,
        10,
        "Relatório Executivo de Vendas",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0,
        8,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 35, 190, 25, "F")
    pdf.set_y(40)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(60, 8, "Receita Total", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, "Quantidade", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, "Ticket Médio", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(60, 8, formatar_moeda_br(total_faturamento), align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, formatar_numero_br(total_quantidade), align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, formatar_moeda_br(avg_ticket), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Top 15 Vendas (por receita):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    col_widths = [30, 30, 30, 40, 25, 35]
    headers = ["Data", "Região", "Categoria", "Produto", "Qtd", "Receita"]
    pdf.set_font("Helvetica", "B", 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, 1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    df_top = df_filtrado.sort_values("faturamento", ascending=False).head(15)
    for _, row in df_top.iterrows():
        data = [
            row["date"].strftime("%d/%m/%Y"),
            row["regiao"],
            row["categoria"],
            row["produto"][:20],
            formatar_numero_br(row["quantidade"]),
            formatar_moeda_br(row["faturamento"]),
        ]
        for i, item in enumerate(data):
            safe_txt = str(item).encode("latin-1", "replace").decode("latin-1")
            pdf.cell(col_widths[i], 7, safe_txt, 1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln()

    result = pdf.output()
    return result.encode("latin-1") if isinstance(result, str) else bytes(result)
