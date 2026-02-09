from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet

from db.models import Order, MovieSession, Ticket

if TYPE_CHECKING:
    pass


@transaction.atomic
def create_order(
        tickets: list,
        username: str,
        date: str = None
) -> None:
    user = get_user_model().objects.get(username=username)

    order = Order.objects.create(user=user)

    if date:
        parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        order.created_at = parsed_date
        order.save(update_fields=["created_at"])

    movie_session_ids = [item["movie_session"] for item in tickets]
    queryset = MovieSession.objects.filter(id__in=movie_session_ids)
    movie_sessions_dict = {
        session.id: session
        for session in queryset
    }

    tickets_list = [
        Ticket(
            order=order,
            movie_session=movie_sessions_dict[item["movie_session"]],
            row=item["row"],
            seat=item["seat"]
        ) for item in tickets
    ]

    for ticket in tickets_list:
        ticket.full_clean()

    Ticket.objects.bulk_create(tickets_list)


def get_orders(username: str = None) -> "QuerySet[Order]":
    queryset = Order.objects.select_related("user").all()

    if username is not None:
        queryset = queryset.filter(user__username=username)

    return queryset
