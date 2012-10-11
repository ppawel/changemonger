##  Changemonger: An OpenStreetMap change analyzer
##  Copyright (C) 2012 Serge Wroclawski
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as
##  published by the Free Software Foundation, either version 3 of the
##  License, or (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provides a simple abstraction against the OSM API"""
"""Operations are implemented using PostGIS snapshot schema database instead of public API calls"""

import os.path
import sys

import psycopg2
import psycopg2.extensions
import psycopg2.extras

import requests
import requests_cache

rs = requests.session(headers={'user-agent': 'changemonger/0.0.1'})
requests_cache.configure('osm_cache')

server = 'api.openstreetmap.org'

import logging
from xml.dom.minidom import getDOMImplementation

domimpl = getDOMImplementation()

logging.basicConfig(level=logging.DEBUG)

try:
    dbconn = psycopg2.connect("dbname='osmdb' user='ppawel' host='localhost' password='aa'")
except:
    raise Exception("Unable to connect to the database")

dbcursor = dbconn.cursor(cursor_factory = psycopg2.extras.DictCursor)
# This will enable automatic hstore column -> dict conversion which is nice for columns with tags.
psycopg2.extras.register_hstore(dbcursor, unicode = True)
# Fix some unicode madness...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

def getNode(id, version = None):
    id = str(id)
    logging.debug("Retrieving node %s version %s" % (id, version))
    dbcursor.execute("SELECT * FROM nodes WHERE id = %s" % id)
    row = dbcursor.fetchone()
    return createNodeXml(row)

def getWay(id, version = None):
    id = str(id)
    logging.debug("Retrieving way %s version %s" % (id, version))
    dbcursor.execute("SELECT * FROM ways w INNER JOIN way_nodes wn ON (wn.way_id = w.id) WHERE w.id = %s" % id)
    rows = dbcursor.fetchall()
    return createWayXml(rows)

def getRelation(id, version = None):
    id = str(id)
    if version:
        url = "http://%s/api/0.6/relation/%s/%s" % (server, id, str(version))
    else:
        url = "http://%s/api/0.6/relation/%s" % (server, id)
    logging.debug("Retrieving %s for relation %s version %s" % (
        url, id, version))
    r = rs.get(url)
    r.raise_for_status()
    return r.content

def getChangeset(id):
    id = str(id)
    url = "http://%s/api/0.6/changeset/%s" % (server, id)
    logging.debug("Retrieving %s for changeset %s metadata" % (
        url, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.content

def getChange(id):
    return open(sys.argv[1]).read()

def getWaysforNode(id):
    id = str(id)
    logging.debug("Retrieving node %s version %s ways" % (id, version))
    dbcursor.execute("SELECT * FROM ways w INNER JOIN way_nodes wn ON (wn.way_id = w.id) WHERE wn.node_id = %s ORDER BY w.id" % id)
    rows = dbcursor.fetchall()
    return createWayXml(rows)

def getRelationsforElement(type, id):
    type = str(type)
    id = str(id)
    url = "http://%s/api/0.6/%s/%s/relations" % (server, type, id)
    logging.debug("Retrieving %s for %s %s relations" % (url, type, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.content

## Caution: XML handling! Not pretty!

def createOsmDocument():
    return domimpl.createDocument(None, "osm", None)

def createNodeXml(node_row):
    newdoc = createOsmDocument()
    node_el = newdoc.createElement('node')
    node_el.setAttribute('id', str(node_row['id']))

    for k, v in node_row['tags'].items():
        tag_el = newdoc.createElement('tag')
        tag_el.setAttribute('k', k)
        tag_el.setAttribute('v', v)
        node_el.appendChild(tag_el)

    newdoc.documentElement.appendChild(node_el)
    return newdoc.toprettyxml(encoding = 'utf-8')

def createWayXml(way_rows):
    newdoc = createOsmDocument()
    appendWayXml(newdoc.documentElement, way_rows)
    return newdoc.toprettyxml(encoding = 'utf-8')

def createNodeWaysXml(way_rows):
    newdoc = createOsmDocument()
    appendWayXml(newdoc.documentElement, way_rows)
    return newdoc.toprettyxml(encoding = 'utf-8')

def appendWayXml(el, way_rows):
    way_el = newdoc.createElement('way')
    way_el.setAttribute('id', str(way_rows[0]['id']))

    for node in way_rows:
        node_el = newdoc.createElement('nd')
        node_el.setAttribute('ref', str(node['id']))
        way_el.appendChild(node_el)

    for k, v in way_rows[0]['tags'].items():
        tag_el = newdoc.createElement('tag')
        tag_el.setAttribute('k', k)
        tag_el.setAttribute('v', v)
        way_el.appendChild(tag_el)

    el.appendChild(way_el)
    return newdoc.toprettyxml(encoding = 'utf-8')
