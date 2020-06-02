import math


def paginate_projects(request, queryset, paginator):
    regular = queryset.filter(is_detailed=False)
    detailed = queryset.filter(is_detailed=True)
    sorted = []
    detailed_append_index = 2
    regular_index = 0
    detailed_index = 0
    if detailed.count() > 0:
        if regular.count() / detailed.count() >= 6 / 1:
            for index, item in enumerate(queryset):
                if index == detailed_append_index and detailed_index < detailed.count():
                    sorted.append(detailed[detailed_index])
                    detailed_append_index += (5 if detailed_index % 2 == 0 else 9)
                    detailed_index += 1
                elif regular_index < regular.count():
                    sorted.append(regular[regular_index])
                    regular_index += 1
        else:
            below_count = math.trunc(regular.count() / 6)
            if (detailed.count() - below_count) % 2 == 0:
                detailed_append_index = (detailed.count() - below_count) + 4
            else:
                detailed_append_index = (detailed.count() - below_count) + 8
            for index, item in enumerate(queryset):
                if index < detailed.count() - below_count:
                    sorted.append(detailed[detailed_index])
                    detailed_index += 1
                else:
                    if index == detailed_append_index and detailed_index < detailed.count():
                        sorted.append(detailed[detailed_index])
                        detailed_append_index += (5 if detailed_index % 2 != 0 else 9)
                        detailed_index += 1
                    elif regular_index < regular.count():
                        sorted.append(regular[regular_index])
                        regular_index += 1
    else:
        sorted = queryset
    page = paginator.paginate_queryset(sorted, request)
    return page
