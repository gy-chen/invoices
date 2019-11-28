class UserInvoiceModel:

    def add_invoice(self, user_sub, year, month, number, note):
        """Add invoice

        Args:
            user_sub (str)
            year (int)
            month (invoice.common.Month)
            number (str)
            note (str)

        Returns:
            new added invoice
        """
        return NotImplemented

    def update_invoice(self, user_sub, id, year, month, number, note):
        """Update invoice

        Args:
            user_sub (str)
            id (int)
            year (int)
            month (invoice.common.Month)
            number (str)
            note (str)

        Returns:
            updated invoice
        """
        return NotImplemented

    def delete_invoice(self, user_sub, id):
        """Delete invoice

        Args:
            user_sub (str)
            id (int)
        """
        return NotImplemented

    def get_user_invoices(self, user_sub, offset, per_page):
        """Get user invoces

        Args:
            user_sub (str)
            offset (int)
            per_page (int)

        Returns:
            list of UserInvoice
        """
        return NotImplemented

    def get_processed_user_invoices(self, user_sub, offset, per_page):
        """Get processed user invoices

        Args:
            user_sub (str)
            offset (int)
            per_page (int)

        Returns:
            list of UserInvoiceMatch
        """
        return NotImplemented