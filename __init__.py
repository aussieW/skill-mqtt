import time

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from urllib2 import urlopen
import paho.mqtt.client as mqtt

__author__ = 'jamiehoward430'

LOGGER = getLogger(__name__)

dataRequestTopic = 'send/#'
actionConfirmationTopic = 'automation/action/confirm'

class mymqttskill(MycroftSkill):

    def __init__(self):
        super(mymqttskill, self).__init__(name="mymqttskill")

	self.default_location = "family_room"
       
        self.protocol = self.config["protocol"]
	self.mqttssl = self.config["mqtt-ssl"]
	self.mqttca = self.config["mqtt-ca-cert"]
	self.mqtthost = self.config["mqtt-host"]
	self.mqttport = self.config["mqtt-port"]
	self.mqttauth = self.config["mqtt-auth"]
	self.mqttuser = self.config["mqtt-user"]
	self.mqttpass = self.config["mqtt-pass"]

#        if (self.protocol == "mqtt"):
#            self.mqttc = mqtt.Client("MycroftAI")
#            if (self.mqttauth == "yes"):
#                self.mqttc.username_pw_set(self.mqttuser,self.mqttpass)
#            if (self.mqttssl == "yes"):
#                self.mqttc.tls_set(self.mqttca)
#            LOGGER.info("AJW - connect to: " + self.mqtthost)
#            LOGGER.info("AJW - connect to: " + str(self.mqttport))
#            self.mqttc.connect(self.mqtthost,self.mqttport,10)
#            self.mqttc.on_message = self.on_message
#            self.mqttc.subscribe(dataRequestTopic)
#            self.mqttc.loop_start()
 
    
    def initialize(self):
        self.load_data_files(dirname(__file__))
        self. __build_automation_command()
        self. __build_control_command()
	self. __build_dataRequest_command()
        
        
    def __build_automation_command(self):
        intent = IntentBuilder("automation_Intent")\
	.require("CommandKeyword")\
	.require("ModuleKeyword")\
	.require("ActionKeyword")\
	.optionally("LocationKeyword")\
	.build()
        self.register_intent(intent, self.handle_automation_command)

    def __build_control_command(self):
        intent = IntentBuilder("control_Intent")\
        .require("ModuleKeyword")\
        .require("AttributeKeyword")\
        .require("ValueKeyword")\
        .optionally("LocationKeyword")\
        .build()
        self.register_intent(intent, self.handle_control_command)

    def __build_dataRequest_command(self):
	# example: "what's the temperature on the deck"
        intent = IntentBuilder("dataRequest_Intent")\
        .require("RequestKeyword")\
        .require("SensorKeyword")\
        .require("LocationKeyword")\
        .build()
        self.register_intent(intent, self.handle_dataRequest_command)        

    def handle_automation_command(self, message):
	LOGGER.info('AJW: mqtt automation command')

        cmd_name = message.data.get("CommandKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        act_name = message.data.get("ActionKeyword")
	loc_name = message.data.get("LocationKeyword")

	if loc_name:
	    loc_name = loc_name.replace(' ', '_')
	else:
	    loc_name = self.default_location

        LOGGER.info('AJW: cmd: ' + cmd_name + '; mdl: ' + mdl_name + '; act: ' + act_name + '; loc: ' + loc_name)
        
        if act_name:
            cmd_name += '_' + act_name

        if (self.protocol == "mqtt"):
	    self.mqttc = mqtt.Client("MycroftAI")
	    if (self.mqttauth == "yes"):
	        mqttc.username_pw_set(self.mqttuser,self.mqttpass)
	    if (self.mqttssl == "yes"):
		mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            self.mqttc.connect(self.mqtthost,self.mqttport,10)
	    self.mqttc.on_message = self.on_message
	    self.mqttc.loop_start()
	    self.mqttc.subscribe(actionConfirmationTopic)
            LOGGER.info("AJW - connected - about to execute" + "-" + cmd_name)
            self.mqttc.publish(loc_name + "/" + mdl_name, act_name)
            LOGGER.info("AJW - Published: " + loc_name + "/" + mdl_name + ", " + act_name)
	    # allow time for the action to be performed and a confirmation to be returned
	    time.sleep(10)
	    self.mqttc.disconnect()
            LOGGER.info(mdl_name + "-" + cmd_name)

	else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

    def handle_control_command(self, message):

        att_name = message.data.get("AttributeKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        val_name = message.data.get("ValueKeyword")
        loc_name = message.data.get("LocationKeyword")

        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        LOGGER.info('AJW: att: ' + att_name + '; mdl: ' + mdl_name + '; val: ' + val_name + '; loc: ' + loc_name)

#        if act_name:
#            cmd_name += '_' + act_name

        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")            
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            mqttc.connect(self.mqtthost,self.mqttport,10)
#            LOGGER.info("AJW - connected - about to execute" + "-" + cmd_name)
            mqttc.publish(loc_name + "/" + mdl_name + "/" + att_name, val_name)
#           mqttc.publish("/mediaCenter/" + loc_name + "/" + mdl_name, act_name)
#            LOGGER.info("AJW - Published: " + loc_name + "/" + mdl_name + ", " + act_name)
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
#            LOGGER.info(mdl_name + "-" + cmd_name)

        else:
#            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

    def handle_dataRequest_command(self, message):
        req_name = message.data.get("RequestKeyword")
        sen_name = message.data.get("SensorKeyword")
        loc_name = message.data.get("LocationKeyword")

        if (self.protocol == "mqtt"):
            self.mqttc = mqtt.Client("MycroftAI")
            if (self.mqttauth == "yes"):
                self.mqttc.username_pw_set(self.mqttuser,self.mqttpass)
            if (self.mqttssl == "yes"):
                self.mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            self.mqttc.connect(self.mqtthost,self.mqttport,10)
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            self.mqttc.subscribe(dataRequestTopic)
            self.mqttc.publish("request/" + sen_name + "/" + loc_name, "")
            LOGGER.info("AJW - Published: request/" + sen_name + "/" + loc_name)
            time.sleep(10)
            self.mqttc.disconnect()
        else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

        
    def stop(self):
        pass

    def on_message(self, mqttClient, userdata, msg):
        LOGGER.info('AJW: Topic = ' + msg.topic)
        splitTopic = msg.topic.split('/')
        if splitTopic[0] == 'send':
            LOGGER.info('AJW: Received a message')
            self.speak_dialog("sensor.value", {"location": splitTopic[2], "sensor": splitTopic[1], "value": msg.payload})
	    return
	if msg.topic == actionConfirmationTopic:
	    if msg.payload == '1':
	        LOGGER.info('AJW: Requested action was successful')
	        self.speak_dialog('action.successful')
	    else:
	        LOGGER.info('AJW: Requested action was unsuccessful')
	        self.speak_dialog('action.unsuccessful')
	    return
        
def create_skill():
#    myskill = mymqttskill()
#    return myskill
    return mymqttskill()

