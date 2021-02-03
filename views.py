from django.shortcuts import render, redirect
import os
import requests
import base64
import json
import time


def registration(request):
    if (request.GET.get("Neon_event_id") is None):
        return render(request, 'index.html')


    try:

        Neon_login_r = requests.get('https://api.neoncrm.com/neonws/services/api/common/login?', params={'login.apiKey':Neon_login_API_key, 'login.orgid': Neon_org_id})

        # Ticket Tailor events data pulled from Ticket Tailor API: https://developers.tickettailor.com/#ticket-tailor-api
        TT_headers = {
                  'Accept': 'application/json',
                  'Authorization': 'Basic %s' % TT_API_key,
                }
        TT_events_r = requests.get('https://api.tickettailor.com/v1/events', params={}, headers = TT_headers)
        TT_events_data = TT_events_r.json()
        TT_events_data = TT_events_data.get("data")

        # Neon API user session id pulled from API
        Neon_login_data = Neon_login_r.json()
        Neon_login_data = Neon_login_data.get("loginResponse")
        Neon_user_session_id = Neon_login_data.get("userSessionId") #user session id authenticates an API user and grant access to make further requests.

        # First page of Neon event data pulled from Neon CRM API: https://developer.neoncrm.com/api/events/
        Neon_events_r = requests.get('https://api.neoncrm.com/neonws/services/api/event/listEvents?userSessionId={0}&outputfields.idnamepair.name=Event Name&outputfields.idnamepair.name=Event Start Date&outputfields.idnamepair.name=Event ID&searches.search.key=Event Start Date&searches.search.searchOperator=GREATER_THAN&searches.search.value={1}&page.sortColumn=Event ID'.format(Neon_user_session_id, '2020-01-01'))
        Neon_events_data = Neon_events_r.json()
        Neon_events_data = Neon_events_data.get("listEvents")

        Neon_event_id = int(request.GET.get("Neon_event_id"))
        page_count = 1
        last_event_id = Neon_events_data.get("searchResults").get("nameValuePairs")[-1]
        last_event_id = int((last_event_id.get("nameValuePair"))[1].get("value"))
        while last_event_id < Neon_event_id:
            # go to next page in Neon's events data to search for this event
            page_count += 1
            Neon_events_r = requests.get('https://api.neoncrm.com/neonws/services/api/event/listEvents?userSessionId={0}&outputfields.idnamepair.name=Event Name&outputfields.idnamepair.name=Event Start Date&outputfields.idnamepair.name=Event ID&searches.search.key=Event Start Date&searches.search.searchOperator=GREATER_THAN&searches.search.value={1}&page.sortColumn=Event ID&page.currentPage={2}'.format(Neon_user_session_id, '2020-01-01', page_count))
            Neon_events_data = Neon_events_r.json()
            Neon_events_data = Neon_events_data.get("listEvents")

            last_event_id = Neon_events_data.get("searchResults").get("nameValuePairs")[-1]
            last_event_id = int((last_event_id.get("nameValuePair"))[1].get("value"))

        # find the AOA event's name and date by the event id
        for event in Neon_events_data.get("searchResults").get("nameValuePairs"):
            if int((event.get("nameValuePair"))[1].get("value")) == Neon_event_id:
                eventName = (event.get("nameValuePair"))[0].get("value")
                eventDate = (event.get("nameValuePair"))[2].get("value")
                break

        # userPreferences is a list of tuples containing the user's inputs into the time slot filtering form (in iframe url)
        userPreferences = []
        for keys, values in list(request.GET.items()):
            if keys == "Neon_event_id":
                continue
            elif values.isnumeric() :
                userPreferences.append((keys, int(values)))
            elif values == "on":
                userPreferences.append((keys, "true"))
            else:
                userPreferences.append((keys, values))

        # timeSlots is a list of the Ticket Tailor events that represent different time slots for an AOA event
        # Pulls all events from Ticket Tailor which have the same name and date as specified in the iframe url
        # time slots in Ticket Tailor have the same name, date, event_series_id, but different event_id and time
        timeSlotsDict = {}
        timeSlots = []
        for event in list(TT_events_data):
            if (event.get("name") == eventName and event.get("start").get("date") == eventDate):
                timeSlotsDict[event.get("start").get("time")] = event
        timeSlots = [value for (key, value) in sorted(timeSlotsDict.items())]


        ticketGroups = []
        for group in timeSlots[0].get("ticket_groups"):
            ticketGroups.append(group)

        # list of dictionaries for every time slot containing the time slot's event id, the quantity of tickets in its Tandem
        # Recumbent Trikes ticket group and the quantity of tickets in its Duet Wheelchair Bicycle Tandems ticket group
        groupQuantitiesList = []
        for timeSlot in timeSlots:
            groupQuantitiesDict = {}
            for group in timeSlot.get("ticket_groups"):
                groupQuantitiesDict['id'] = timeSlot.get("id")
                groupTixQuantity = 0
                if "Duet" in group.get("name") or "Tandem Recumbent" in group.get("name"):
                    for tixTypeId in group.get("ticket_ids"):
                        for tixType in timeSlot.get("ticket_types"):
                            if (tixTypeId in tixType.values() and tixType.get):
                                groupTixQuantity += int(tixType.get("quantity"))
                    groupQuantitiesDict[group.get("name")[:3]] = groupTixQuantity
            if groupQuantitiesDict != {}:
                groupQuantitiesList.append(groupQuantitiesDict)

        Neon_logout_r = requests.get("https://api.neoncrm.com/neonws/services/api/common/logout", params={"userSessionId":"Neon_user_session_id"})

        return render(request, 'index.html', {
            'eventName': eventName,
            'eventDate': eventDate,
            'userPreferences': userPreferences,
            'timeSlots': timeSlots,
            'ticketGroups': ticketGroups,
            'groupQuantitiesList': groupQuantitiesList,
            'Neon_event_id': Neon_event_id,
        })

    except:
        return redirect('/handler500')

def handler500_error_view(request):
    return render(request, 'handler500.html')

from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def ok_to_load_in_a_frame(request):
    return HttpResponse("This page is safe to load in a frame on any site.")