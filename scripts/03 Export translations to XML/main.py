#!/usr/bin/env python3
# Note: pip install requests
import json, requests
import xml.etree.cElementTree as ET
import xml.dom.minidom
from io import BytesIO

# == Settings ==
# Authentication
API_USERNAME = argv[1] or os.environ.get('C4_USER', '')
API_PASSWORD = argv[2] or os.environ.get('C4_PASS', '')
# API root URI
API_URL_BASE = 'https://test.metering.space/api/'
# API call origin and referer
ORIGIN = API_URL_BASE
# ==============

class ConvergeSession:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json',
                        'Referer': ORIGIN,
                        'Origin': ORIGIN}

    def Login(self, username, password):
        content = {'userName': username, 'password': password}
        response = requests.post(self.base_url + 'login/user-login', headers=self.headers, json=content)
        if response.status_code != 200:
            raise Exception("Authentication has failed.")
        self.headers['Authorization'] = 'Bearer %s' % json.loads(response.content.decode('utf-8'))['token']

class Main(ConvergeSession):
    def __init__(self, *args, **kwagrs):
        super().__init__(*args, **kwagrs)

    def GetLanguages(self):
        response = requests.get(self.base_url + 'locale/list', headers=self.headers, json={})
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % (response.status_code,))
        return json.loads(response.content.decode('utf-8'))

    def GetTranslations(self, ietf_code):
        response = requests.get(self.base_url + 'locale/' + ietf_code, headers=self.headers, json={})
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % (response.status_code,))
        return json.loads(response.content.decode('utf-8'))

    def CreateMenuItem(self, xml, record):
        attrib = {
            'item': record['key'].split('.')[-1],
            'type': record['type'],
        }

        if '.' in record['key']:
            attrib['parent'] = record['key'].split('.')[-2]

        if record['permission']:
            attrib['permission'] = record['permission']

        if record['icon']:
            attrib['icon'] = record['icon']

        doc = ET.SubElement(xml, "menuitem", attrib=attrib)

        return doc

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)

    # Call a method: Get and show meter data
    languages = session.GetLanguages()

    root = ET.Element("translations")
    for lang in languages:
        translations = session.GetTranslations(lang['ietf'])
        if not translations:
            continue

        xml_language = ET.SubElement(root, "language", attrib={'ietf': lang['ietf']})

        element_cache = {}
        for tag in translations.keys():
            if tag.endswith('$tooltip'):
                cache_key = tag[:-8]
                element_name = 'tooltip'
            else:
                cache_key = tag
                element_name = 'text'

            if cache_key in element_cache:
                xml_translation = element_cache[cache_key]
            else:
                xml_translation = element_cache[cache_key] = ET.SubElement(xml_language, "translation", attrib={'tag': tag})

            ET.SubElement(xml_translation, element_name).text = translations[tag]

    # Generate output XML
    f = BytesIO()
    tree = ET.ElementTree(root)
    tree.write(f, encoding="utf-8", xml_declaration=True)
    with open("exported - translations.xml", 'wt') as fo:
        f.seek(0)
        xml.dom.minidom.parse(f).writexml(fo, addindent="    ", newl="\n")
