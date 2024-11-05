from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import GenericViewSet

from .models import User
from .serializers import SubscriptionUserSerializer


class SubscriptionsView(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=['get'])
    def subscriptions(self, request: Request) -> Response:
        paginated_data = self.paginate_queryset(
            SubscriptionUserSerializer(
                request.user.subscription_list.users.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )
        return self.get_paginated_response(paginated_data)

    @action(
        detail=True,
        methods=['post'],
    )
    def subscribe(self, request: Request, pk: int) -> Response:
        user_to_subscribe = self.get_object()
        current_user = request.user

        if current_user == user_to_subscribe:
            return Response(status=HTTP_400_BAD_REQUEST)

        if user_to_subscribe in current_user.subscription_list.users.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.subscription_list.users.add(user_to_subscribe)

        return Response(
            SubscriptionUserSerializer(
                user_to_subscribe,
                context=self.get_serializer_context(),
            ).data,
            status=HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request: Request, pk: int) -> Response:
        current_user = request.user
        user_to_unsubscribe = self.get_object()

        if (
            user_to_unsubscribe
            not in current_user.subscription_list.users.all()
        ):
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.subscription_list.users.remove(user_to_unsubscribe)

        return Response(status=HTTP_204_NO_CONTENT)
