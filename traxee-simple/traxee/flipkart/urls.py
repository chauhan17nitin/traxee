from django.conf.urls import url
from . import views

app_name = 'flipkart'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^signup/$', views.signup_user, name='signup'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^search/$', views.search_product, name='search'),
    url(r'^add_track/(?P<product_id>\w+)/$', views.add_track, name='add_track'),
    url(r'^track/$', views.display_track, name='track'),
    url(r'^(?P<product_id>\w+)/del_track/$', views.remove_track, name='delete_track'),
]