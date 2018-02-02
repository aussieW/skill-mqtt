import time

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
from mycroft.api import DeviceApi

from urllib2 import urlopen  # <<< not sure if this is required
import paho.mqtt.client as mqtt

__author__ = 'aussieW'  # based on the original work of 'jamiehoward430'

LOGGER = getLogger(__name__)

dataRequestTopic = 'send/#'
actionConfirmationTopic = 'automation/action/confirm'

class mqttskill(MycroftSkill):

    def __init__(self):
        super(mqttskill, self).__init__(name="mymqttskill")

        self.default_location = self.room_name()
       
        self.protocol = self.config["protocol"]
        self.mqttssl = self.config["mqtt-ssl"]
        self.mqttca = self.config["mqtt-ca-cert"]
        self.mqtthost = self.config["mqtt-host"]
        self.mqttport = self.config["mqtt-port"]
        self.mqttauth = self.config["mqtt-auth"]
        self.mqttuser = self.config["mqtt-user"]
        self.mqttpass = self.config["mqtt-pass"]
    
    def initialize(self):
        pass
		
    def mqqt_connect(self, topic=None):
        self.mqttc = mqtt.Client("MycroftAI_" + self.default_location)
        if (self.mqttauth == "yes"):
            mqttc.username_pw_set(self.mqttuser,self.mqttpass)
        if (self.mqttssl == "yes"):
            mqttc.tls_set(self.mqttca)
        LOGGER.info("AJW - connect to: " + self.mqtthost + ":" + str(self.mqttport))
        self.mqttc.connect(self.mqtthost,self.mqttport,10)
		# if s topic is provided then set up a listener
		if topic:
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            self.mqttc.subscribe(topic)
		
    def mqtt_publish(self, topic, msg):
	    LOGGER.info("AJW: Published " + topic + ", " + msg)
        self.mqttc.publish(topic, msg)
		
    def mqtt_disconnect(self):
        self.mqttc.disconnect()
	
	# from steve-mycroft wink skill
    @property	
    def room_name(self):
        # assume the "name" of the device is the "room name"
        device = DeviceApi().get()
		return device['name']

	@intent_handler(IntentBuilder('handle_automation_command').require("CommandKeyword").require("ModuleKeyword").require("ActionKeyword").optionally("LocationKeyword"))
    def handle_automation_command(self, message):
        LOGGER.info('AJW: mqtt automation command')

        cmd_name = message.data.get("CommandKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        act_name = message.data.get("ActionKeyword")
        loc_name = message.data.get("LocationKeyword")

        # set a default location in none provided
        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location
        
        if act_name:
            cmd_name += '_' + act_name

        LOGGER.info('AJW: Heard: ' + cmd_name + '; mdl: ' + mdl_name + '; act: ' + act_name + '; loc: ' + loc_name)

        self.mqtt_connect(actionConfirmationTopic)
        self.mqtt_publish(loc_name + "/" + mdl_name, act_name)
        # allow time for the action to be performed and a confirmation to be returned
        time.sleep(10)
        self.mqtt_disconnect()
        LOGGER.info(mdl_name + "-" + cmd_name)

	@intent_handler(IntentBuilder('handle_control_command').require("ModuleKeyword").require("AttributeKeyword").require("ValueKeyword").optionally("LocationKeyword"))
    def handle_control_command(self, message):
	    # example: "set the kitchen display brightness to 40"
	
        LOGGER.info('AJW: handle control command')
		
        att_name = message.data.get("AttributeKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        val_name = message.data.get("ValueKeyword")
        loc_name = message.data.get("LocationKeyword")

        # set a default location in none provided
        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        LOGGER.info('AJW: att: ' + att_name + '; mdl: ' + mdl_name + '; val: ' + val_name + '; loc: ' + loc_name)

        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")            
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            mqttc.connect(self.mqtthost,self.mqttport,10)
            mqttc.publish(loc_name + "/" + mdl_name + "/" + att_name, val_name)
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
        else:
#            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

	@intent_handler(IntentBuilder('handle_show_world_time').require("ShowWordTime").require("WorldTime").require("City").optionally("LocationKeyword"))
    def handle_show_world_time(self, message):
	    # examples: "show the world time for shanghi on the kitchen display"
	    #           "display the world time for shanghi"
		
        LOGGER.info('AJW: handle show world time')
		
        city_name = message.data.get("City")
        loc_name = message.data.get("LocationKeyword")

        # set a default location in none provided
        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")            
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            mqttc.connect(self.mqtthost,self.mqttport,10)
            mqttc.publish(loc_name + "/display/worldtime", city_name)
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
        else:
#            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

	@intent_handler(IntentBuilder('handle_hide_world_time').require("HideWordTime").require("WorldTime").optionally("LocationKeyword"))
    def handle_hide_world_time(self, message):
	    # examples: "hide the world time on the kitchen display"
	    #           "hide the world time"
		#           "remove the world time"
		
        LOGGER.info('AJW: handle show world time')
		
        loc_name = message.data.get("LocationKeyword")

        # set a default location in none provided
        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")            
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            mqttc.connect(self.mqtthost,self.mqttport,10)
            mqttc.publish(loc_name + "/display/worldtime", "")
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
        else:
#            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

	@intent_handler(IntentBuilder('handle_dataRequest_command').require("RequestKeyword").require("SensorKeyword").require("LocationKeyword"))
    def handle_dataRequest_command(self, message):
	    # example: "what is the temperature on the deck"
		
        LOGGER.info('AJW: handle control command')
		
        req_name = message.data.get("RequestKeyword")
        sen_name = message.data.get("SensorKeyword")
        loc_name = message.data.get("LocationKeyword")

        # set a default location in none provided
        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        self.mqqt_connect()
        self.mqtt_publish("request/" + sen_name + "/" + loc_name, "")
        self.mqtt_disconnect()

#    def stop(self):
#        pass

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
    return mqttskill()
