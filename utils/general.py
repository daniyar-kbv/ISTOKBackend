import constants

def is_digits(str):
    for char in str:
        if not ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].__contains__(char):
            return False
    return True


def format_time_period(amount, unit):
    amount_str = f'{amount}'
    last_char = amount_str[-1]
    if amount >= 2:
        last_two_chars = amount_str[-2:]
        if last_two_chars in ['11', '12', '13', '14', '15', '16', '17', '18', '19']:
            if unit == constants.TIME_DAY:
                return 'дней'
            elif unit == constants.TIME_MONTH:
                return 'месяцев'
            elif unit == constants.TIME_YEAR:
                return 'лет'
    if last_char == '1':
        if unit == constants.TIME_DAY:
            return 'день'
        elif unit == constants.TIME_MONTH:
            return 'месяц'
        elif unit == constants.TIME_YEAR:
            return 'год'
    elif last_char in ['0', '5', '6', '7', '8', '9']:
        if unit == constants.TIME_DAY:
            return 'дней'
        elif unit == constants.TIME_MONTH:
            return 'месяцев'
        elif unit == constants.TIME_YEAR:
            return 'лет'
    else:
        if unit == constants.TIME_DAY:
            return 'дня'
        elif unit == constants.TIME_MONTH:
            return 'месяца'
        elif unit == constants.TIME_YEAR:
            return 'года'
    return ''


def get_status_name(user, obj):
    if obj.status == constants.APPLICATION_CONFIRMED:
        return 'В процессе'
    if obj.status == constants.APPLICATION_FINISHED_CONFIRMED:
        return 'Завершена'
    if obj.status == constants.APPLICATION_DECLINED_MERCHANT or obj.status == constants.APPLICATION_DECLINED_CLIENT:
        return 'Отклонена'
    if user.role == constants.ROLE_CLIENT:
        if obj.status == constants.APPLICATION_CREATED or obj.status == constants.APPLICATION_FINISHED:
            return 'Ожидает ответа'
    elif user.role == constants.ROLE_MERCHANT:
        if obj.status == constants.APPLICATION_CREATED:
            return 'Новая'
        elif obj.status == constants.APPLICATION_FINISHED:
            return 'Ожидает завершения'
