from django.urls import include, path, re_path

import booru.account.views
import booru.core.views

from . import views

app_name = "booru"

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^upload/$', views.upload, name='upload'),

    re_path(r'^post/view/(?P<post_id>[0-9]+)/$', views.post_detail, name='post_detail'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/history$', views.post_history, name='post_history'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/history/(?P<page_number>[0-9]+)/$', views.post_history, name='post_history'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/approve$', views.post_approve, name='post_approve'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/hide$', views.post_hide, name='post_hide'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/delete$', views.post_delete, name='post_delete'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/favorite$', views.post_favorite, name='post_favorite'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/vote$', views.post_score_vote, name='post_score_vote'),
    re_path(r'^post/view/(?P<post_id>[0-9]+)/flag$', booru.core.views.PostFlagCreateView.as_view(), name='post_flag'),

    re_path(r'^post/list/$', views.post_list_detail, name='posts'),
    re_path(r'^post/list/(?P<page_number>[0-9]+)/$', views.post_list_detail, name='post_page_detail'),
    
    re_path(r'^tags/$', views.tags_list, name='tags_list'),
    re_path(r'^tags/(?P<tag_id>[0-9]+)/$', views.tag_detail, name='tag_detail'),
    re_path(r'^tags/list/(?P<page_number>[0-9]+)/$', views.tags_list, name='tags_page_list'),
    re_path(r'^tags/(?P<tag_id>[0-9]+)/edit/$', views.tag_edit, name='tag_edit'),
    path('tags/<int:pk>/delete/', views.TagDelete.as_view(), name='tag-delete'),
    re_path(r'^tags/(?P<tag_id>[0-9]+)/history/$', views.tag_history, name='tag_history'),
    re_path(r'^tags/(?P<tag_id>[0-9]+)/history/(?P<page_number>[0-9]+)/$', views.tag_history, name='tag_history'),
    re_path(r'^tags/(?P<tag_id>[0-9]+)/revision_difference/$', views.tag_revision_diff, name='tag_revision_diff'),

    path('tag_implications', views.ImplicationListView.as_view(), name='implication-list'),
    path('tag_implications/<int:pk>/', views.ImplicationDetailView.as_view(), name='implication-detail'),

    re_path(r'^tag_implication_request/$', views.implication_create, name='implication_create'),

    re_path(r'^tag_implications/(?P<implication_id>[0-9]+)/approve/$', views.implication_approve, name='implication_approve'),
    re_path(r'^tag_implications/(?P<implication_id>[0-9]+)/disapprove/$', views.implication_disapprove, name='implication_disapprove'),
    
    re_path(r'^tag_search/$', views.tag_search, name='tag_search'),

    re_path(r'^profile/(?P<account_slug>[\w-]+)/$', booru.account.views.profile, name='profile'),
    re_path(r'^profile/(?P<account_slug>[\w-]+)/delete$', booru.account.views.DeleteAccountView.as_view(), name='profile_delete'),

    re_path(r'^gallery/list/$', views.gallery_list, name='gallery'),
    re_path(r'^gallery/list/(?P<page_number>[0-9]+)/$', views.gallery_list, name='gallery_list'),
    re_path(r'^gallery/new/$', views.gallery_create, name='gallery_create'),
    re_path(r'^gallery/(?P<gallery_id>[0-9]+)/$', views.gallery_detail, name='gallery_detail'),
    re_path(r'^gallery/(?P<gallery_id>[0-9]+)/edit$', views.gallery_edit, name='gallery_edit'),
    re_path(r'^gallery/(?P<gallery_id>[0-9]+)/history/$', views.gallery_history, name='gallery_history'),
    re_path(r'^gallery/(?P<gallery_id>[0-9]+)/history/(?P<page_number>[0-9]+)/$', views.gallery_history, name='gallery_history_page'),
    
    re_path(r'^staff_page/$', views.staff_page, name='staff_page'),
    re_path(r'^staff_page/mass_rename$', views.staff_mass_rename, name='staff_mass_rename'),
    re_path(r'^staff_page/configuration$', views.SiteConfigurationView.as_view(), name='staff_site_configuration'),
    re_path(r'^staff_page/block$', views.StaffBanUser.as_view(), name='staff_block'),

    path('comment/<int:pk>/toggle_view', booru.core.views.StaffCommentToggleHiddenView.as_view(), name='comment-toggle-view'),
]
