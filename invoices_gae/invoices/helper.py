#coding: utf-8

MESSAGE_SUCCESSFUL = 1

def get_messages_for_add(message):
    try:
        message_i = int(message)
    except TypeError:
        return []
    messages = []
    if message_i & MESSAGE_SUCCESSFUL:
        messages.append('Invoice sucessfully added.')
    return messages

def readable_month(month):
    try:
        month_i = int(month)
    except TypeError:
        return None
    return "{} ~ {}".format(month_i * 2 - 1, month_i * 2)

def readable_matched_prize_id(matched_prize_id):
    if matched_prize_id is None:
        return 'Wait'
    return 'Yes' if matched_prize_id else 'No'
