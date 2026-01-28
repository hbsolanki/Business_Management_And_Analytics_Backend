from django.template.loader import render_to_string
from weasyprint import HTML

def generate_invoice_pdf(invoice):
    tax_amount = float(invoice.total_amount) - float(invoice.sub_total)

    html_string = render_to_string(
        "invoice.html",
        {
            "invoice": invoice,
            "tax_amount": tax_amount,
        },
    )
    pdf = HTML(string=html_string).write_pdf()
    return pdf  # bytes

