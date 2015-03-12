from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from stream_twitter import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^discover/', login_required(views.discover)),
                       url(r'^timeline/',
                           login_required(views.TimelineView.as_view())),
                       url(r'^user/(?P<user_name>.+)/$', views.user),
                       url(r'^hashtag/(?P<hashtag_name>.+)/', views.hashtag),
                       url(r'^accounts/login/', 'django.contrib.auth.views.login',
                           {'template_name': 'admin/login.html'}),
                       url(r'^accounts/logout/',
                           'django.contrib.auth.views.logout'),
                       url(r'^$', views.HomeView.as_view()),
                       url(r'^follow/$', login_required(views.follow), name='follow'),
                       url(r'^unfollow/(?P<target_id>\d+)/$', login_required(views.unfollow), name='unfollow')
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns(
    'django.views.static',
    (r'media/(?P<path>.*)',
     'serve',
     {'document_root': settings.MEDIA_ROOT}))
