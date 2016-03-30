import math


class Pagination:
    """Store pagination information

    The page number is 1 based.
    This class is lazy. The updates of properties of this class will not affect
    the pagination information. Must call the refresh() method to update the 
    pagination information.
    """
    DEFAULT_PER_ROWS = 12
    DEFAULT_PAGES_RANGE = 7

    def __init__(self, total_rows, per_rows=DEFAULT_PER_ROWS, current_page=1, pages_range=DEFAULT_PAGES_RANGE):
        self._total_rows = None
        self._per_rows = None
        self._current_page = None
        self._pages_range = None
        self._pagination_from_page = None
        self._pagination_to_page = None
        self._total_page = None
        self.set_total_rows(total_rows)
        self.set_per_rows(per_rows)
        self.set_current_page(current_page)
        self.set_pages_range(pages_range)
        self.refresh()

    def set_total_rows(self, total_rows):
        if total_rows < 0:
            raise ValueError("total rows must greater than zero")
        self._total_rows = total_rows

    def get_total_rows(self):
        return self._total_rows

    def set_per_rows(self, per_rows):
        if per_rows < 0:
            raise ValueError("per rows must greater than zero")
        self._per_rows = per_rows

    def get_per_rows(self):
        return self._per_rows

    def set_current_page(self, current_page):
        if current_page < 1:
            raise ValueError("current page must greater than 1")
        self._current_page = current_page

    def get_current_page(self):
        return self._current_page

    def get_from_rows(self):
        return (self._current_page - 1) * self._per_rows

    def get_to_rows(self):
        return self.get_from_rows() + self._per_rows - 1

    def set_pages_range(self, pages_range):
        if pages_range < 1:
            raise ValueError("pages range must greater than 1")
        self._pages_range = pages_range

    def get_pages_range(self):
        return self._pages_range

    def get_pagination_from_page(self):
        return self._pagination_from_page

    def get_pagination_to_page(self):
        return self._pagination_to_page

    def get_total_pages(self):
        return self._total_pages

    def refresh(self):
        # update total pages
        self._total_pages = math.ceil(self._total_rows / self._per_rows) # +/+, always positive
        # sanitize current page
        self._current_page = self._total_pages if self._total_pages < self._current_page else self._current_page
        # update pagination from page
        left_span_coda = math.floor(self._pages_range / 2)
        right_span_coda = self._pages_range - left_span_coda
        self._pagination_from_page = max(1, self._current_page - left_span_coda)
        # add the left left span coda to right span coda
        right_span_coda += left_span_coda - (self._current_page - self._pagination_from_page)
        # update pagination to page
        self._pagination_to_page = min(self._total_pages, self._current_page + right_span_coda)
        right_left_span_coda = right_span_coda - (self._pagination_to_page - self._current_page)
        # update pagination from page again if right span coda is left
        if right_left_span_coda != 0:
            left_span_coda += right_left_span_coda
            self._pagination_from_page = max(1, self._current_page - left_span_coda)

       
if __name__ == '__main__':
    p = Pagination(178, current_page=7) 
