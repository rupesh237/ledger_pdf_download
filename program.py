def general_ledger_function():
    ledgers_list = Receipts.objects.all().values("date").distinct().order_by("-date").annotate(
        sum_sharecapital_amount=Sum('sharecapital_amount'),
        sum_entrancefee_amount=Sum('entrancefee_amount'),
        sum_membershipfee_amount=Sum('membershipfee_amount'),
        sum_bookfee_amount=Sum('bookfee_amount'),
        sum_loanprocessingfee_amount=Sum('loanprocessingfee_amount'),
        sum_savingsdeposit_thrift_amount=Sum('savingsdeposit_thrift_amount'),
        sum_fixeddeposit_amount=Sum('fixeddeposit_amount'),
        sum_recurringdeposit_amount=Sum('recurringdeposit_amount'),
        sum_loanprinciple_amount=Sum('loanprinciple_amount'),
        sum_loaninterest_amount=Sum('loaninterest_amount'),
        sum_insurance_amount=Sum('insurance_amount'),
        total_sum=Sum('sharecapital_amount') +
                  Sum('entrancefee_amount') +
                  Sum('membershipfee_amount') +
                  Sum('bookfee_amount') +
                  Sum('loanprocessingfee_amount') +
                  Sum('savingsdeposit_thrift_amount') +
                  Sum('fixeddeposit_amount') +
                  Sum('recurringdeposit_amount') +
                  Sum('loanprinciple_amount') +
                  Sum('loaninterest_amount') +
                  Sum('insurance_amount')
    )
    return ledgers_list

def general_ledger(request):
    ledgers_list = general_ledger_function()
    return render(request, "generalledger.html", {'ledgers_list': ledgers_list})

def general_ledger_pdf_download(request):
    general_ledger_list = general_ledger_function()
    try:
        html_template = get_template("pdfgeneral_ledger.html")
        context = {
            'pagesize': 'A4',
            "list": general_ledger_list,
            "mediaroot": settings.MEDIA_ROOT
        }
        rendered_html = html_template.render(context).encode(encoding="UTF-8")
        css_files = [
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'mf.css')),
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf_stylesheet.css'))
        ]
        pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=css_files)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="General_Ledger.pdf"'
        return response
    except Exception as err:
        return HttpResponse(f'Error generating PDF: {err}', status=500)


# Day_book pdf dwoload
def day_book_function(request, date):
    selected_date = date
    query_set = Receipts.objects.filter(date=selected_date)
    grouped_receipts_list = query_set.values_list('group_id', flat=True).distinct()
    receipts_list = []

    results_lists = {
        'thrift_deposit_sum_list': [],
        'loanprinciple_amount_sum_list': [],
        'loaninterest_amount_sum_list': [],
        'entrancefee_amount_sum_list': [],
        'membershipfee_amount_sum_list': [],
        'bookfee_amount_sum_list': [],
        'loanprocessingfee_amount_sum_list': [],
        'insurance_amount_sum_list': [],
        'fixed_deposit_sum_list': [],
        'recurring_deposit_sum_list': [],
        'share_capital_amount_sum_list': []
    }

    for group_id in grouped_receipts_list:
        if group_id:
            receipts_list = Receipts.objects.filter(group=group_id, date=selected_date)
            results_lists = get_results_list(
                receipts_list, group_id, 
                *[results_lists[key] for key in results_lists.keys()]
            )
        else:
            receipts_list = Receipts.objects.filter(group=None, date=selected_date)
            for receipt in receipts_list:
                results_lists = get_results_list(
                    [receipt], None,
                    *[results_lists[key] for key in results_lists.keys()]
                )

    total_dict = {f"total_{key}": sum([i.get(f"{key}_sum", 0) for i in results_lists[key]]) for key in results_lists}
    total = sum(total_dict.values())

    payments_list = Payments.objects.filter(date=selected_date)
    payment_types = [
        "TravellingAllowance", "Loans", "Paymentofsalary", "PrintingCharges", 
        "StationaryCharges", "OtherCharges", "SavingsWithdrawal", 
        "FixedWithdrawal", "RecurringWithdrawal"
    ]
    dict_payments = {payment_type: list(payments_list.filter(payment_type=payment_type)) for payment_type in payment_types}
    dict_payments_totals = {key: sum([p.total_amount for p in value]) for key, value in dict_payments.items()}

    total_payments = sum(dict_payments_totals.values())

    return {
        'receipts_list': list(receipts_list),
        'total_payments': total_payments,
        'travellingallowance_list': dict_payments.get("TravellingAllowance", []),
        'loans_list': dict_payments.get("Loans", []),
        'paymentofsalary_list': dict_payments.get("Paymentofsalary", []),
        'printingcharges_list': dict_payments.get("PrintingCharges", []),
        'stationarycharges_list': dict_payments.get("StationaryCharges", []),
        'othercharges_list': dict_payments.get("OtherCharges", []),
        'savingswithdrawal_list': dict_payments.get("SavingsWithdrawal", []),
        'fixedwithdrawal_list': dict_payments.get("FixedWithdrawal", []),
        'recurringwithdrawal_list': dict_payments.get("RecurringWithdrawal", []),
        'total': total,
        'dict_payments': dict_payments_totals,
        'total_dict': total_dict,
        'selected_date': selected_date,
        'grouped_receipts_list': list(grouped_receipts_list),
        'thrift_deposit_sum_list': results_lists['thrift_deposit_sum_list'],
        'loanprinciple_amount_sum_list': results_lists['loanprinciple_amount_sum_list'],
        'loaninterest_amount_sum_list': results_lists['loaninterest_amount_sum_list'],
        'entrancefee_amount_sum_list': results_lists['entrancefee_amount_sum_list'],
        'membershipfee_amount_sum_list': results_lists['membershipfee_amount_sum_list'],
        'bookfee_amount_sum_list': results_lists['bookfee_amount_sum_list'],
        'loanprocessingfee_amount_sum_list': results_lists['loanprocessingfee_amount_sum_list'],
        'insurance_amount_sum_list': results_lists['insurance_amount_sum_list'],
        'fixed_deposit_sum_list': results_lists['fixed_deposit_sum_list'],
        'recurring_deposit_sum_list': results_lists['recurring_deposit_sum_list'],
        'share_capital_amount_sum_list': results_lists['share_capital_amount_sum_list']
    }

