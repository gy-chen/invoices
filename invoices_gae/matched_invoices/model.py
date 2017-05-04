#coding: utf-8
from .. import invoices
from .. import prizes


class MatchInvoiceModel:
    """Contains logic for matching invoices

    """

    @staticmethod
    def match_invoices():
        # fetch unmatch invoices
        unmatched_invoices, _  = invoices.model.Invoice.list_unmatched()
        # try to match these invoice
        for unmatched_invoice in unmatched_invoices:
            try:
                matched_prize = prizes.model.Prize.match_prize(
                    unmatched_invoice[invoices.model.InvoiceColumn.YEAR],
                    unmatched_invoice[invoices.model.InvoiceColumn.MONTH],
                    unmatched_invoice[invoices.model.InvoiceColumn.NUMBER])
                unmatched_invoice[invoices.model.InvoiceColumn.MATCHED_PRIZE_ID] = matched_prize.key.id if matched_prize else 0
                invoices.model.Invoice.update(unmatched_invoice, unmatched_invoice.key.id)
            except prizes.model.UnpublicPrizeException:
                pass
