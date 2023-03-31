import logging
import os

from django.http import HttpResponse
from django.shortcuts import render
import requests
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_logger")

from dotenv import load_dotenv
load_dotenv()


def main_page_view(request):
    model = SearchingModel()
    aircrafts = model.get_aircrafts()
    return render(request, 'index.html', context={'aircrafts': aircrafts})


def aircraft_info(request, tail_number):
    model = SearchingModel(tail_number=tail_number)
    aircraft = model.get_aircrafts(tail_number)
    aircraft = aircraft[0] if aircraft else None
    print(aircraft.keys())

    company = model.get_company(aircraft['company_name'])
    logger.debug(company)
    if not aircraft:
        return HttpResponse("Error: Aircraft not found.")
    return render(request, 'aircraft_info.html', {'aircraft': aircraft, 'company': company})


def searching(request):
    query_ = request.GET['search_query']
    type_ = request.GET['search_type']
    logger.debug(request)
    if type_ == "tail_number":
        model = SearchingModel(tail_number=type_)
    else:
        model = SearchingModel(serial_number=type_)
    aircrafts = model.get_aircrafts(query_)
    return render(request, 'index.html', context={'aircrafts': aircrafts})


class SearchingModel():

    AIRCRAFTS_LIMIT = 300
    headers = {
        'accept': "application/json",
        'authorization': os.getenv("TOKEN")
    }

    tail_number = None
    serial_number = None

    def __init__(self, tail_number=None, serial_number=None):
        self.tail_number = tail_number
        self.serial_number = serial_number

    def get_aircrafts(self, query_=None):
        if query_ is None or len(query_) < 2:
            return None
        request_query = "https://dir.aviapages.com/api/aircraft/?ordering=aircraft_id&images=True"
        if self.tail_number is not None:
            request_query += f'&search_tail_number={query_}'
        elif self.serial_number is not None:
            request_query += f'&search_serial_number={query_}'
        logger.debug(request_query)
        response = requests.get(
            request_query,
            headers=self.headers
        )
        json_result = json.loads(response.content)
        if response:
            logger.debug(json_result["results"][0])
            return json_result["results"][:self.AIRCRAFTS_LIMIT]
        else:
            logger.debug("error")
        return None

    def get_company(self, company_name):
        request_query = "https://dir.aviapages.com/api/companies/"
        request_query += f'?search_name={company_name}'
        response = requests.get(
            request_query,
            headers=self.headers
        )
        json_result = json.loads(response.content)
        if response:
            logger.debug(json_result["results"])
            for company in json_result["results"]:
                print(company['name'],company_name)
                if company['name'] == company_name:
                    return company
        else:
            logger.debug("error")
        return None
