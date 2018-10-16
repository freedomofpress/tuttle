#!/usr/bin/env python3

import sqlite3
import textwrap

import dominate

from dominate.tags import *
from dominate.util import raw
from logincoming import SignalMessage

from settings import NUMBER, database

def main():
    conn = sqlite3.connect(database)

    collist = "rowid, source, recipient, groupID, message, attachments, datetime(timestamp, 'localtime')"

    msgdb = conn.execute('select {} from messages'.format(collist)).fetchall()
    messages = []

    for msg in msgdb:
        sigmsg = SignalMessage(msg[6], msg[1], msg[2], msg[3], \
                               msg[4], msg[5], msg[0])
        messages.append(sigmsg)

    numbers = []

    for msg in reversed(messages):
        if msg.source == NUMBER and msg.recipient not in numbers:
            numbers.append(msg.recipient)
        elif msg.source != NUMBER and msg.source not in numbers:
            numbers.append(msg.source)

    h = dominate.document()
    h.title = 'tipline tips'

    with h.head:
        link(rel="stylesheet", href="/style.css")

    body = h.add(div(id='body'))

    body.add(h1("tipline messages"))

    if numbers:
        contactlist = body.add(ul())
    else:
        body.add('No messages to display.')

    for num in numbers:
        msgs = [msg for msg in messages if 
                msg.source == num or msg.recipient == num]

        thread = contactlist.add(li())

        delete_button = '❌'

        thread_delete = form(method='post', cls='delete-thread')

        delete_thread_button = button(raw(delete_button), cls='delete-button',
                                title='delete entire thread',
                                name='delete-thread', type='submit',
                                value=num)

        thread_delete.add(delete_thread_button)

        thread.add(div(thread_delete, h2('messages with {}'.format(num)),
                       cls='thread-header', __pretty=False))

        with thread.add(ul()):
            for msg in msgs:
                if msg.source == num:
                    msg_text = msg.message
                    msg_class = 'tip'
                    sayswho = span('They said: ', cls='sr-only')
                else:
                    msg_text = msg.message
                    msg_class = 'reply'
                    sayswho = span('You said: ', cls='sr-only')

                if msg.timestamp:
                    sent_at = span(msg.timestamp, cls='timestamp')
                else:
                    sent_at = ''

                attachment_indicator = '📎&#xFE0E;'

                if msg.attachments:
                    has_attachments = span(a(raw(attachment_indicator),
                        href='attachments/' + msg.attachments,
                        target='_blank'), cls='attachment')
                else:
                    has_attachments = ''

                msg_delete = form(method='post', cls='delete-msg')

                delete_msg_button = button(raw(delete_button),
                                  cls='delete-button', title="delete message",
                                  name='delete-msg', type='submit', 
                                  value=msg.rowid)

                msg_delete.add(delete_msg_button)

                li(msg_delete, sayswho, msg_text, sent_at, has_attachments,
                    cls=msg_class, __pretty=False)

        with thread.add(form(method='post', cls='reply-form')).add(p()):
            label('Send a message to {}'.format(num), fr='message',
                    cls='sr-only')
            input_(type='textarea', name='message', id='message',
                    placeholder='Message to {}'.format(num))
            input_(type='hidden', name='recipient', id='recipient',
                    value=num)
            input_(type='submit', value='Reply')

    return h.render()

if __name__ == '__main__':
    main()
