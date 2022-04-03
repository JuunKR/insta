from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Feed, Like, Bookmark
from uuid import uuid4
from config.settings import MEDIA_ROOT
from user.models import User
import os


# Create your views here.
class Main(APIView):
    def get(self, request):
        
        feed_list = Feed.objects.all().order_by('-id')
        
        email = request.session.get('email')

        if email is None:
            return render(request, "user/login.html")
        
        user = User.objects.filter(email=email).first()
        
        if user is None:
            return render(request, "user/login.html")
        
        
        return render(request, "insta/main.html", context=dict(feeds=feed_list, user=user))
    
class UploadFeed(APIView):
    def post(self, request):
        
        file = request.FILES.get('file')
        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        content = request.data.get('content')
        image = uuid_name
        profile_image = request.data.get('profile_image')
        user_id = request.data.get('user_id')

        Feed.objects.create(content=content, image=image, profile_image=profile_image, user_id=user_id, like_count=0)

        return Response(status=200)
    
class Profile(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, "user/login.html")

        feed_list = Feed.objects.filter(email=email)
        like_list = list(Like.objects.filter(email=email, is_like=True).values_list('feed_id', flat=True))
        like_feed_list = Feed.objects.filter(id__in=like_list)
        bookmark_list = list(Bookmark.objects.filter(email=email, is_marked=True).values_list('feed_id', flat=True))
        bookmark_feed_list = Feed.objects.filter(id__in=bookmark_list)
        return render(request, 'content/profile.html', context=dict(feed_list=feed_list,
                                                                    like_feed_list=like_feed_list,
                                                                    bookmark_feed_list=bookmark_feed_list,
                                                                    user=user))
    def post(self, request):
        # 일단 파일 불러와
        file = request.FILES['file']
        email = request.data.get('email')
        print(file)

        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        profile_image = uuid_name

        user = User.objects.filter(email=email).first()

        user.thumbnail = profile_image
        user.save()

        return Response(status=200)