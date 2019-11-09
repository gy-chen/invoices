from invoices.prize_match import is_number_match


def test_number_match():
    assert is_number_match('45698621', '45698621')
    assert not is_number_match('45698621', '45698620')
    assert not is_number_match('45698621', '621')

    assert is_number_match('621', '45698621')
    assert not is_number_match('621', '45698620')