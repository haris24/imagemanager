#! /usr/bin/env python3
#Importing the libraries
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

#query_result=s.post(urljoin(baseurl,'%s' % delete_rule_path))
ct_headers = {"content-type": "application/json"}
luna_apitoken_header_source = {"Luna-Token": "images_menswearhouse_com_pm-10816058"}
luna_apitoken_header_dest = {"Luna-Token": "images_menswearhouse_com_pm-10816058", "content-type": "application/json"}
with open("im_policy_list_file", "r") as im_policy_list_file:
  for policy_name_ in im_policy_list_file:
      policy_name = policy_name_.rstrip()
      apiurl = '/imaging/v2/policies/'+policy_name
      print("\n")
      print("getting policy from source:" + policy_name)
      query_result_get=s.get(urljoin(baseurl,'%s' % apiurl ), headers=luna_apitoken_header_source)
      if (query_result_get.status_code == 200):
          add_unsharp_mask = "yes"
          add_perceptualQuality = "no"
          query_result_get_loads = json.loads(query_result_get.text)
          query_result_get_loads = json.loads(query_result_get.text)
          query_result_get_loads_new = json.loads(query_result_get.text)
          if query_result_get_loads["output"]:
              if(query_result_get_loads["output"]["perceptualQuality"] != "mediumHigh"):
                  add_perceptualQuality = "yes"
                  print("changing quality to mediumHigh")
                  query_result_get_loads_new["output"]["perceptualQuality"] = "mediumHigh"
          else:
              add_perceptualQuality = "yes"
              print("setting quality to mediumHigh")
              query_result_get_loads_new["output"]= {'perceptualQuality': 'mediumHigh'}
          if 'transformations' not in query_result_get_loads:
              print("adding transformations : Unsharp ")
              query_result_get_loads_new["transformations"]= [{'transformation': 'UnsharpMask', 'sigma': 1, 'gain': 1, 'threshold': 0.05}]
          else:
              for i in query_result_get_loads["transformations"]:
                  if i["transformation"] == "UnsharpMask":
                      add_unsharp_mask = "no"
              if add_unsharp_mask == "yes":
                  query_result_get_loads_new["transformations"].append({'transformation': 'UnsharpMask', 'sigma': 1, 'gain': 1, 'threshold': 0.05})
                  print("adding Unsharp to transformations")
          if add_unsharp_mask == "yes" or add_perceptualQuality == "yes":
              query_result_get_loads_new_2  = json.dumps(query_result_get_loads_new)
              query_result_put=s.put(urljoin(baseurl,'%s' % apiurl),data=query_result_get_loads_new_2, headers=luna_apitoken_header_dest)
              if query_result_put.status_code == 200 or query_result_put.status_code == 201:
                  print("success updating policy at dest:" + policy_name + "--" + query_result_put.text)
              else:
                  print(query_result_put.status_code)
                  print("error updating policy :" + policy_name + "--" + query_result_put.text)
      else:
          print("error getting policy :" + policy_name + "--" + query_result_get.text)
