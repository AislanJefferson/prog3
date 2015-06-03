#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    """Classe manipuladora das requisicoes na raiz do dominio api.posting.us.to"""

    def get(self):
        """Metodo que redireciona para a pagina web do projeto"""
        self.response.set_status(301)
        self.response.headers.add('Location', 'http://posting.us.to/')


class UsuariosHandler(webapp2.RequestHandler):
    """Classe manipuladora de requisicoes para a COLECAO de usuario"""

    def get(self, arg):
        """Metodo de consulta de dados todos usuarios em uma unica requisicao"""
        usuarios = Usuario.query().fetch()
        if (len(usuarios) > 0):
            self.response.headers['Content-Type'] = 'application/json'
            saida = JSONEncoder().encode(usuarios)
            self.response.write(saida)

    def post(self, arg):
        """Metodo de criacao de um novo usuario

        Parametros recebidos (Case Sensitive) via post:
        usuarioID: O id unico e textual(pode ser numero) do usuario a ser criado
        nome: Nome de exibicao do usuario
        email: o email vinculado a ele ( pode haver o mesmo para varias contas )"""
        id = self.request.get('usuarioID')
        if id and (not Usuario.existe(id)):
            novo_usuario = Usuario(id=id, usuarioID=id,
                                   nome=self.request.get('nome'),
                                   email=self.request.get('email'))
            novo_usuario.put()
            self.response.set_status(201)
        elif id:
            self.response.set_status(409)
        else:
            self.response.set_status(404)


class UsuarioHandler(webapp2.RequestHandler):
    """Classe manipuladora de requisicoes para um unico usuario"""

    def get(self, id):
        usr = Usuario.get_by_id(id)
        if usr is None:
            self.response.set_status(404)
        else:
            self.response.headers['Content-Type'] = 'application/json'
            saida = JSONEncoder().encode(usr)
            self.response.write(saida)

    def put(self, id):

        """Metodo de atualizacao de dados de um usuario

            Parametros que podem ser recebidos (Case Sensitive) via put:
            nome: Nome de exibicao do usuario
            email: o email vinculado a ele ( pode haver o mesmo para varias contas )"""

        usr = Usuario.get_by_id(id)
        args_recebidos = self.request.arguments()
        if usr is None:
            self.response.set_status(404)
        elif len(args_recebidos) > 0:
            for arg in args_recebidos:
                if (arg != 'usuarioID' and arg != 'id'):
                    usr.__setattr__(arg, self.request.get(arg))
            usr.put()
            self.response.set_status(204)


def delete(self, id):
    """Metodo que remove usuario e seus posts existentes.
    Ele envia um status 400, caso nao exista tal usuario a ser deletado

    Parametros recebidos via DELETE:
    Nenhum! Ele usa o conteudo <id> do  api.posting.us.to/usuarios/<id> como id
    """
    usr = Usuario.get_by_id(id)
    if usr is not None:
        for post in usr.posts:
            post.delete()
        usr.key.delete()
        self.response.set_status(200)
    else:
        self.response.set_status(404)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/usuarios/((?!\s*$).+)', UsuarioHandler),
    ('/usuarios(/?)$', UsuariosHandler)
], debug=True)
