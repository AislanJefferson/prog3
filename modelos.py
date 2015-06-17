# -*- coding: utf-8 -*-
__author__ = 'Aislan'

from datetime import datetime, date, time
import json

from google.appengine.ext import ndb


class JSONEncoder(json.JSONEncoder):
    """Classe de transformacao de elementos do datastore para JSON
    """

    def default(self, o):
        """Metodo que sobrescreve o da classe pai JSONEncoder para adequar
        os metodos da classe pai para elementos do datastore"""
        if isinstance(o, ndb.Key):
            o = o.get()
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return str(o.isoformat())
        elif o is not None and isinstance(o, object):
            return o.__dict__


class JsonDataWrapper():
    def __init__(self, atual_URL=None, proxima_URL=None, data=None):
        self.links = {'self': atual_URL, 'next': proxima_URL}
        self.data = data


class Post(ndb.Model):
    """Classe de modelagem para o datastore de um Post
    """
    # FIXME: Modelagem incompleta ou fraca
    conteudo = ndb.StringProperty()
    id = ndb.StringProperty()
    url = ndb.StringProperty()
    dt_postado = ndb.DateTimeProperty(auto_now_add=True)
    dt_modificado = ndb.DateTimeProperty(auto_now=True)


class Usuario(ndb.Model):
    """Classe de modelagem para o datastore de um usuario"""
    # FIXME: Aperfeicoar mais este modelo
    nome = ndb.StringProperty()
    usuarioID = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    data_cadastro = ndb.DateProperty(auto_now_add=True)
    posts = ndb.KeyProperty(kind=Post, repeated=True)

    @staticmethod
    def existe(id):
        """Metodo estatico(da classe) utilizado para verificar se existe alguma
         entidade com um respectivo ID salvada no datastore """
        try:
            existe = False
            if Usuario.get_by_id(id):
                existe = True
            return existe
        except:
            raise Exception('Nao foi possivel conectar ao datastore')
