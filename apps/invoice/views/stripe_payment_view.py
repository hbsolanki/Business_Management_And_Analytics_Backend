import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.invoice.models import Invoice
from datetime import datetime
from apps.base.permission.model_permissions import ModelPermissions
from apps.invoice.tasks import send_invoice_email

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [ModelPermissions]

    @action(detail=False, methods=["post"], url_path="create-intent")
    def create_intent(self, request):
        try:
            invoice_id = request.data.get('invoice_id')
            invoice = Invoice.objects.get(id=invoice_id)
            amount_in_cents = int(invoice.total_amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='inr',
                metadata={
                    "invoice_id": invoice.id,
                    "business_id": invoice.business.id,
                    "customer_id": invoice.customer.id,
                },
                automatic_payment_methods={'enabled': True},
            )

            return Response({'clientSecret': intent['client_secret']}, status=status.HTTP_200_OK)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="webhook", permission_classes=[AllowAny], authentication_classes=[])
    def webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            invoice_id = intent['metadata'].get('invoice_id')

            try:
                invoice = Invoice.objects.get(id=invoice_id)
                invoice.payment_mode = "ONLINE"
                invoice.transaction_id = event['data']['object']['id']
                invoice.payment_date = datetime.now()
                invoice.save(update_fields=['payment_date', 'payment_mode', 'transaction_id'])
                send_invoice_email.delay(to_email=invoice.customer.email, invoice_id=invoice.id)
            except Invoice.DoesNotExist:
                pass

        return HttpResponse(status=200)