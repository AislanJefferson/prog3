__author__ = 'Aislan'

from datetime import datetime, date, time
import json

from google.appengine.ext import ndb


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ndb.Key):
            return str(o.id())
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return str(o)


class Post(ndb.Model):
    conteudo = ndb.StringProperty()
    dt_postado = ndb.DateTimeProperty(auto_now_add=True)
    dt_modificado = ndb.DateTimeProperty(auto_now=True)


class Usuario(ndb.Model):
    nome = ndb.StringProperty()
    usuarioID = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    data_cadastro = ndb.DateProperty(auto_now_add=True)
    posts = ndb.KeyProperty(kind=Post, repeated=True)

    @staticmethod
    def existe(id):
        try:
            existe = False
            if Usuario.get_by_id(id):
                existe = True
            return existe
        except:
            raise Exception('Nao foi possivel conectar ao datastore')
