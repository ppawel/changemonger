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

import psycopg2
import psycopg2.extras

import logging
from xml.dom.minidom import getDOMImplementation

domimpl = getDOMImplementation()

logging.basicConfig(level=logging.DEBUG)

try:
    dbconn = psycopg2.connect("dbname='osmdb' user='ppawel' host='localhost' password='aa'")
except:
    raise Exception("Unable to connect to the database")

dbcursor = dbconn.cursor(cursor_factory = psycopg2.extras.DictCursor)

def getNode(id, version = None):
    id = str(id)
    logging.debug("Retrieving node %s version %s" % (id, version))
    dbcursor.execute("SELECT * FROM nodes WHERE id = %s" % id)
    row = dbcursor.fetchone()
    print createNodeXml(row)
    return createNodeXml(row)

def getWay(id, version = None):
    id = str(id)
    if version:
        url = "http://%s/api/0.6/way/%s/%s" % (server, id, str(version))
    else:
        url = "http://%s/api/0.6/way/%s" % (server, id)
    logging.debug("Retrieving %s for way %s version %s" % (
        url, id, version))
    r = rs.get(url)
    r.raise_for_status()
    return r.text

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
    return r.text

def getChangeset(id):
    id = str(id)
    url = "http://%s/api/0.6/changeset/%s" % (server, id)
    logging.debug("Retrieving %s for changeset %s metadata" % (
        url, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.text

def getChange(id):
    id = str(id)
    url = "http://%s/api/0.6/changeset/%s/download" % (server, id)
    logging.debug("Retrieving %s for changeset %s data" % (
        url, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.text

def getWaysforNode(id):
    id = str(id)
    url = "http://%s/api/0.6/node/%s/ways" % (server, id)
    logging.debug("Retrieving %s for node %s ways" % (url, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.text

def getRelationsforElement(type, id):
    type = str(type)
    id = str(id)
    url = "http://%s/api/0.6/%s/%s/relations" % (server, type, id)
    logging.debug("Retrieving %s for %s %s relations" % (url, type, id))
    r = rs.get(url)
    r.raise_for_status()
    return r.text

## Caution: XML handling! Not pretty!

def createOsmDocument():
    return domimpl.createDocument(None, "osm", None)

def createNodeXml(node_row):
    newdoc = createOsmDocument()
    node_el = newdoc.createElement('node')
    node_el.setAttribute('id', str(node_row['id']))
    newdoc.documentElement.appendChild(node_el)
    return newdoc.toprettyxml()
