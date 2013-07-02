import json
import logging

from urbanairship import common


logger = logging.getLogger('urbanairship')


class Push(object):
    """A push notification. Set audience, message, etc, and send."""

    def __init__(self, airship):
        self._airship = airship
        self.audience = None
        self.notification = None
        self.device_types = None
        self.options = None
        self.message = None

    @property
    def payload(self):
        data = {
            "audience": self.audience,
            "notification": self.notification,
            "device_types": self.device_types,
        }
        if self.options is not None:
            data['options'] = self.options
        if self.message is not None:
            data['message'] = self.message
        return data

    def send(self):
        """Send the notification.

        :returns: Dictionary with response information, including ``push_id``.
        :raises AirshipFailure: Request failed. See args for status and
            response body.
        :raises Unauthorized: Authentication failed.

        """
        body = json.dumps(self.payload)
        response = self._airship._request('POST', body,
            common.PUSH_URL, 'application/json', version=3)

        data = response.json()
        logger.info("Push successful. push_ids: %s",
            ', '.join(data['push_ids']))

        return PushResponse(response)


class ScheduledPush(object):
    """A scheduled push notification. Set schedule, push, and send."""

    def __init__(self, airship):
        self._airship = airship
        self.schedule = None
        self.name = None
        self.push = None

    @property
    def payload(self):
        data = {
            "schedule": self.schedule,
            "push": self.push.payload,
        }
        if self.name is not None:
            data['name'] = self.name
        return data

    def send(self):
        """Schedule the notification

        :returns: Dictionary with response information, including ``push_id``.
        :raises AirshipFailure: Request failed. See args for status and
            response body.
        :raises Unauthorized: Authentication failed.

        """
        body = json.dumps(self.payload)
        response = self._airship._request('POST', body,
            common.SCHEDULES_URL, 'application/json', version=3)

        data = response.json()
        logger.info("Push successful. push_ids: %s",
            ', '.join(data.get('push_ids', [])))

        return PushResponse(response)


class PushResponse(object):
    """Response to a successful push notification send or schedule.

    Right now this is a fairly simple wrapper around the json payload response,
    but making it an object gives us some flexibility to add functionality
    later.

    """
    ok = None
    push_ids = None
    schedule_ids = None
    operation_id = None
    payload = None

    def __init__(self, response):
        data = response.json()
        self.push_ids = data.get('push_ids')
        self.schedule_ids = data.get('schedule_ids')
        self.operation_id = data.get('operation_id')
        self.ok = data.get('ok')
        self.payload = data
