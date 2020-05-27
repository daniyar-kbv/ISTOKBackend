def make_messages(messages=None):
    return {
        'messages': messages
    }


def make_messages_args(args):
    messages = []
    for arg in args:
        messages.append(f'{arg[0]}: {arg[1]}')
    return {
        'massages': messages
    }


def make_errors(serializer):
    messages = []
    for key, value in serializer.errors.items():
        if isinstance(value, dict):
            for key2, value2 in value.items():
                messages.append(f'{key2.capitalize()}: {value2[0]}')
        else:
            messages.append(f'{key.capitalize()}: {value[0]}')
    return make_messages(messages)


def missing_field(field):
    return f'Укажите: {field}'
