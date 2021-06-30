#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os,sys
import yaml,json
import logging
import argparse

from requests.packages.urllib3.exceptions import InsecureRequestWarning



requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ScriptItem(object):

  def __init__(self, script):
    self._script = script
    self.name = script['name']
    self.type = script['type']
    self.content = self.get_content()

    self.get_autostart()
    self.get_args()
    self.run = self.get_run()


  def get_args(self):
    self.args = {}
    if 'args' in self._script:
      self.args = bool(self._script['args'])

    return self.args


  def get_autostart(self):
    self.autostart = False
    if 'autostart' in self._script:
      self.autostart = bool(self._script['autostart'])

    return self.autostart


  def get_run(self):
    run = []
    if 'run' in self._script:
      run = self._script['run']

    return run


  def get_content(self):
    content = self._script['content']
    if content[0] == '@':
      with open(content[1:], 'r') as stream:
          #content = stream.read().replace('\n', '')
          content = stream.read()

    return content


  def get_dict(self):
    return {
        'name': self.name,
        'type': self.type,
        'content': self.content
      }



class Script(object):

  SUB_URL = "/service/rest/v1/script"


  def __init__(self, nexus, script, logger):
    self.logger = logger
    self.nexus  = nexus
    self.script = ScriptItem(script)


  def get_url(self):
    return self.nexus.url + self.SUB_URL



  def is_exists(self):
    url = '/'.join([self.get_url(), self.script.name])
    r = requests.get(
        url,
        auth=(self.nexus.username, self.nexus.password),
        verify=not self.nexus.insecure)
    return (r.status_code == 200)


  def update(self):
    self.logger.log(logging.DEBUG, "Update script '%s'" % self.script.name)
    url = '/'.join([self.get_url(), self.script.name])
    data = self.script.get_dict()
    r = requests.put(
        url,
        json = data,
        auth=(self.nexus.username, self.nexus.password),
        verify=not self.nexus.insecure)
    return (r.status_code == 204)


  def create(self):
    self.logger.log(logging.DEBUG, "Create script '%s'" % self.script.name)
    url = self.get_url()
    data = self.script.get_dict()
    r = requests.post(
        url,
        json = data,
        auth=(self.nexus.username, self.nexus.password),
        verify=not self.nexus.insecure)
    return (r.status_code == 204)


  def run(self, args={}):
    self.logger.log(logging.DEBUG, "Run script '%s' with args '%s'" %
        (self.script.name, args))
    url = '/'.join([self.get_url(), self.script.name, 'run'])
    r = requests.post(
        url,
        json = args,
        auth=(self.nexus.username, self.nexus.password),
      verify=not self.nexus.insecure)

    try:
      respData = r.json()
      if 'result' in respData:
        #self.logger.log(logging.DEBUG, respData['result'])
        self.logger.log(logging.DEBUG, respData)
    except e:
      self.logging.log(logging.DEBUG, e)

    return (r.status_code == 204)


  def apply(self):
    if self.is_exists():
      self.logger.log(logging.DEBUG, "Script '%s' exists" % self.script.name)
      self.update()
    else:
      self.create()

    if self.script.autostart:
      self.run(self.script.args)

    for run_params in self.script.run:
      self.run(run_params)



  def delete(self):
    self.logger.log(logging.DEBUG, "Delete script '%s'" % self.script.name)
    url = '/'.join([self.get_url(), self.script.name])
    r = requests.delete(
        url,
        auth=(self.nexus.username, self.nexus.password),
        verify=not self.nexus.insecure)
    return (r.status_code == 204)

########################################################################

class Security(object):

  SUB_URL = "/service/rest/v1/security"

  def __init__(self, nexus, security, logger):
    self.logger = logger
    self.nexus  = nexus

    self.anonymous = []
    if 'anonymous' in security:
      self.anonymous = security['anonymous']



  def get_url(self):
    return self.nexus.url + self.SUB_URL


  def apply_anonymous(self):
    sub_url_postfix = 'anonymous'
    for anonymous in self.anonymous:
      realmName =  anonymous['realmName']
      enabled =  anonymous['enabled']
      self.logger.log(logging.DEBUG, "Update security '%s' enabled=%s" %
          (realmName, enabled) )
      url = '/'.join([self.get_url(), sub_url_postfix])
      data = {
          'userId': 'anonymous',
          'enabled': enabled,
          'realmName': realmName
      }
      r = requests.put(
          url,
          json = data,
          auth=(self.nexus.username, self.nexus.password),
          verify=not self.nexus.insecure)
      #return (r.status_code == 204)


  def apply(self):
    self.apply_anonymous()

class NexusSettings(object):
  url = ''
  username = ''
  password = ''
  insecure = False


class NexusConfigurator(object):
    NC_CONFIG_NAME = "nc.yml"


    def __init__(self):
      self.verbose = logging.INFO
      #self.url      = os.environ['CONFIGURATOR_CONFIG_PATH']
      self.configure()


    def configure(self):
      self.nexus  = self.get_nexus_options()
      self.config = self.get_config()
      self.parse_args()
      self.set_logger()



    def get_nexus_options(self):
      nexus = NexusSettings()
      nexus.url      = os.environ['TF_VAR_nexus_url']
      nexus.username = os.environ['TF_VAR_nexus_username']
      nexus.password = os.environ['TF_VAR_nexus_password']
      nexus.insecure = bool(os.environ['TF_VAR_nexus_insecure'])

      return nexus


    def get_config(self):
      config = {}
      with open(self.NC_CONFIG_NAME, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            os.exit(1)

      return config


    def parse_args(self):
      parser = argparse.ArgumentParser(description='NexusConfigurator')

      parser.add_argument(
          "-v", "--verbose",
          help="increase output verbosity",
          action="store_true")

      #parser.add_argument('apply', metavar='N', type=int, nargs='+',
                          #help='action apply')
      parser.add_argument(
          'action',
          action='store',
          type=str,
          default='apply',
          choices=['apply', 'destroy'],
          help='action')

      args = parser.parse_args()

      self.action = args.action
      if args.verbose:
        self.verbose= logging.DEBUG


    def set_logger(self):
      self.logger = logging.getLogger()
      self.logger.setLevel(self.verbose)

      handler = logging.StreamHandler(sys.stdout)
      handler.setLevel(self.verbose)
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)
      self.logger.addHandler(handler)


    def apply(self):
      if "scripts" in self.config:
        for script in self.config['scripts']:
          script = Script(self.nexus, script, self.logger)
          script.apply()

      if 'security' in self.config:
        security = Security(self.nexus, self.config['security'], self.logger)
        security.apply()


    def destroy(self):
      if "scripts" in self.config:
        for script in self.config['scripts']:
          script = Script(self.nexus, script, self.logger)
          script.delete()



    def run(self):
      getattr(self, self.action)()



if __name__ == "__main__":
  nc = NexusConfigurator()
  nc.run()

