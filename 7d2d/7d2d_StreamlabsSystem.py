import telnetlib
import clr
import sys
import json
import os
import ctypes
import codecs

ScriptName = "7d2d Zombie Spawner"
Website = "http://www.github.com/vbawol/"
Description = "Zombie Spawner for Streamlabs Bot"
Creator = "vbawol"
Version = "1.0.0"

configFile = "config.json"
settings = {}

def ScriptToggled(state):
	return

def Init():
	global settings
	global tn

	# toto add setttings
	host = '127.0.0.1'
	port = 8080
	password = 'changeMe'
	# connect to remote host
	try:
		tn = telnetlib.Telnet(host, port)
	except:
		print('Unable to connect')
		sys.exit()

	# Send Password
	tn.read_until(b"Please enter password: ", 4)
	tn.write(password.encode('ascii') + b"\n")

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"liveOnly": True,
			"command": "!zombie",
			"permission": "Everyone",
			"useCustomCosts" : True,
			"costs": 25,
			"useCooldown": True,
			"useCooldownMessages": True,
			"cooldown": 1,
			"onCooldown": "$user, $command is still on cooldown for $cd minutes!",
			"userCooldown": 300,
			"onUserCooldown": "$user $command is still on user cooldown for $cd minutes!",
			"responseNotEnoughPoints": "$user you have only $points $currency and need $cost $currency.",
			"responseLost": "$user spawned a horde! Cost: $cost $currency."
		}

def Execute(data):
	if data.IsChatMessage() and data.GetParam(0).lower() == settings["command"] and Parent.HasPermission(data.User, settings["permission"], "") and ((settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
		outputMessage = ""
		userId = data.User			
		username = data.UserName
		points = Parent.GetPoints(userId)

		if settings["useCustomCosts"] and (data.GetParamCount() == 2):
			try: 
				costs = int(data.GetParam(1))
			except:
				if data.GetParam(1) == 'all': 
					costs = points
				else :
					costs = settings["costs"] 
		else:
			costs = settings["costs"]

		if (costs > Parent.GetPoints(userId)) or (costs < 1):
			outputMessage = settings["responseNotEnoughPoints"]
		elif settings["useCooldown"] and (Parent.IsOnCooldown(ScriptName, settings["command"]) or Parent.IsOnUserCooldown(ScriptName, settings["command"], userId)):
			if settings["useCooldownMessages"]:
				if Parent.GetCooldownDuration(ScriptName, settings["command"]) > Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId):
					cdi = Parent.GetCooldownDuration(ScriptName, settings["command"])
					cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
					outputMessage = settings["onCooldown"]
				else:
					cdi = Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId)
					cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
					outputMessage = settings["onUserCooldown"]
				outputMessage = outputMessage.replace("$cd", cd)
			else:
				outputMessage = ""
		else:
			Parent.RemovePoints(userId, username, costs)

			outputMessage = settings["responseLost"]
			reward = costs
			#Parent.AddPoints(userId, username, int(reward))

			# toto add twitch user that sent it
			message = "Spawning Horde"
			tn.write(b'say " ' + message.encode('ascii') + b'" \n')
			tn.write(b'spawnwh \n')


				

			outputMessage = outputMessage.replace("$reward", str(reward))

			if settings["useCooldown"]:
				Parent.AddUserCooldown(ScriptName, settings["command"], userId, settings["userCooldown"])
				Parent.AddCooldown(ScriptName, settings["command"], settings["cooldown"])

		outputMessage = outputMessage.replace("$cost", str(costs))
		outputMessage = outputMessage.replace("$user", username)
		outputMessage = outputMessage.replace("$points", str(points))
		outputMessage = outputMessage.replace("$currency", Parent.GetCurrencyName())
		outputMessage = outputMessage.replace("$command", settings["command"])

		Parent.SendStreamMessage(outputMessage)
	return

def ReloadSettings(jsonData):
	Init()
	return

def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "README.txt")
	os.startfile(location)
	return

def Tick():
	return
