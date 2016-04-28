# coding:utf-8
'''
R-env(連舞)からV-Sidoでロボットを動かすサンプル

Copyright (c) 2015 Daisuke IMAI

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
'''
import os
import sys
import time
import json
import threading

import tornado.ioloop
import tornado.web
import tornado.websocket

state = {
    'robot_connected': False,
}


#ここからTornadeでのWeb/WebSocketサーバーに関する定義
class IndexHandler(tornado.web.RequestHandler):
    '''
    通常のHTTPリクエストで/が求められた時のハンドラ
    '''
    @tornado.web.asynchronous
    def get(self):
        self.render("server.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    '''
    WebSocketで/wsにアクセスが来た時のハンドラ

    on_message -> receive data
    write_message -> send data
    '''
    clients = set()

    def open(self):
        global state
        self.i = 0
        self.callback = tornado.ioloop.PeriodicCallback(self._send_message, 50)
        self.callback.start()
        print('WebSocket opened')
        self.clients.add(self)
        if state['robot_connected']:
            self.write_message(json.dumps({'message': 'robot_connected'}))
        else:
            self.write_message(json.dumps({'message': 'robot_disconnected'}))

    def check_origin(self, origin):
        ''' アクセス元チェックをしないように上書き '''
        return True

    def on_message(self, message):
        global state

        received_data = json.loads(message)
        print('got message:', received_data['command'])
        if received_data['command'] == 'robot_connected':
            for client in self.waiters:
                if client == self:
                    continue
                client.write_message(json.dumps({'message': 'robot_connected'}))
            state['robot_connected'] = True
        elif received_data['command'] == 'robot_disconnected':
            for client in self.waiters:
                if client == self:
                    continue
                client.write_message(json.dumps({'message': 'robot_disconnected'}))
            state['robot_connected'] = False
        elif received_data['command'] == 'arrival_alert':
            for client in self.waiters:
                if client == self:
                    continue
                client.write_message(json.dumps({'message': 'arrival_alert'}))
        elif received_data['command'] == 'alert_reset':
            for client in self.waiters:
                if client == self:
                    continue
                client.write_message(json.dumps({'message': 'alert_reset'}))

    def _send_message(self):
        pass
#        if len(vsidoconnect.message_buffer) > 0:
#            self.write_message(vsidoconnect.message_buffer.pop(0))

    def on_close(self):
        self.clients.remove(self)
        print('WebSocket closed')


if __name__ == '__main__':

    # アプリケーション割り当て
    web_application = tornado.web.Application(
        [
            (r'/', IndexHandler),
            (r'/ws', WebSocketHandler),
        ],
        template_path=os.path.join(os.getcwd(),  'templates'),
        static_path=os.path.join(os.getcwd(),  'assets'),
    )

    # Tornadoサーバー起動
    print('Starting Web/WebSocket Server...', end='')
    web_application.listen(8880)
    print('done')

    print('Open http://localhost:8880/')
    print('')

    tornado.ioloop.IOLoop.instance().start()
