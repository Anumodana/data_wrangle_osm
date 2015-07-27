# -*- coding: utf-8 -*-

# Note: Please make sure that you have unzipped the
# data/chiang-mai_thailand.osm.zip file before running this.

import xml.etree.cElementTree as ET
import re
import codecs
import json

CREATED = ["version", "changeset", "timestamp", "user", "uid"]
ADDRESS = ["addr:housenumber", "addr:postcode", "addr:street", "addr:city", "addr:district", "addr:province", "addr:subdistrict"]
GENERAL = ["amenity", "shop", "tourism", "name", "name:en"]

STREETNAME_MAPPING = { "Rd": "Road", "Rd.": "Road" }

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        row = element.attrib
        add_type(element.tag, node)
        add_id(row["id"], node)
        add_created(CREATED, row, node)
        add_pos(row, node)
        add_general_info(GENERAL, element, node)
        add_address(ADDRESS, element, node)
        add_node_refs(element, node)

        return node
    else:
        return None

def add_type(row_type, node):
    node["type"] = row_type

def add_id(row_id, node):
    node["id"] = row_id

def add_created(fields, record, node):
    node["created"] = {}
    keys = record.keys()
    for field in fields:
        if field in keys:
            node["created"][field] = record[field]
        else:
            node["created"][field] = None

def add_address(fields, record, node):
    row = {}
    for attr in record.iter("tag"):
        if attr.attrib["k"] in fields:
            row[attr.attrib["k"].split(":")[1]] = attr.attrib["v"]

    if row: node["address"] = row

def add_general_info(fields, record, node):
    for attr in record.iter("tag"):
        if attr.attrib["k"] in fields:
            node[attr.attrib["k"]] = attr.attrib["v"]

def add_node_refs(record, node):
    refs = [attr.attrib["ref"] for attr in record.iter("nd")]
    if refs: node["node_refs"] = refs

def add_pos(row, node):
    if set(["lat", "lon"]) <= set(row.keys()):
        node["loc"] = { "type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])] }

def audit_default_name(row):
    fields = row.keys()
    if (not has_default_name(fields)) and has_english_name(fields):
        row["name"] = row["name:en"]

def has_default_name(fields):
    return ("name" in fields)

def has_english_name(fields):
    return ("name:en" in fields)

def audit_streetname(row):
    if "address" in row.keys() and "street" in row["address"].keys():
        for k, v in STREETNAME_MAPPING.iteritems():
            row["address"]["street"] = re.sub(" "+k+"(\.?)", " "+v, row["address"]["street"])

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                audit_default_name(el)
                audit_streetname(el)
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

if __name__ == "__main__":
    process_map("data/chiang-mai_thailand.osm")