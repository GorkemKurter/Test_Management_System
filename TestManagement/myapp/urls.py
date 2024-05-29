from django.urls import path
from .views import (login_view, home_view, tests_view,
                    testrequest_view, test_request_filter_view,
                    get_test_details, add_to_calendar)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('tests/', tests_view, name='tests'),
    path('home/testrequests/', testrequest_view, name='testrequests'),
    path('home/testrequestslist/', test_request_filter_view, name='home/testrequestslist/'),
    path('get_test_details/', get_test_details, name='get_test_details'),
    path('add_to_calendar/', add_to_calendar, name='add_to_calendar'),

]
