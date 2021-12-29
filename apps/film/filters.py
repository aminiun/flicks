from rest_framework import filters


class CreatedTimeBasedOrdering(filters.OrderingFilter):

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            return queryset.order_by('-created_time').order_by(*ordering)

        return queryset
