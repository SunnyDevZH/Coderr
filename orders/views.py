from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order
from .serializers import OrderSerializer
from accounts.models import User

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]  # TokenAuthentication verwenden
    permission_classes = [IsAuthenticated]  # Authentifizierung erforderlich
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_user', 'business_user', 'status']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        """
        Filters orders based on the query parameters.
        """
        queryset = super().get_queryset()
        customer_user_id = self.request.query_params.get('customer_user_id')
        business_user_id = self.request.query_params.get('business_user_id')
        status = self.request.query_params.get('status')
        ordering = self.request.query_params.get('ordering', '-created_at')

        if customer_user_id:
            queryset = queryset.filter(customer_user_id=customer_user_id)
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if status:
            queryset = queryset.filter(status=status)
        queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Creates a new order.
        """
        data = request.data
        data['customer_user'] = request.user.id 
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"Aktuelle Anfrage von Benutzer ID {request.user.id}")
        order = Order.objects.get(id=6)
        print(f"customer_user: {order.customer_user.id}, business_user: {order.business_user.id}")

        if instance.customer_user != request.user and instance.business_user != request.user and not request.user.is_staff:
            print("Permission denied: User is not the customer, business user, or an admin.")
            return Response({"detail": "You do not have permission to edit this order."}, status=status.HTTP_403_FORBIDDEN)
    
        print(f"Updating order {instance.id} to status {request.data.get('status')}")
        return super().partial_update(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        """
        Deletes an order. Only admins are allowed to delete orders.
        """
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete orders."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='order-count/(?P<business_user_id>[^/.]+)')
    def order_count(self, request, business_user_id=None):
        """
        Returns the number of ongoing orders (status: in_progress) for a business user.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})

    @action(detail=False, methods=['get'], url_path='completed-order-count/(?P<business_user_id>[^/.]+)')
    def completed_order_count(self, request, business_user_id=None):
        """
        Returns the number of completed orders (status: completed) for a business user.
        """
        business_user = get_object_or_404(User, pk=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})

    def list(self, request, *args, **kwargs):
        """
        Overrides the default list method to ensure the response is always an array.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CustomerOrdersView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]
    """
    Returns all orders placed by the currently authenticated customer.
    """
    def get(self, request):
        orders = Order.objects.filter(customer_user=request.user)
        if not orders.exists():
            return Response({"orders": [], "message": "No orders found."})
        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})


class OrderCountView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [AllowAny]
    """
    Returns the number of active orders (status: in_progress) for a given business user.
    """
    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, pk=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})


class CompletedOrderCountView(APIView):
    authentication_classes = [TokenAuthentication] 
    permission_classes = [AllowAny]
    """
    #Returns the number of completed orders (status: completed) for a given business user.
    """
    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, pk=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})
