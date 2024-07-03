# @csrf_exempt
# def TobuyAPI(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user_role_id = data.get('user_role_id')  
#             invoice_secondary_id = data.get('invoice_secondary_id')
#             wallet_id = data.get('wallet_id')
#             seller_id = data.get('seller_id') #if 2nd buyer
#             fractional_unit_id = data.get('fractional_unit_id') #automatically assign
#             no_of_partition = data.get('no_of_partition')
#             total_amount_invested = data.get('total_amount_invested')
#             purchase_date = timezone.now().date()
#             purchase_time = timezone.now().time()

#             try:
#                 user_role = models.UserRole.objects.get(id=user_role_id)
#             except models.UserRole.DoesNotExist:
#                 return JsonResponse({"message": "User role not found"}, status=404)

#             try:
#                 invoice = models.Invoices.objects.get(id=invoice_secondary_id)
#             except models.Invoices.DoesNotExist:
#                 return JsonResponse({"message": "Invoice not found"}, status=404)

#             try:
#                 wallet = models.OutstandingBalance.objects.get(id=wallet_id)
#             except models.OutstandingBalance.DoesNotExist:
#                 return JsonResponse({"message": "Wallet not found"}, status=404)

#             if not all([no_of_partition, total_amount_invested]):
#                 return JsonResponse({"message": "All fields are required"}, status=400)

#             if wallet.balance < total_amount_invested:
#                 return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)

#             with transaction.atomic():

#                 if seller_id:
#                     try:
#                         seller = models.Sellers.objects.get(id=seller_id, remaining_partitions__gte=no_of_partition)
#                     except models.Sellers.DoesNotExist:
#                         return JsonResponse({"message": "Seller not found or not enough partitions available"}, status=404)
#                 else:

#                 buyer = models.Buyers.objects.create(
#                     user=user_role,
#                     invoice=invoice,
#                     no_of_partitions=no_of_partition,
#                     total_amount_invested=total_amount_invested,
#                     wallet=wallet,
#                     purchase_date=purchase_date,
#                     purchase_time=purchase_time,
#                 )

#                 # if seller_id:
#                 #     try:
#                 #         seller = models.Sellers.objects.get(id=seller_id, remaining_partitions__gte=no_of_partition)
#                 #     except models.Sellers.DoesNotExist:
#                 #         return JsonResponse({"message": "Seller not found or not enough partitions available"}, status=404)

#                     seller_wallet = seller.wallet

#                     if fractional_unit_id:
#                         try:
#                             fractional_unit = models.FractionalUnits.objects.get(unit_id=fractional_unit_id, invoice=invoice, current_owner=seller.buyer.user, sold=True)
#                             fractional_units = [fractional_unit]
#                         except models.FractionalUnits.DoesNotExist:
#                             return JsonResponse({"message": "Requested fractional unit not available"}, status=404)
#                     else:
#                         fractional_units = models.FractionalUnits.objects.filter(invoice=invoice ,  sold=False)[:no_of_partition]
#                         if len(fractional_units) < no_of_partition:
#                             return JsonResponse({"message": "Not enough fractional units available"}, status=400)

#                     for unit in fractional_units:
#                         unit.sold = True
#                         unit.current_owner = user_role
#                         unit.save()

#                         models.SalePurchaseReport.objects.create(
#                             unit=unit,
#                             seller=seller,
#                             buyer=buyer,
#                         )

#                     seller.remaining_partitions -= no_of_partition
#                     if seller.remaining_partitions == 0:
#                         seller.someone_purchased = True
#                     seller.save()

#                     seller_wallet.balance += total_amount_invested
#                     seller_wallet.save()

#                     models.OutstandingBalanceTransaction.objects.create(
#                         wallet=seller_wallet,
#                         transaction_id=uuid.uuid4(),
#                         type='sell',
#                         creditedAmount=total_amount_invested,
#                         debitedAmount=0,
#                         status='response',
#                         source='wallet_to_sell',
#                         purpose='Funds received from selling',
#                         bank_acc=None,
#                         invoice=invoice,
#                         time_date=timezone.now()
#                     )

#                 else:
#                     fractional_units = models.FractionalUnits.objects.filter(invoice=invoice, sold=False)[:no_of_partition]
#                     for unit in fractional_units:
#                         unit.sold = True
#                         unit.current_owner = user_role
#                         unit.save()

#                 if wallet.balance < total_amount_invested:
#                     return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)
#                 else:
#                     wallet.balance -= total_amount_invested
#                     wallet.save()

#                 models.OutstandingBalanceTransaction.objects.create(
#                     wallet=wallet,
#                     transaction_id=uuid.uuid4(),
#                     type='buy',
#                     creditedAmount=0,
#                     debitedAmount=total_amount_invested,
#                     status='response',
#                     source='wallet_to_buy',
#                     purpose='Funds used for purchasing',
#                     bank_acc=None,
#                     invoice=invoice,
#                     time_date=timezone.now()
#                 )

#             return JsonResponse({"message": "Transaction completed successfully", "buyer_id": buyer.id}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)

#     else:
#         return JsonResponse({"message": "Only POST method is allowed"}, status=405)