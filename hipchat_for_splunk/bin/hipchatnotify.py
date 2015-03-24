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

import requests
import base

headers = {'Accept': 'application/json', 'content-type': 'application/json'}
hipchat_url = None
auth_token = None
room_id = None
message = None
timeout = None
proxies = None
url = '{0}/v2/room/{1}/notification?auth_token={2}'.format(hipchat_url, room_id, auth_token)
data = {'message': message, 'message_format': 'text'}
hipchat_response = requests.post(url, headers=headers, data=base.tojson(data), timeout=timeout, proxies=proxies)

print hipchat_response.content
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
        require=True)

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

    def generate(self):
        logger = base.setup_logger(INFO)
        try:
            default_conf = base.getstanza('hipchat', 'default')
            conf = base.getstanza('hipchat', 'hipchatnotify')
            proxies = base.setproxy(conf, default_conf)
            hipchat_url = conf['url'] if 'url' in conf else default_conf['url']
            auth_token = conf['authToken'] if 'authToken' in conf else default_conf['autToken']
        finally:
            raise Exception("Unable to parse Config File. Check if hipchat.conf exists")

        headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        hipchat_url = '{0}/v2/room/{1}/notification?auth_token={2}'.format(hipchat_url, room_id, auth_token)
        hipchat_response = requests.post(url, headers=headers, data=base.tojson(data), timeout=timeout, proxies=proxies)

        pass
dispatch(hipChatNotifyComand, sys.argv, sys.stdin, sys.stdout, __name__)