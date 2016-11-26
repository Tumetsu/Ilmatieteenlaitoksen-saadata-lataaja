import math
import datetime
import copy
from fmiapi.fmirequest import FMIRequest


class FMIRequestHandler:
    """
    This class takes a data request and splits it to multiple http-requests if required and
    does the request by using FMIRequest class.
    """

    def __init__(self, api_key):
        self._api_key = api_key
        self._FMI_request = FMIRequest(self._api_key)
        self._callbackFunction = None

    def request(self, params, max_timespan, progress_callback=None):
        requests = self._divide_to_multiple_requests(params, max_timespan)
        return self._execute_requests(requests, progress_callback)

    def _execute_requests(self, requests, progress_callback):
        all_requests = len(requests)
        responses = []
        count = 0
        for r in requests:
            responses.append(self._do_request(r))
            count += 1
            if progress_callback is not None:
                progress_callback(count, all_requests)
        return responses

    def _do_request(self, request):
        return self._FMI_request.get(request)

    @staticmethod
    def _divide_to_multiple_requests(params, max_timespan):
        requests = []
        done = False
        i = 0
        while not done:
            request_params = copy.copy(params)
            request_params["starttime"] += datetime.timedelta(hours=max_timespan) * i
            request_params["endtime"] = request_params["starttime"] + datetime.timedelta(hours=max_timespan)

            # This additional minute to starting time is to prevent requests from fetching same time twice in
            # the splitting point. Otherwise previous request's last time will be fetched as first in the next.
            # FMI's service recognizes minutes as smallest significate time step so seconds or milliseconds could not
            # be used.
            if i > 0:
                request_params["starttime"] += datetime.timedelta(minutes=1)

            requests.append(request_params)

            if request_params["endtime"] > params["endtime"]:
                done = True
                request_params["endtime"] = params["endtime"]
            i += 1
        return requests
