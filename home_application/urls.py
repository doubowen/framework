# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^api/test/$', 'test'),
    (r'^get_set_list/$', 'get_set_list'),
    (r'^history/$', 'history'),
    (r'^get_host_list/$', 'get_host_list'),
    (r'^get_history_log/$', 'get_history_log'),
    (r'^fast_execute_script/$', 'fast_execute_script'),
)
