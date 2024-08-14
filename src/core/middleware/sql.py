from django.conf import settings
from django.db import connection


class SqlPrintingMiddleware:
    """
    Middleware which prints out a list of all SQL queries done
    for each view that is processed.
    Original source: https://gist.github.com/vstoykov/1390853/5d2e8fac3ca2b2ada8c7de2fb70c021e50927375
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response = self.process_response(request, response)

        return response

    def process_response(self, request, response):
        if not settings.DEBUG or len(connection.queries) == 0 or request.path_info.startswith(settings.MEDIA_URL):
            return response

        indentation = 2
        print("\n\n%s\033[1;35m[SQL Queries for]\033[1;34m %s\033[0m\n" % (" " * indentation, request.path_info))
        total_time = 0
        for query in connection.queries:
            nice_sql = query["sql"].replace('"', "").replace(",", ", ")
            sql = "\033[1;31m[%s]\033[0m %s" % (query["time"], nice_sql)
            total_time = total_time + float(query["time"])
            print("%s%s\n" % (" " * indentation, sql))
        replace_tuple = (" " * indentation, str(total_time))
        print("%s\033[1;32m[TOTAL TIME: %s seconds]\033[0m" % replace_tuple)
        return response
