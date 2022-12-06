# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 15:43:21 2022

@author: kinjo
"""
import requests
import json

class Cryostat:
    
    def __init__(self,IP):
        self.IP=IP
        
        
    def cooldown(self):
        resp=requests.post(self.IP+'/v1/controller/methods/cooldown()')


    def warmup(self):
        resp = requests.post(self.IP+'/v1/controller/methods/warmup()')
        

    def terminate(self):
        resp = requests.post(self.IP+'/v1/controller/methods/abortGoal()')
        
    def pullVacuum(self):
        resp = requests.post(self.IP+'/v1/controller/methods/pullVacuum()')

    def getTemp(self):
        resp = requests.get(self.IP+'/v1/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        temp_list = json.loads(resp.content.decode('utf-8'))['sample']
        current_temp = temp_list['temperature']
        return current_temp

    def getTargetTemp(self):
        resp = requests.get(self.IP+'/v1/controller/properties/platformTargetTemperature')
        target = json.loads(resp.content.decode('utf-8'))['platformTargetTemperature']
        return target
    
    def setTargetTemp(self, target_temp):
        resp = requests.put(self.IP+'/v1/controller/properties/platformTargetTemperature', json=target_temp)