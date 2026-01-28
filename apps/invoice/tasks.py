
from celery import shared_task
import base64
from apps.invoice.utils import generate_invoice_pdf
from apps.core.tasks import send_email_task
from apps.invoice.models import Invoice


@shared_task
def send_invoice_email(*, to_email: str, invoice_id: int):

    invoice = Invoice.objects.get(id=invoice_id)
    pdf_bytes = generate_invoice_pdf(invoice)
    encoded_pdf = base64.b64encode(pdf_bytes).decode()

    send_email_task.delay(
        to_email=to_email,
        subject=f"Invoice #{invoice.id}",
        text_content="Please find your invoice attached.",
        attachments=[
            {
                "content": encoded_pdf,
                "name": f"invoice_{invoice.id}_BizVisionary.pdf",
            }
        ],
    )
