#! /usr/bin/env python3
#Importing the libraries
# This program is to clone Image manager policies from one Policy Set to another polocy set. For any feedback and concerns reach to hmallika@akamai.com
# IMP: Update below parameters before running this program
#1. Line 39 . Update the Source IM Policy set or API key name
#2. Line 40 . Update the Destination IM Policy set or API key name
#3. Line 41: Save all IM policy names that needs to be cloned from source to destination in a text file (one entry in each line), in this case policy_list_to_clone.txt and keep it in same directory
#4. You should have API Read/Write access to Image Manager and credential file .edgerc is stored in home dir.
#5. Cloned IM policy automaticallay activates to Akamai staging or production, activation environment is decided by the host entry in edgerc file
#   Eg:  host = akab-iyvy5asdasdqwo7aft-nlprmiz7yv6h6kbk.imaging.akamaiapis-staging.net --> for cloning followed by activation to staging
#   Eg:  host = akab-iyvy5asdasdqwo7aft-nlprmiz7yv6h6kbk.imaging.akamaiapis.net --> for cloning followed by activation to prod

import requests
import json
from akamai.edgegrid import EdgeGridAuth
from urllib.parse import urljoin
from config import EdgeGridConfig
import sys
from http_calls import EdgeGridHttpCaller

section_name = "default"
config = EdgeGridConfig({},section_name)
s = requests.Session()
debug = False
verbose = False
s.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

if hasattr(config, "debug") and config.debug:
  debug = True

if hasattr(config, "verbose") and config.verbose:
  verbose = True

baseurl = '%s://%s/' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(s, debug, verbose, baseurl)

ct_headers = {"content-type": "application/json"}
luna_apitoken_header_source = {"Luna-Token": "images_menswearhouse_com_pm-10816058"}
luna_apitoken_header_dest = {"Luna-Token": "images_josbank_com_pm-10816149", "content-type": "application/json"}
with open("policy_list_to_clone.txt", "r") as im_policy_list_file:
  for policy_name in im_policy_list_file:
      apiurl = '/imaging/v2/policies/'+policy_name
      print("\n")
      print("getting policy from source:" + policy_name.rstrip())
      query_result_get=s.get(urljoin(baseurl,'%s' % apiurl.rstrip()), headers=luna_apitoken_header_source)
      if (query_result_get.status_code == 200):
          dest_query_result_get=s.get(urljoin(baseurl,'%s' % apiurl.rstrip()), headers=luna_apitoken_header_dest)
          if (dest_query_result_get.status_code == 200):
              dest_query_result_delete=s.delete(urljoin(baseurl,'%s' % apiurl.rstrip()), headers=luna_apitoken_header_dest)
              if (dest_query_result_delete.status_code == 200):
                  print("deleting policy at dest:" + policy_name.rstrip())
          print("creating policy at dest:" + policy_name.rstrip())
          query_result_get_json = json.dumps(query_result_get.text)
          query_result_get_json_2 = json.loads(query_result_get_json)
          query_result_put=s.put(urljoin(baseurl,'%s' % apiurl.rstrip()),data=query_result_get_json_2, headers=luna_apitoken_header_dest)
          if query_result_put.status_code == 200 or query_result_put.status_code == 201:
              print("success creating policy at dest:" + policy_name.rstrip() + "--" + query_result_put.text)
          else:
              print(query_result_put.status_code)
              print("error cloning policy at dest:" + policy_name.rstrip() + "--" + query_result_put.text)
      else:
          print("error getting policy from sorce:" + policy_name.rstrip() + "--" + query_result_get.text)
