from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from authentication.models import User
from authentication.renderers import UserJSONRenderer
from authentication.serializers import LoginSerializer, RegistrationSerializer
from main_app.models import Photo
import requests

class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.POST

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponseRedirect("/")


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.POST

        current_user = User.objects.get(email=user['email'])
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        request.session['user'] = user

        photo = Photo.objects.exclude(user_id=current_user.id).first()
        try:
            request.session['photo'] = {'url': photo.url, 'user_id': photo.user_id}
        except:
            request.session['emptyError'] = True
        request.session['distance'] = 20

        return HttpResponseRedirect("/")
