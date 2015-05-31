#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from modelos import *


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.set_status(301)
        self.response.headers.add('Location', 'http://posting.us.to/')


class UsuariosHandler(webapp2.RequestHandler):
    def get(self, uri):
        usuarios = Usuario.query().fetch()
        if (len(usuarios) > 0):
            self.response.headers['Content-Type'] = 'application/json'
            saida = JSONEncoder().encode(usuarios)
            self.response.write(saida)

    def post(self, arg):
        id = self.request.get('usuarioID')
        if id and (not Usuario.existe(id)):
            novo_usuario = Usuario(id=id, usuarioID=id,
                                   nome=self.request.get('nome'),
                                   email=self.request.get('email'))
            novo_usuario.put()
            self.response.set_status(201)
        else:
            self.response.set_status(400)


class UsuarioHandler(webapp2.RequestHandler):
    def get(self, id):
        usr = Usuario.get_by_id(id)
        if usr is None:
            self.response.set_status(404)
        else:
            self.response.headers['Content-Type'] = 'application/json'
            saida = JSONEncoder().encode(usr)
            self.response.write(saida)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/usuarios/((?!\s*$).+)', UsuarioHandler),
    ## para quando uri for na forma /usuarios/algumacoisa
    ('/usuarios(/?)$', UsuariosHandler)
    ##para quando uri for na forma /usuario ou /usuarios/
], debug=True)
