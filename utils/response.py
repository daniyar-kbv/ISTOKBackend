def make_messages(messages=None):
    return {
        'messages': messages
    }


def make_messages_args(args):
    messages = []
    for arg in args:
        messages.append(f'{arg[0]}: {arg[1]}')
    return {
        'messages': messages
    }


def make_messages_new(args):
    messages = {}
    # print(args)
    for arg in args:
        messages[arg[0]] = arg[1]
    return {
        'messages': messages
    }


def make_errors(serializer):
    messages = []
    try:
        for key, value in serializer.errors.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    messages.append(f'{key2.capitalize()}: {value2[0]}')
            else:
                messages.append(f'{key.capitalize()}: {value[0]}')
        return make_messages(messages)
    except:
        return serializer.errors


def make_errors_new(serializer):
    messages = []
    try:
        for key, value in serializer.errors.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    messages.append((key2, value2[0]))
            else:
                messages.append((key, value[0]))
        return make_messages_new(messages)
    except:
        return serializer.errors


def missing_field(field):
    return f'Укажите: {field}'


def get_message(serializer):
    messages = []
    try:
        for key, value in serializer.errors.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    messages.append(f'{key2.capitalize()}: {value2[0]}')
            else:
                messages.append(f'{key.capitalize()}: {value[0]}')
        if len(messages) > 0:
            return messages[0]
        return ''
    except:
        return ''
