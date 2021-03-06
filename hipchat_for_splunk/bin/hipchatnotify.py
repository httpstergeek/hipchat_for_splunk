#
# All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Bernardo Macias '
__credits__ = ['Bernardo Macias']
__license__ = "ASF"
__version__ = "2.0"
__maintainer__ = "Bernardo Macias"
__email__ = 'bmacias@httpstergeek.com'
__status__ = 'Production'

import sys
import json
from logging import INFO
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option

import util


@Configuration()
class hipChatNotifyComand(StreamingCommand):
    """ %(synopsis)

    ##Syntax
    .. code-block::
    hipchatnotify msg="<key1>=<value1> <key2>=<value2>" fields="<field>,<field>"

    ##Description

    Sends an hipchat notification for each event generated in search.

    ##Example

    Sends an hipchat event

    .. code-block::
        ...| hipchatnotify msg="Server threshold exceed threshold" fields="host,avg_cpu" room=splunk
            OR
        ...| hipchatnotify msg="Server threshold exceed threshold" room=152648

    """

    msg = Option(
        doc='''**Syntax:** **msg=***<str>*
        **Description:** String to attach notification event.''',
        require=False)

    room = Option(
        doc='''**Syntax:** **room=***<str>*
        **Description:** Room name or id''',
        require=False)

    fields = Option(
        doc='''**Syntax:** **fields=***<str>*
        **Description:** list of fields separated by commas. Default is will send all fields''',
        require=False)

    color = Option(
        doc='''**Syntax:** **color=***<str>*
        **Description:** Background color for message. Valid values: yellow, green, red, purple, gray, random.
        Defaults to 'yellow''',
        require=False)

    notify = Option(
        doc='''**Syntax:** **color=***<bol>*
        **Description:** whether this message should trigger a user notification (change the tab color, play a sound,
        notify mobile phones, etc). Each recipient's notification preferences are taken into account. Defaults
        to false.''',
        require=False)

    listrooms = Option(
        doc='''**Syntax:** **color=***<bol>*
        **Description:** whether this message should trigger a user notification (change the tab color, play a sound,
        notify mobile phones, etc). Each recipient's notification preferences are taken into account. Defaults
        to false.''',
        require=False)

    def generate(self):
        logger = util.setup_logger(INFO)
        try:
            default_conf = util.getstanza('hipchat', 'default')
            local_conf = util.getstanza('hipchat', 'hipchat')
            proxy_conf = util.setproxy(local_conf, default_conf)
            hipchat_url = local_conf['url'] if 'url' in local_conf else default_conf['url']
            auth_token = local_conf['authToken'] if 'authToken' in local_conf else default_conf['autToken']
            timeout = local_conf['timeout'] if 'timeout' in local_conf else default_conf['timeout']
        finally:
            logger.info('Unable to parse Config File. Check if hipchat.conf exists')
            raise Exception("Unable to parse Config File. Check if hipchat.conf exists")
            exit()

        headers = dict(Authorization='Bearer {0}'.format(auth_token))
        data = dict(message=None, message_format='text')
        hipchat_room_url = '{0}/v2/room/{1}/notification'.format(hipchat_url, self.room)
        hipchat_room_list_url = '{0}/v2/room'.format(hipchat_url)

        if not self.listrooms:
            for record in records:
                message = None
                for key, value in record:
                    message = message.join('{0}={1} '.format(key, value))
                response = util.request(hipchat_room_url, data=data, headers=headers, timeout=timeout, proxy=proxy_conf)
                logger.info('sending notification room={0} status_code={1} response={2}'.format(self.room,
                                                                                                response['code'],
                                                                                                response['msg']))
                record['status_code'] = response['code']
                record['response'] = response['msg']
                record['_raw'] = util.tojson(response)
                yield record
        else:
            while hipchat_room_list_url:
                response = util.request(hipchat_room_list_url, headers=headers, timeout=timeout, proxy=proxy_conf)
                if response['code'] == 200:
                    room_list = json.loads(response['msg'])
                    hipchat_room_list_url = room_list['links']['next'] if 'next' in room_list['links'] else None
                    for room in room_list['items']:
                        room_info = dict()
                        room_info['room_id'] = room['id']
                        room_info['room_name'] = room['id']
                        room_info['_raw'] = util.tojson(room_info)
                        yield room_info
                else:
                    yield response
        exit()


dispatch(hipChatNotifyComand, sys.argv, sys.stdin, sys.stdout, __name__)