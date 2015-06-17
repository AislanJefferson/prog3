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
from Utils import *


class MainHandler(webapp2.RequestHandler):
    """Classe manipuladora das requisicoes na raiz do dominio api.posting.us.to"""

    def get(self):
        """Metodo que redireciona para a pagina web do projeto"""
        self.response.set_status(301)
        self.response.headers.add('Location', 'http://posting.us.to/')


class UsuariosHandler(webapp2.RequestHandler):
    """Classe manipuladora de requisicoes para a COLECAO de usuario"""

    def get(self):
        """Metodo de consulta de dados todos usuarios em uma unica requisicao"""
        try:
            curs = ndb.Cursor(urlsafe=self.request.get('hash'))
            qtde = int(self.request.get('qtde')) if self.request.get(
                'qtde') else 20
        except:
            curs = ndb.Cursor(urlsafe='')
            self.request.GET.pop('qtde')
            qtde = 20
        qry = Usuario.query().order(Usuario.usuarioID)
        usuarios, prox_cursor, mais = qry.fetch_page(qtde, start_cursor=curs)
        if (len(usuarios) > 0):
            urlAtual = insert_URL_Params(get_URL_Atual(self), self.request.GET)
            proxima_url = insert_URL_Params(urlAtual, {
                'hash': prox_cursor.urlsafe()}) if mais else None
            users_wrapper = JsonDataWrapper(atual_URL=urlAtual,
                                            proxima_URL=proxima_url,
                                            data=usuarios)
            self.response.content_type = 'application/json'

            self.response.cache_control = 'public'
            self.response.cache_control.max_age = 1

            saida = JSONEncoder().encode(users_wrapper)
            self.response.write(saida)

    def post(self):
        """Metodo de criacao de um novo usuario

        Parametros recebidos (Case Sensitive) via post:
        usuarioID: O id unico e textual(pode ser numero) do usuario a ser criado
        nome: Nome de exibicao do usuario
        email: o email vinculado a ele ( pode haver o mesmo para varias contas )"""
        if (self.request.content_type == 'application/json'):
            campos = json.loads(self.request.body)
            id = campos['usuarioID'] if campos.has_key('usuarioID') else ''
            if id and (not Usuario.existe(id)):
                novo_usuario = Usuario(id=id, usuarioID=id,
                                       nome=campos['nome'] if campos.has_key(
                                           'nome') else '',
                                       email=campos['email'] if campos.has_key(
                                           'email') else '')
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
            self.response.content_type = 'application/json'
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = 1
            usr_wrapper = JsonDataWrapper(atual_URL=get_URL_Atual(self),
                                          data=usr)
            saida = JSONEncoder().encode(usr_wrapper)
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


class PostsHandler(webapp2.RequestHandler):
    def get(self, *args):
        usuarioID = args[0]
        usr = Usuario.get_by_id(usuarioID)
        if usr is not None and len(usr.posts) > 0:
            try:
                curs = ndb.Cursor(urlsafe=self.request.get('hash'))
                qtde = int(self.request.get('qtde')) if self.request.get(
                    'qtde') else 20
            except:
                curs = ndb.Cursor(urlsafe='')
                self.request.GET.pop('qtde')
                qtde = 20
            qry = Post.query(ancestor=usr.key).order(-Post.dt_postado)
            posts, prox_cursor, mais = qry.fetch_page(qtde, start_cursor=curs)
            urlAtual = insert_URL_Params(get_URL_Atual(self), self.request.GET)
            proximaURL = insert_URL_Params(urlAtual, {
                'hash': prox_cursor.urlsafe()}) if mais else None
            posts_wrapper = JsonDataWrapper(atual_URL=urlAtual,
                                            proxima_URL=proximaURL,
                                            data=posts)
            json_str = JSONEncoder().encode(posts_wrapper)
            self.response.content_type = 'application/json'
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = 1
            self.response.write(json_str)
        else:
            self.response.set_status(404)

    def post(self, *args):
        campos = json.loads(self.request.body)
        usuarioID = args[0]
        conteudo = campos['conteudo'] if campos.has_key('conteudo') else ''
        usr = Usuario.get_by_id(usuarioID)
        if conteudo and usr is not None:
            post = Post(conteudo=conteudo, parent=usr.key)
            post_key = post.put()
            post.id = str(post_key.id())
            post.url = get_URL_Atual(self) + '/' + str(
                post.id)
            post.put()
            usr.posts.append(post_key)
            usr.put()
        else:
            self.response.set_status(404)


class PostHandler(webapp2.RequestHandler):
    def get(self, *args):

        usuarioID = args[0]
        postID = args[1]
        usr = Usuario.get_by_id(usuarioID)
        key = ndb.Key(Post, int(postID), parent=usr.key)
        post = key.get()
        if usr is not None and post is not None:
            self.response.content_type = 'application/json'
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = 1
            post_wrapper = JsonDataWrapper(atual_URL=get_URL_Atual(self),
                                           data=post)
            saida = JSONEncoder().encode(post_wrapper)
            self.response.write(saida)
        else:
            self.response.set_status(404)

    def put(self, *args):
        pass

    def delete(self, *args):
        usuarioID = args[0]
        postID = args[1]
        usr = Usuario.get_by_id(usuarioID)
        post = Post.get_by_id(int(postID))
        if usr is not None and post is not None and post.key in usr.posts:
            usr.posts.remove(post.key)
            post.key.delete()
            usr.put()
        else:
            self.response.set_status(404)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/usuarios/((?!\s*$).+)/posts/((?!\s*$).+)', PostHandler),
    ('/usuarios/((?!\s*$).+)/posts$', PostsHandler),
    ('/usuarios/((?!\s*$).+)', UsuarioHandler),
    ('/usuarios$', UsuariosHandler)

], debug=True)
