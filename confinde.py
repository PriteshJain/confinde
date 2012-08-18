#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Harshad Sharma. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import logging
from pprint import pprint

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from settings import *

from django.core.management import setup_environ
from djapp import settings

setup_environ(settings)

from djapp.database.models import Message, Keyword

class ConfindeBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)


    def session_start(self, event):
        self.send_presence()

        #Most get_*/set_* methods from plugins use Iq stanzas, which
        #can generate IqError and IqTimeout exceptions

        try:
            self.get_roster()
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            logging.error('Server is taking too long to respond')
            self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            #print dir(msg)
            user_from = str(msg.get_from()).split('/')[0]
            message = msg['body']

            response = self.process_message(user_from, message)

            msg.reply(response).send()

    def process_message(self, user_from, message):
        """Processes the message - and returns an appropriate text response."""
        if message[:2] == '/f':
            # find mode
            words = message[2:].replace(',',' ').strip().split(' ')
            response = ''
            rows = Message.get_by_search(email=user_from, words_to_match=words)
            
            for r in rows:
                response += r.text + '\n'

            return response

        else:
            Message.store(email=user_from, text=message)
            return "Ok."


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = ConfindeBot(BOT_USERNAME, BOT_PASSWORD)
    xmpp.connect(('talk.google.com',5222))
    xmpp.process(block=True)