def day_book_view(request):
    if request.method == 'POST':
        date_str = request.POST.get("date")
        try:
            date = datetime.strptime(date_str, "%m/%d/%Y").date()
        except (ValueError, TypeError):
            return render(request, "day_book.html", {"error_message": "Invalid date format. Use MM/DD/YYYY."})
    else:
        date_str = request.GET.get("date")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
        except (ValueError, TypeError):
            return render(request, "day_book.html", {"error_message": "Invalid date format. Use YYYY-MM-DD."})

    context = day_book_function(request, date)
    context['date_formated'] = date.strftime("%m/%d/%Y")
    return render(request, "day_book.html", context)



def daybook_pdf_download(request, date):
    # Ensure 'date' is correctly retrieved
    date = request.GET.get("date") or date

    receipts_data = day_book_function(request, date)
    
    try:
        context = {
            'pagesize': 'A4',
            "mediaroot": settings.MEDIA_ROOT,
            "receipts_list": receipts_data['receipts_list'],
            "total_payments": receipts_data['total_payments'],
            "loans_list": receipts_data['loans_list'],
            "selected_date": receipts_data['selected_date'],
            "fixedwithdrawal_list": receipts_data['fixedwithdrawal_list'],
            "total": receipts_data['total'],
            "dict_payments": receipts_data['dict_payments'],
            "dict": receipts_data['total_dict'],
            "travellingallowance_list": receipts_data['travellingallowance_list'],
            "paymentofsalary_list": receipts_data['paymentofsalary_list'],
            "printingcharges_list": receipts_data['printingcharges_list'],
            "stationarycharges_list": receipts_data['stationarycharges_list'],
            "othercharges_list": receipts_data['othercharges_list'],
            "savingswithdrawal_list": receipts_data['savingswithdrawal_list'],
            "recurringwithdrawal_list": receipts_data['recurringwithdrawal_list'],
            "grouped_receipts_list": receipts_data['grouped_receipts_list'],
            "thrift_deposit_sum_list": receipts_data['thrift_deposit_sum_list'],
            "loanprinciple_amount_sum_list": receipts_data['loanprinciple_amount_sum_list'],
            "loaninterest_amount_sum_list": receipts_data['loaninterest_amount_sum_list'],
            "entrancefee_amount_sum_list": receipts_data['entrancefee_amount_sum_list'],
            "membershipfee_amount_sum_list": receipts_data['membershipfee_amount_sum_list'],
            "bookfee_amount_sum_list": receipts_data['bookfee_amount_sum_list'],
            "insurance_amount_sum_list": receipts_data['insurance_amount_sum_list'],
            "share_capital_amount_sum_list": receipts_data['share_capital_amount_sum_list'],
            "recurring_deposit_sum_list": receipts_data['recurring_deposit_sum_list'],
            "fixed_deposit_sum_list": receipts_data['fixed_deposit_sum_list'],
            "loanprocessingfee_amount_sum_list": receipts_data['loanprocessingfee_amount_sum_list']
        }

        html_template = get_template("pdf_daybook.html")
        rendered_html = html_template.render(context).encode(encoding="UTF-8")
        css_files = [
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'mf.css')),
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf_stylesheet.css'))
        ]

        pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=css_files)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        return response

    except Exception as err:
        return HttpResponse(f'Error generating PDF: {err}', status=500)

