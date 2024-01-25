import uuid

import var_dump
from yookassa import Configuration, Payment

Configuration.configure('308535', 'test_UcfnC6Gb-VDueSPfsl3xoDrLQc_pu0cBdCzFer1XI68')

# payment = Payment.create(
#     {
#         "amount": {
#             "value": 1,
#             "currency": "RUB"
#         },
#         "payment_method_data": {
#             "type": "bank_card"
#         },
#         "confirmation": {
#             "type": "redirect",
#             "return_url": "http://127.0.0.1"
#         },
#         "capture": True,
#         "description": f"Оплата тарифного плана . Стоимость",
#         "save_payment_method": True
#     }
# )
#
# var_dump.var_dump(payment)


# #0 object(PaymentResponse) (12)
#     _PaymentResponse__id => str(36) "2d4436d0-000f-5000-8000-1268d84e433d"
#     _PaymentResponse__status => str(7) "pending"
#     _PaymentResponse__amount => object(Amount) (2)
#         _Amount__value => object(Decimal) (1.00)
#         _Amount__currency => str(3) "RUB"
#     _PaymentResponse__description => str(34) "Оплата тарифного плана . Стоимость"
#     _PaymentResponse__recipient => object(Recipient) (2)
#         _Recipient__account_id => str(6) "308535"
#         _Recipient__gateway_id => str(7) "2179030"
#     _PaymentResponse__payment_method => object(PaymentDataBankCard) (3)
#         _PaymentData__type => str(9) "bank_card"
#         _ResponsePaymentData__id => str(36) "2d4436d0-000f-5000-8000-1268d84e433d"
#         _ResponsePaymentData__saved => bool(False)
#     _PaymentResponse__created_at => str(24) "2024-01-25T09:00:00.489Z"
#     _PaymentResponse__confirmation => object(ConfirmationRedirect) (3)
#         _Confirmation__type => str(8) "redirect"
#         _ConfirmationRedirect__return_url => str(16) "http://127.0.0.1"
#         _ConfirmationRedirect__confirmation_url => str(94) "https://yoomoney.ru/checkout/payments/v2/contract?orderId=2d4436d0-000f-5000-8000-1268d84e433d"
#     _PaymentResponse__test => bool(True)
#     _PaymentResponse__paid => bool(False)
#     _PaymentResponse__refundable => bool(False)
#     _PaymentResponse__metadata => dict(0)

# payment = Payment.create({
#     "amount": {
#         "value": "2.00",
#         "currency": "RUB"
#     },
#     "capture": True,
#     "payment_method_id": "2d43ba7c-000f-5000-a000-18e8a1f6734b",
#     "description": "Заказ №105"
# })

payment = Payment.find_one('2d4436d0-000f-5000-8000-1268d84e433d')

var_dump.var_dump(payment)