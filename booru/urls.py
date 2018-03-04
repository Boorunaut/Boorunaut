from django.urls import path
from django.conf.urls import url

from . import views

app_name = "booru"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post/view/(?P<post_id>[0-9]+)/$', views.post_detail, name='post_detail'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^post/list/$', views.post_list_detail, name='posts'),
    url(r'^post/list/(?P<page_number>[0-9]+)/$', views.post_list_detail, name='post_page_detail'),
    url(r'^tags/$', views.tags_list, name='tags_list'),
    url(r'^tags/list/(?P<page_number>[0-9]+)/$', views.tags_list, name='tags_page_list'),
    url(r'^tags/(?P<tag_id>[0-9]+)/edit/$', views.tag_edit, name='tag_edit'),
    path('tag_implications', views.ImplicationListView.as_view(), name='implication-list'),
    path('tag_implications/<int:pk>/', views.ImplicationDetailView.as_view(), name='implication-detail'),
    path('tag_aliases', views.AliasListView.as_view(), name='alias-list'),
    path('tag_aliases/<int:pk>/', views.AliasDetailView.as_view(), name='alias-detail'),
]
