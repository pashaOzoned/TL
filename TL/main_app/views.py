from django.contrib.auth import logout
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View

from authentication.models import User
from .models import Photo
import random
import datetime


def change_photo(request):
    counter_to_change = {0: 20, 1: 100, 2: 10000000}
    range_of_search = {0: 10, 1: 25, 2: request.session['distance']}
    current_user = User.objects.get(email=request.session['user']['email'])
    users = User.objects.exclude(id=current_user.id)
    last_user = users.last()
    photo_session = request.session['photo']

    photos = Photo.objects.exclude(user_id=current_user.id)
    if current_user.counter < counter_to_change[current_user.type_of_account]:
        current_user.counter += 1
        current_user.save()

        for user in users:
            if (user.lat - current_user.lat) ** 2 + (user.lng - current_user.lng) ** 2 <= \
                    range_of_search[current_user.type_of_account] ** 2:
                if user.id == last_user.id:
                    request.session['photo'] = {'url': photos.first().url, 'user_id': photos.first().user_id}
                elif user.id > photo_session['user_id']:
                    try:
                        request.session['photo'] = {'url': photos.filter(user_id=user.id).first().url,
                                                    'user_id': photos.filter(user_id=user.id).first().user_id}
                        break
                    except AttributeError:
                        if user.id == last_user.id:
                            request.session['photo'] = {'url': photos.first().url, 'user_id': photos.first().user_id}
                            break
                        else:
                            continue
            if user.id == last_user.id:
                request.session['photo'] = {'url': photos.first().url, 'user_id': photos.first().user_id}


class IndexView(View):
    counter_to_change = {0: 20, 1: 100, 2: 10000000}

    def get(self, request):
        try:
            current_user = User.objects.get(email=request.session['user']['email'])
            try:
                photo = request.session['photo']
                user = User.objects.get(id=photo['user_id'])
            except:
                return render(request, "index.html", context={'auth': 1,
                                                              'current_user': current_user,
                                                              'emptyError': 1})
        except:
            return render(request, "index.html", context={'auth': 0})
        else:
            return render(request, "index.html", context={'auth': 1,
                                                          'current_user': current_user,
                                                          'photo': photo,
                                                          'user': user,
                                                          'limit': self.counter_to_change[current_user.type_of_account]
                                                          })



class DizView(View):
    def post(self, request):
        change_photo(request)
        return HttpResponseRedirect('/')


class LikeView(View):
    def post(self, request):
        another_user_like = random.randint(0, 1)

        if another_user_like == 1:
            return HttpResponseRedirect("/messenger")
        else:
            change_photo(request)

        return HttpResponseRedirect("/")


class SignUpView(View):
    def get(self, request):
        return render(request, "sign up.html")


class SignInView(View):
    def get(self, request):
        return render(request, "sign in.html")


class SignOutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class ProfileView(View):
    def get(self, request):
        current_user = User.objects.get(email=request.session['user']['email'])
        print(current_user.type_of_account)
        return render(request, 'userpage.html', context={'user': current_user})

    def post(self, request):
        user = request.session['user']

        current_user = User.objects.get(email=user['email'])
        if request.POST.get("old_password") == user['password']:
            if request.POST.get("new_password") != '':
                current_user.set_password(request.POST.get("new_password"))

        t = 0
        dt = datetime.datetime.now()
        if (current_user.time_last_change_location + datetime.timedelta(hours=2)).timestamp() < dt.timestamp():

            lat = request.POST.get('lat')
            lng = request.POST.get('lng')
            if lat and lat != current_user.lat:
                current_user.lat = request.POST.get('lat')
                t = 1
            if lng and lng != current_user.lng:
                current_user.lng = request.POST.get('lng')
                t = 1

            if t == 1:
                current_user.time_last_change_location = dt

        current_user.type_of_account = request.POST.get('type_of_account')

        current_user.save()
        current_user = User.objects.get(email=request.session['user']['email'])
        if current_user.type_of_account == 2:
            try:
                request.session['distance'] = int(request.POST.get('distance'))
            except:
                request.session['distance'] = 20
        else:
            request.session['distance'] = 20
        return HttpResponseRedirect('/')


class AddPhotoView(View):

    def get(self, request):
        user = request.session['user']
        return render(request, 'add.html', context={'user': user})

    def post(self, request):
        u = User.objects.get(email=request.session['user']['email'])
        Photo.objects.create(user_id=u.id,
                             url=request.POST.get("url"),
                             title=request.POST.get('title'))
        return HttpResponseRedirect('/')


class MessengerView(View):
    def get(self, request):
        current_user = User.objects.get(email=request.session['user']['email'])
        another_user = User.objects.get(id=request.session['photo']['user_id'])
        return render(request, 'messenger.html', context={'current': current_user,
                                                          'another': another_user})

    def post(self, request):
        return HttpResponseRedirect("/messenger")
