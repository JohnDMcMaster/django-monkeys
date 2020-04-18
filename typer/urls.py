from django.conf.urls import url

from .views import indexView, taskInstructionsView, adminSummaryHomeView, adminSummaryView, taskSpecificUserStatisticsView, adminStatisticsView

app_name = 'typer'
urlpatterns = [
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/$', indexView, name='index'),
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/statistics/(?P<userName>[a-zA-Z0-9\._@\-]+)/$', taskSpecificUserStatisticsView, name='taskSpecificUserStatistics'),
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/instructions/$', taskInstructionsView, name='taskInstructions'),
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/adminStatistics/$', adminStatisticsView, name='adminStatistics'),
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/$', adminSummaryHomeView, name='adminSummaryHome'),
    url(r'^die/(?P<dieName>[a-zA-Z0-9-_]+)/adminSummary/(?P<imageId>[0-9]+)/$', adminSummaryView, name='adminSummaryView'),
]
