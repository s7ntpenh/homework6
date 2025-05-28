import logging

from django.utils.deprecation import MiddlewareMixin

from general.models import RequestStatistics

logger = logging.getLogger('middlewares')

class RequestStatisticMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def __call__(self, request):
        logger.debug('Called BEFORE view and get_response')
        response = self.get_response(request)
        logger.debug('Called AFTER view and get_response')
        return  response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and not request.path.startswith("/admin"):
            stats, is_created = RequestStatistics.objects.get_or_create(user=request.user)
            stats.requests += 1
            stats.save()

    def process_exception(self, request, exception):
        stat, _ = RequestStatistics.objects.get_or_create(
            path=request.path,
            method=request.method,
        )
        stat.exceptions += 1
        stat.save()