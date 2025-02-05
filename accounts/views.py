from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer, ReviewSerializer
from .models import User, Review
from offers.models import Offer
from django.db.models import Avg

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'user_id': user.user_id,
                'type': user.type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'user_id': user.user_id,
                'type': user.type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_type = self.request.query_params.get('type')
        if user_type:
            queryset = queryset.filter(type=user_type)
        return queryset

    @action(detail=False, methods=['get'], url_path='business')
    def list_business(self, request):
        queryset = self.get_queryset().filter(type='business')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer')
    def list_customer(self, request):
        queryset = self.get_queryset().filter(type='customer')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_queryset().filter(pk=pk).first()
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        business_profile_count = User.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": round(average_rating, 1),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        ordering = self.request.query_params.get('ordering', '-updated_at')

        if business_user_id and business_user_id != 'undefined':
            queryset = queryset.filter(user_id=business_user_id)
        queryset = queryset.order_by(ordering)

        return queryset
