from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet

from db.models import Order, Ticket, MovieSession


def create_order(
        tickets: list,
        username: str,
        date: str = None
) -> None:
    with transaction.atomic():
        user = get_user_model().objects.get(username=username)
        order = Order.objects.create(user=user)

        if date:
            order.created_at = date
            order.save(update_fields=["created_at"])

        unique_id = [item["movie_session"] for item in tickets]
        queryset = MovieSession.objects.filter(id__in=unique_id)
        new_dict = {
            el.id: el
            for el in queryset
        }

        tickets_list = [
            Ticket(
                order=order,
                movie_session=new_dict[item["movie_session"]],
                row=item["row"],
                seat=item["seat"]
            ) for item in tickets
        ]

        Ticket.objects.bulk_create(tickets_list)


def get_orders(username: str = None) -> QuerySet:
    queryset = Order.objects.select_related("user").all()

    if username:
        queryset = queryset.filter(user__username=username)

    return queryset
