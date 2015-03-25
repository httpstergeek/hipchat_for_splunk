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

import os
import sys
import json
from platform import system
from logging import INFO
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option

# discovering platform
platform = system().lower()
if platform == 'darwin':
    platform = 'macosx'

# Loading eggs into python execution path
running_dir = os.path.dirname(os.path.realpath(__file__))
egg_dir = os.path.join(running_dir, 'eggs')
for filename in os.listdir(egg_dir):
    file_segments = filename.split('-')
    if filename.endswith('.egg'):
        filename = os.path.join(egg_dir, filename)
        if len(file_segments) <= 3:
            sys.path.append(filename)
        else:
            if platform in filename:
                sys.path.append(filename)

import base


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
        logger = base.setup_logger(INFO)
        try:
            default_conf = base.getstanza('hipchat', 'default')
            local_conf = base.getstanza('hipchat', 'hipchat')
            proxy_conf = base.setproxy(local_conf, default_conf)
            hipchat_url = local_conf['url'] if 'url' in local_conf else default_conf['url']
            auth_token = local_conf['authToken'] if 'authToken' in local_conf  else default_conf['autToken']
            timeout = local_conf['timeout'] if 'timeout' in  local_conf  else default_conf['timeout']

            print
        finally:
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
                response = base.request(hipchat_room_url, data=data, headers=headers, timeout=timeout, proxy=proxy_conf)
                record['status_code'] = response['code']
                record['response'] = response['msg']
                record['_raw'] = base.tojson(response)
                yield record
        else:
            while hipchat_room_list_url:
                response = base.request(hipchat_room_list_url, headers=headers, timeout=timeout, proxy=proxy_conf)
                if response['code'] == 200:
                    room_list = json.loads(response['msg'])
                    hipchat_room_list_url = room_list['links']['next'] if 'next' in room_list['links'] else None
                    for room in room_list['items']:
                        room_info = dict()
                        room_info['room_id'] = room['id']
                        room_info['room_name'] = room['id']
                        room_info['_raw'] = base.tojson(room_info)
                        yield room_info
                else:
                    yield response
        exit()


dispatch(hipChatNotifyComand, sys.argv, sys.stdin, sys.stdout, __name__)