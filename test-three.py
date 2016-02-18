#!/usr/bin/python
# coding: utf-8
# encoding=utf8
import os
import textwrap
import time
import traceback
import math
import urllib
import Cookie
import cookielib
import urllib2
import errno
import sys
import re
import threading
import random
import collections
from colorama import init
import dbhash
import anydbm
import logging
import shelve
from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
from ws4py import configure_logger
import datetime
#from bs4 import BeautifulSoup #beautifulsoup for windows #For processing HTML
from BeautifulSoup import BeautifulSoup #beautifulsoup for linux         # For processing HTML

ss=['800x600','1280x720', '720x480', '1920x1080', '1024x768', '1366x768', '1024x576', '960x540', '720x405']

utc_offset= [  '-11', '-10', '-9.5', '-9', '-8', '-7', '-6', '-5', '-4.5', '-4', '-3.5', '-3',
                '-2', '-1', '+0', '+1', '+10', '+10.5', '+11', '+12', '+13', '+13.75', '+14',
                '+2', '+3', '+3.5', '+4', '+4.5', '+5', '+5.5', '+5.75', '+6', '+6.5', '+7',
                '+8', '+8.5', '+8.75', '+9', '+9.5' ]

#ts = time.time()
#utc_offset = (datetime.datetime.fromtimestamp(ts) -
#	      datetime.datetime.utcfromtimestamp(ts)).total_seconds()

re1=[ "All you need is an e-mail address!We are currently having difficulty sending confirmation emails to Hotmail and MSN. Please use alternate email services","&nbsp;", "Your E-Mail Address:","Create Your Free AccountSign up for yourFREEaccount", "Choose Your Username:","(This will be your chat name.)","I am over 18 years old. I have read theTerms and ConditionsandPrivacy Policy.(You will receive an e-mail when you register, plus an optional newsletter every few months. We will not share your e-mail with any 3rd party.)NOTE: If you do not receive our verification e-mail, or if you are considering creating a new free e-mail address to use here, we suggestGmail. That's what we use! :-)Forgot your Password?-Instructions / Frequently Asked Questions-Contact Support", "(Verification e-mail will be sent here.)",". ."]

#logger = configure_logger()
main_session = WebSocketManager()

emote={}
client=[]
gindex=1

xchat=[ 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
	20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 
	33, 34, 35, 36, 39, 40, 41, 42, 43, 44, 45, 46, 
	47, 48, 49, 56, 57, 58, 59, 60, 61
      ]

xchat_index=0

g_mute="Guests have been temporarily muted by the model. Members can still chat normally. Please login or register free to chat"
b_mute="Basic members have been temporarily muted by the model. Buy tokens once to become a Premium Member for life."

video_state={}
video_state[0]="PUBLIC-CHAT"
video_state[2]="AWAY"
video_state[12]="PVT"
video_state[13]="GROUP"
video_state[90]="WEBCAM IS OFF"
video_state[127]="OFFLINE"

startup_time = int(time.time())

guser="guest"
gpasscode="guest"

textwrapper = textwrap.TextWrapper(initial_indent="", width=100,
                               subsequent_indent=' ' * 14)

def db_open(flatdb):
	db_file = shelve.open(flatdb)
	return db_file

def db_sync(flatdb, lock):
	lock.acquire()
	flatdb.sync()
	lock.release()

def db_add(flatdb, lock, key, data):
	lock.acquire()
	try:
		flatdb[key] = data
	except:
		pass
	lock.release()
	return

def db_del(flatdb, key):
	try:
		del flatdb[key]   
	except KeyError:
		pass
def db_update(flatdb, lock, key, data):
	lock.acquire()
	db_del(flatdb, key)
	flatdb[key] = data
	lock.release()

def db_append(flatdb, lock, key, append_data):
	lock.acquire()
	temp = flatdb[key]
	temp.append(append_data)      
	flatdb[key]=temp
	lock.release()

def db_get(flatdb, lock, key):
	lock.acquire()
	try:
		entry=flatdb[key]
		lock.release()
		return entry
	except:
		lock.release()
		return None

def db_dumpall(flatdb, lock, call_back):
	i=0
	lock.acquire()
	for key in flatdb.keys():
		value=""
		try:
			value=flatdb[key]
		except KeyError:
			db_del(flatdb, key)
			pass
		call_back (value, key)
		i += 1
	print "Total entires : ", i
	lock.release()

def db_dumpinfo(flatdb, lock):
	lock.acquire()
	for key in flatdb.keys():
		value=flatdb[key]
		if len(value) > 5:
			print value
	lock.release()

def db_valuelookup(flatdb, lock, val_look, dump_func):
	match=0
	lock.acquire()
	for key in flatdb.keys():
		value=""
		try:
			value=flatdb[key]
		except KeyError:
			pass
		for i in range(len(value)):
			if val_look.lower() in str(value[i]).lower():
				dump_func(key, value)
				match += 1
				break
	if match == 0:
		print ("No match found for %s" % val_look)
	else:
		print "Total matches found : ", match
	lock.release()

def db_getvaluelookup(flatdb, lock, val_look):
	match=0
	lock.acquire()
	for key in flatdb.keys():
		value=""
		try:
			value=flatdb[key]
		except KeyError:
			pass
		for i in range(len(value)):
			if val_look.lower()==str(value[i]).lower():
				match += 1
				lock.release()
				return value
	lock.release()
	return None

def db_keybasedlookup(flatdb, key):
	return flatdb[key]	

class attr:
	reset='\033[0m'
	bold='\033[01m'
	dim='\033[02m'
	normal='\033[22m'
class fg:
	black='\033[30m'
	red='\033[31m'
	green='\033[32m'
	yellow='\033[33m'
	blue='\033[34m'
	magenta='\033[35m'
	cyan='\033[36m'
	white='\033[37m'
class bg:
	black='\033[40m'
	red='\033[41m'
	green='\033[42m'
	yellow='\033[43m'
	blue='\033[44m'
	magenta='\033[45m'
	cyan='\033[46m'
	white='\033[47m'


def emote_init():
	x = raw_input(fg.white+'Set bEmote Width: ')
	y = raw_input(fg.white+'Set bEmote Height: ')
	global emote
	emote["(:"]="#~e,9,(:,18,18~#"
	emote["8)"]="#~e,12,8),18,18~#"
	emote["8d"]="#~e,5,8d,18,18~#"
	emote[":("]="#~e,26,(,18,18~#"
	emote[":)"]="#~e,1,),18,18~#"
	emote[":*"]="#~e,64,*,18,18~#"
	emote[":-$"]="#~e,37,-$,18,18~#"
	emote[":-)"]="#~e,1,-),18,18~#"
	emote[":-*"]="#~e,64,-*,18,18~#"
	emote[":-d"]="#~e,6,-d,18,18~#"
	emote[":08"]="#~e,67,08,20,21~#"
	emote[":1"]="#~e,69,1,20,20~#"
	emote[":1eye"]="#~e,68,1eye,20,24~#"
	emote[":2"]="#~e,70,2,20,22~#"
	emote[":34"]="#~e,71,34,30,26~#"
	emote[":48"]="#~e,72,48,20,21~#"
	emote[":59"]="#~e,74,59,28,26~#"
	emote[":838261"]="#~e,75,838261,19,19~#"
	emote[":?"]="#~e,46,?,18,18~#"
	emote[":ablow"]="#~e,76,ablow,30,25~#"
	emote[":admin"]="#~e,77,admin,30,22~#"
	emote[":afro"]="#~e,79,afro,33,31~#"
	emote[":afro2"]="#~e,78,afro2,27,27~#"
	emote[":agasi"]="#~e,80,agasi,27,22~#"
	emote[":aggressive"]="#~e,81,aggressive,36,27~#"
	emote[":ala"]="#~e,82,ala,20,22~#"
	emote[":alien"]="#~e,45,alien,18,18~#"
	emote[":alien2"]="#~e,83,alien2,26,22~#"
	emote[":alucard"]="#~e,85,alucard,38,24~#"
	emote[":angel"]="#~e,86,angel,42,23~#"
	emote[":angel_hypocrite"]="#~e,87,angel_hypocrite,20,25~#"
	emote[":angel_innocent"]="#~e,88,angel_innocent,18,22~#"
	emote[":angel_not"]="#~e,89,angel_not,18,24~#"
	emote[":angrier"]="#~e,90,angrier,18,18~#"
	emote[":angry"]="#~e,92,angry,20,20~#"
	emote[":angry2"]="#~e,91,angry2,18,18~#"
	emote[":angst"]="#~e,93,angst,16,16~#"
	emote[":animals_bunny1"]="#~e,95,animals_bunny1,18,24~#"
	emote[":animals_bunny2"]="#~e,96,animals_bunny2,18,29~#"
	emote[":animal_rooster"]="#~e,94,animal_rooster,18,23~#"
	emote[":appl"]="#~e,97,appl,35,31~#"
	emote[":arabia"]="#~e,98,arabia,21,28~#"
	emote[":argue3"]="#~e,99,argue3,43,18~#"
	emote[":arrow"]="#~e,48,arrow,18,18~#"
	emote[":arrow_1"]="#~e,100,arrow_1,20,20~#"
	emote[":arrow_2"]="#~e,101,arrow_2,20,20~#"
	emote[":arrow_3"]="#~e,102,arrow_3,20,20~#"
	emote[":arrow_4"]="#~e,103,arrow_4,20,20~#"
	emote[":arrow_5"]="#~e,104,arrow_5,20,20~#"
	emote[":arrow_6"]="#~e,105,arrow_6,20,20~#"
	emote[":badair"]="#~e,106,badair,48,19~#"
	emote[":bag"]="#~e,107,bag,22,23~#"
	emote[":balloon"]="#~e,108,balloon,18,32~#"
	emote[":bash"]="#~e,109,bash,41,28~#"
	emote[":basketball"]="#~e,110,basketball,31,20~#"
	emote[":batman"]="#~e,111,batman,20,27~#"
	emote[":bb"]="#~e,112,bb,32,20~#"
	emote[":beaver"]="#~e,41,beaver,18,18~#"
	emote[":bee"]="#~e,113,bee,40,33~#"
	emote[":beer"]="#~e,52,beer,18,18~#"
	emote[":biggrin"]="#~e,115,biggrin,20,20~#"
	emote[":biggrin2"]="#~e,114,biggrin2,20,20~#"
	emote[":biggrinthumb"]="#~e,116,biggrinthumb,40,20~#"
	emote[":bigsmile"]="#~e,117,bigsmile,20,20~#"
	emote[":bird"]="#~e,59,bird,18,18~#"
	emote[":bleh"]="#~e,118,bleh,18,18~#"
	emote[":blink"]="#~e,31,blink,20,20~#"
	emote[":blink2"]="#~e,119,blink2,20,20~#"
	emote[":blue_bandana"]="#~e,120,blue_bandana,23,19~#"
	emote[":blush"]="#~e,123,blush,18,18~#"
	emote[":blush-anim-cl"]="#~e,122,blush-anim-cl,20,20~#"
	emote[":blush2"]="#~e,121,blush2,20,20~#"
	emote[":blushing"]="#~e,125,blushing,18,18~#"
	emote[":blushing2"]="#~e,124,blushing2,18,18~#"
	emote[":boat"]="#~e,126,boat,26,33~#"
	emote[":bomb"]="#~e,127,bomb,23,18~#"
	emote[":book"]="#~e,128,book,35,20~#"
	emote[":bored"]="#~e,130,bored,15,15~#"
	emote[":bored2"]="#~e,129,bored2,20,20~#"
	emote[":borg"]="#~e,131,borg,18,18~#"
	emote[":bot"]="#~e,132,bot,18,18~#"
	emote[":boxed"]="#~e,134,boxed,18,18~#"
	emote[":boxed2"]="#~e,133,boxed2,18,18~#"
	emote[":brokeheart"]="#~e,63,brokeheart,18,18~#"
	emote[":busted_blue"]="#~e,136,busted_blue,18,24~#"
	emote[":busted_cop"]="#~e,137,busted_cop,20,28~#"
	emote[":busted_red"]="#~e,138,busted_red,18,24~#"
	emote[":bye2"]="#~e,140,bye2,20,20~#"
	emote[":bye"]="#~e,142,bye,15,15~#"
	emote[":canadian"]="#~e,143,canadian,23,22~#"
	emote[":captain"]="#~e,144,captain,20,25~#"
	emote[":cat"]="#~e,62,cat,18,18~#"
	emote[":censored"]="#~e,146,censored,34,18~#"
	emote[":censored2"]="#~e,145,censored2,48,18~#"
	emote[":chef"]="#~e,147,chef,23,28~#"
	emote[":chefsp"]="#~e,148,chefsp,21,29~#"
	emote[":chih"]="#~e,149,chih,15,15~#"
	emote[":chinese"]="#~e,150,chinese,26,20~#"
	emote[":chipmunk"]="#~e,41,chipmunk,18,18~#"
	emote[":chris"]="#~e,151,chris,20,18~#"
	emote[":cig"]="#~e,53,cig,18,18~#"
	emote[":cigarette"]="#~e,53,cigarette,18,18~#"
	emote[":clap_1"]="#~e,152,clap_1,31,25~#"
	emote[":clear"]="#~e,15151515,LeoLovesDongs,1000,5~#"
	emote[":closedeyes"]="#~e,154,closedeyes,20,20~#"
	emote[":closedeyes2"]="#~e,153,closedeyes2,20,20~#"
	emote[":cloud9"]="#~e,155,cloud9,25,26~#"
	emote[":clover"]="#~e,156,clover,19,20~#"
	emote[":clown"]="#~e,158,clown,20,20~#"
	emote[":clown2"]="#~e,157,clown2,28,18~#"
	emote[":coffee"]="#~e,54,coffee,18,18~#"
	emote[":coke"]="#~e,55,coke,18,18~#"
	emote[":cold"]="#~e,160,cold,26,32~#"
	emote[":cold2"]="#~e,159,cold2,25,32~#"
	emote[":confused"]="#~e,162,confused,16,21~#"
	emote[":confused_1"]="#~e,161,confused_1,18,25~#"
	emote[":confuzzled"]="#~e,163,confuzzled,20,20~#"
	emote[":console"]="#~e,164,console,46,20~#"
	emote[":construction"]="#~e,165,construction,47,23~#"
	emote[":cool"]="#~e,169,cool,20,20~#"
	emote[":cool1"]="#~e,166,cool1,18,18~#"
	emote[":cool2"]="#~e,167,cool2,20,20~#"
	emote[":cool3"]="#~e,168,cool3,18,18~#"
	emote[":coolsmoker"]="#~e,13,coolsmoker,18,18~#"
	emote[":cowboy"]="#~e,170,cowboy,27,26~#"
	emote[":cranky"]="#~e,171,cranky,22,22~#"
	emote[":crash"]="#~e,172,crash,34,28~#"
	emote[":cray"]="#~e,173,cray,31,22~#"
	emote[":crazy"]="#~e,174,crazy,20,20~#"
	emote[":cry"]="#~e,26,cry,18,18~#"
	emote[":cryin_smilie"]="#~e,177,cryin_smilie,20,20~#"
	emote[":cryss"]="#~e,178,cryss,24,20~#"
	emote[":cry_1"]="#~e,175,cry_1,40,18~#"
	emote[":cuckoo"]="#~e,29,cuckoo,26,18~#"
	emote[":cupidarrow"]="#~e,179,cupidarrow,31,19~#"
	emote[":curlers"]="#~e,180,curlers,26,22~#"
	emote[":d"]="#~e,6,d,18,18~#"
	emote[":dance"]="#~e,181,dance,32,32~#"
	emote[":darthvader"]="#~e,182,darthvader,25,26~#"
	emote[":death"]="#~e,183,death,38,24~#"
	emote[":detective"]="#~e,185,detective,23,25~#"
	emote[":detective2"]="#~e,184,detective2,22,22~#"
	emote[":devil"]="#~e,188,devil,18,23~#"
	emote[":devil_1"]="#~e,186,devil_1,22,25~#"
	emote[":devil_2"]="#~e,187,devil_2,25,23~#"
	emote[":director"]="#~e,189,director,41,22~#"
	emote[":dirol"]="#~e,190,dirol,21,21~#"
	emote[":disguise"]="#~e,192,disguise,18,22~#"
	emote[":disguise2"]="#~e,191,disguise2,18,18~#"
	emote[":disgust"]="#~e,194,disgust,20,20~#"
	emote[":disgust1"]="#~e,193,disgust1,20,21~#"
	emote[":doc"]="#~e,195,doc,15,23~#"
	emote[":dont"]="#~e,197,dont,28,27~#"
	emote[":dontgetit"]="#~e,196,dontgetit,20,20~#"
	emote[":dork"]="#~e,35,dork,20,20~#"
	emote[":doublef"]="#~e,198,doublef,37,15~#"
	emote[":dribble"]="#~e,200,dribble,28,28~#"
	emote[":drinks_nologo"]="#~e,201,drinks_nologo,45,25~#"
	emote[":drinks_pepsi"]="#~e,202,drinks_pepsi,45,25~#"
	emote[":drool"]="#~e,203,drool,18,25~#"
	emote[":dry"]="#~e,204,dry,20,20~#"
	emote[":dr_evil"]="#~e,199,dr_evil,30,23~#"
	emote[":dulya"]="#~e,205,dulya,18,18~#"
	emote[":dunno"]="#~e,206,dunno,38,18~#"
	emote[":durak"]="#~e,207,durak,47,20~#"
	emote[":eat"]="#~e,208,eat,47,20~#"
	emote[":ee"]="#~e,209,ee,20,21~#"
	emote[":eek"]="#~e,210,eek,26,24~#"
	emote[":eek_yello"]="#~e,211,eek_yello,20,20~#"
	emote[":egg"]="#~e,212,egg,24,24~#"
	emote[":egypt"]="#~e,213,egypt,31,28~#"
	emote[":eh"]="#~e,214,eh,20,20~#"
	emote[":elvis"]="#~e,215,elvis,18,22~#"
	emote[":embarrassed"]="#~e,14,embarrassed,18,18~#"
	emote[":erm"]="#~e,24,erm,18,18~#"
	emote[":ermm"]="#~e,216,ermm,18,18~#"
	emote[":essen"]="#~e,217,essen,31,26~#"
	emote[":euro"]="#~e,218,euro,28,29~#"
	emote[":evil"]="#~e,222,evil,20,20~#"
	emote[":evilguy"]="#~e,223,evilguy,18,18~#"
	emote[":evil_1"]="#~e,219,evil_1,20,20~#"
	emote[":evil_3"]="#~e,220,evil_3,18,26~#"
	emote[":evil_4"]="#~e,221,evil_4,20,18~#"
	emote[":excl"]="#~e,225,excl,20,20~#"
	emote[":exclamation"]="#~e,224,exclamation,20,20~#"
	emote[":eye_red"]="#~e,226,eye_red,18,18~#"
	emote[":fart"]="#~e,227,fart,18,29~#"
	emote[":fartnew"]="#~e,229,fartnew,18,29~#"
	emote[":fartnew2"]="#~e,228,fartnew2,46,29~#"
	emote[":fear"]="#~e,232,fear,25,25~#"
	emote[":fear2"]="#~e,231,fear2,20,21~#"
	emote[":fear_1"]="#~e,230,fear_1,18,18~#"
	emote[":figa"]="#~e,233,figa,20,20~#"
	emote[":fingal"]="#~e,234,fingal,22,15~#"
	emote[":fireman"]="#~e,236,fireman,25,25~#"
	emote[":fireman_1"]="#~e,235,fireman_1,25,25~#"
	emote[":flag_austria"]="#~e,237,flag_austria,45,25~#"
	emote[":flag_french"]="#~e,238,flag_french,45,25~#"
	emote[":flag_germany"]="#~e,239,flag_germany,45,25~#"
	emote[":flag_schweiz"]="#~e,240,flag_schweiz,45,25~#"
	emote[":flipoff"]="#~e,59,flipoff,18,18~#"
	emote[":flower"]="#~e,65,flower,18,18~#"
	emote[":flowers"]="#~e,587,flowers,28,18~#"
	emote[":flush"]="#~e,242,flush,24,26~#"
	emote[":football"]="#~e,243,football,23,28~#"
	emote[":footinmouth"]="#~e,244,footinmouth,21,19~#"
	emote[":foyer"]="#~e,245,foyer,19,19~#"
	emote[":fredy"]="#~e,246,fredy,34,27~#"
	emote[":frown"]="#~e,247,frown,16,16~#"
	emote[":fruits_apple"]="#~e,248,fruits_apple,18,29~#"
	emote[":fruits_cherry"]="#~e,249,fruits_cherry,18,19~#"
	emote[":fruits_orange"]="#~e,250,fruits_orange,18,18~#"
	emote[":frusty"]="#~e,251,frusty,30,17~#"
	emote[":fullmop"]="#~e,252,fullmop,20,19~#"
	emote[":funny"]="#~e,8,funny,18,18~#"
	emote[":furious"]="#~e,253,furious,18,18~#"
	emote[":fuyou_1"]="#~e,254,fuyou_1,25,20~#"
	emote[":fuyou_2"]="#~e,255,fuyou_2,25,20~#"
	emote[":fyou"]="#~e,256,fyou,25,20~#"
	emote[":g"]="#~e,260,g,25,23~#"
	emote[":geek"]="#~e,35,geek,20,20~#"
	emote[":gent"]="#~e,258,gent,15,21~#"
	emote[":george"]="#~e,259,george,18,18~#"
	emote[":ghost1"]="#~e,261,ghost1,18,21~#"
	emote[":ghost2"]="#~e,262,ghost2,18,21~#"
	emote[":ghostface"]="#~e,263,ghostface,20,28~#"
	emote[":gigi"]="#~e,264,gigi,15,15~#"
	emote[":glare"]="#~e,265,glare,20,20~#"
	emote[":good"]="#~e,266,good,26,23~#"
	emote[":goss"]="#~e,267,goss,40,20~#"
	emote[":greedy"]="#~e,268,greedy,18,18~#"
	emote[":grin"]="#~e,6,grin,18,18~#"
	emote[":gulp"]="#~e,271,gulp,25,17~#"
	emote[":gun2"]="#~e,272,gun2,38,18~#"
	emote[":gun_guns"]="#~e,273,gun_guns,48,22~#"
	emote[":gun_rifle"]="#~e,274,gun_rifle,49,23~#"
	emote[":ha"]="#~e,325,ha,18,18~#"
	emote[":hammer"]="#~e,276,hammer,30,26~#"
	emote[":hammer_1"]="#~e,275,hammer_1,40,21~#"
	emote[":happy"]="#~e,278,happy,20,20~#"
	emote[":happybirth"]="#~e,277,happybirth,40,28~#"
	emote[":harhar"]="#~e,279,harhar,34,26~#"
	emote[":hat"]="#~e,280,hat,26,21~#"
	emote[":hb"]="#~e,281,hb,28,29~#"
	emote[":heart"]="#~e,282,heart,19,19~#"
	emote[":hehe"]="#~e,283,hehe,20,20~#"
	emote[":hello"]="#~e,285,hello,18,18~#"
	emote[":helpsmilie"]="#~e,284,helpsmilie,35,25~#"
	emote[":hi"]="#~e,285,hi,31,28~#"
	emote[":hippi"]="#~e,286,hippi,40,28~#"
	emote[":hit"]="#~e,287,hit,43,22~#"
	emote[":hitler"]="#~e,288,hitler,20,20~#"
	emote[":hmm"]="#~e,289,hmm,18,18~#"
	emote[":holloween"]="#~e,290,holloween,18,18~#"
	emote[":horns"]="#~e,291,horns,33,25~#"
	emote[":horny"]="#~e,27,horny,20,20~#"
	emote[":hug"]="#~e,292,hug,47,18~#"
	emote[":huh"]="#~e,293,huh,20,20~#"
	emote[":ibdrool"]="#~e,294,ibdrool,18,29~#"
	emote[":icecream"]="#~e,295,icecream,22,25~#"
	emote[":icon6"]="#~e,296,icon6,19,19~#"
	emote[":idea"]="#~e,298,idea,20,20~#"
	emote[":idea_1"]="#~e,297,idea_1,22,26~#"
	emote[":idiot"]="#~e,299,idiot,20,20~#"
	emote[":image"]="#~e,588,image,32,32~#"
	emote[":info"]="#~e,300,info,31,31~#"
	emote[":inlove"]="#~e,43,inlove,18,18~#"
	emote[":in_love"]="#~e,301,in_love,20,25~#"
	emote[":ispug"]="#~e,302,ispug,25,22~#"
	emote[":jc"]="#~e,303,jc,18,18~#"
	emote[":jerk"]="#~e,304,jerk,25,20~#"
	emote[":jester"]="#~e,305,jester,33,25~#"
	emote[":jockey"]="#~e,306,jockey,20,21~#"
	emote[":jumpy"]="#~e,307,jumpy,28,28~#"
	emote[":kamikaze"]="#~e,308,kamikaze,24,20~#"
	emote[":kar"]="#~e,309,kar,40,28~#"
	emote[":kenshin2"]="#~e,310,kenshin2,27,26~#"
	emote[":kicher"]="#~e,311,kicher,15,15~#"
	emote[":kid"]="#~e,312,kid,20,20~#"
	emote[":king"]="#~e,313,king,25,27~#"
	emote[":kiss"]="#~e,64,kiss,18,18~#"
	emote[":kiss1"]="#~e,314,kiss1,18,18~#"
	emote[":kisss"]="#~e,315,kisss,36,24~#"
	emote[":kosoy"]="#~e,316,kosoy,15,15~#"
	emote[":krider"]="#~e,317,krider,20,20~#"
	emote[":krilin"]="#~e,318,krilin,20,21~#"
	emote[":kuss"]="#~e,319,kuss,37,18~#"
	emote[":kwasny"]="#~e,320,kwasny,18,18~#"
	emote[":lac"]="#~e,321,lac,24,24~#"
	emote[":lady"]="#~e,322,lady,19,25~#"
	emote[":lamer"]="#~e,323,lamer,49,24~#"
	emote[":laugh"]="#~e,325,laugh,18,18~#"
	emote[":laugh_1"]="#~e,324,laugh_1,20,20~#"
	emote[":licklips"]="#~e,326,licklips,25,25~#"
	emote[":lips"]="#~e,327,lips,23,15~#"
	emote[":lmao1"]="#~e,328,lmao1,16,16~#"
	emote[":lock"]="#~e,329,lock,32,23~#"
	emote[":lol"]="#~e,325,lol,18,18~#"
	emote[":lol1"]="#~e,331,lol1,16,16~#"
	emote[":lol_1"]="#~e,330,lol_1,20,20~#"
	emote[":lookaround"]="#~e,333,lookaround,20,20~#"
	emote[":lu"]="#~e,334,lu,40,24~#"
	emote[":mad"]="#~e,336,mad,20,20~#"
	emote[":mad_2"]="#~e,335,mad_2,22,28~#"
	emote[":mail1"]="#~e,337,mail1,18,24~#"
	emote[":mail2"]="#~e,338,mail2,44,33~#"
	emote[":man"]="#~e,339,man,19,20~#"
	emote[":marinheiro"]="#~e,340,marinheiro,25,25~#"
	emote[":matrix2"]="#~e,341,matrix2,18,18~#"
	emote[":megalol"]="#~e,342,megalol,20,20~#"
	emote[":mellow"]="#~e,343,mellow,20,20~#"
	emote[":mobile"]="#~e,344,mobile,31,24~#"
	emote[":mog"]="#~e,345,mog,33,33~#"
	emote[":moptop"]="#~e,346,moptop,20,19~#"
	emote[":mug"]="#~e,52,mug,18,18~#"
	emote[":mushy"]="#~e,348,mushy,20,20~#"
	emote[":music"]="#~e,351,music,22,23~#"
	emote[":music_blues"]="#~e,349,music_blues,24,25~#"
	emote[":music_dj"]="#~e,350,music_dj,28,28~#"
	emote[":music_walkman"]="#~e,352,music_walkman,26,24~#"
	emote[":music_whistling"]="#~e,354,music_whistling,35,20~#"
	emote[":music_whistling_1"]="#~e,353,music_whistling_1,19,18~#"
	emote[":native"]="#~e,355,native,20,20~#"
	emote[":nerd"]="#~e,35,nerd,20,20~#"
	emote[":new"]="#~e,360,new,30,26~#"
	emote[":newconfus"]="#~e,359,newconfus,18,26~#"
	emote[":nigger"]="#~e,355,nigger,20,20~#"
	emote[":ninja"]="#~e,361,ninja,20,20~#"
	emote[":no"]="#~e,364,no,20,20~#"
	emote[":noexpression"]="#~e,363,noexpression,18,18~#"
	emote[":noimageemot"]="#~e,365,noimageemot,38,18~#"
	emote[":nono"]="#~e,366,nono,23,25~#"
	emote[":nosweat"]="#~e,367,nosweat,19,18~#"
	emote[":notify"]="#~e,368,notify,20,27~#"
	emote[":notworthy"]="#~e,369,notworthy,33,25~#"
	emote[":novicok"]="#~e,370,novicok,31,31~#"
	emote[":no_1"]="#~e,362,no_1,20,20~#"
	emote[":nuke"]="#~e,371,nuke,20,20~#"
	emote[":o)"]="#~e,4,o),18,18~#"
	emote[":ohmy"]="#~e,372,ohmy,20,20~#"
	emote[":ohplease"]="#~e,10,ohplease,20,20~#"
	emote[":omg"]="#~e,33,omg,18,18~#"
	emote[":online2long"]="#~e,373,online2long,18,18~#"
	emote[":osama"]="#~e,374,osama,18,25~#"
	emote[":p"]="#~e,11,p,18,18~#"
	emote[":paperbag1"]="#~e,375,paperbag1,20,19~#"
	emote[":paperbag3"]="#~e,376,paperbag3,20,19~#"
	emote[":pardon"]="#~e,377,pardon,36,26~#"
	emote[":partytime"]="#~e,378,partytime,49,31~#"
	emote[":peace"]="#~e,379,peace,25,21~#"
	emote[":pepsi"]="#~e,56,pepsi,18,18~#"
	emote[":phone"]="#~e,381,phone,41,28~#"
	emote[":phone_1"]="#~e,380,phone_1,20,18~#"
	emote[":photo"]="#~e,382,photo,27,21~#"
	emote[":pig"]="#~e,383,pig,18,21~#"
	emote[":pilot"]="#~e,384,pilot,35,24~#"
	emote[":pimp"]="#~e,385,pimp,22,25~#"
	emote[":pinch"]="#~e,386,pinch,18,18~#"
	emote[":pipe1"]="#~e,387,pipe1,32,20~#"
	emote[":pirate"]="#~e,40,pirate,18,18~#"
	emote[":pirate2"]="#~e,388,pirate2,25,25~#"
	emote[":pissed"]="#~e,22,pissed,20,20~#"
	emote[":plane"]="#~e,390,plane,47,28~#"
	emote[":play_ball"]="#~e,391,play_ball,46,20~#"
	emote[":pleasantry"]="#~e,392,pleasantry,36,26~#"
	emote[":point"]="#~e,48,point,18,18~#"
	emote[":police"]="#~e,393,police,20,22~#"
	emote[":poo"]="#~e,61,poo,18,18~#"
	emote[":poop"]="#~e,61,poop,18,18~#"
	emote[":pop"]="#~e,55,pop,18,18~#"
	emote[":potty"]="#~e,394,potty,24,26~#"
	emote[":pray"]="#~e,395,pray,27,22~#"
	emote[":prop"]="#~e,396,prop,20,25~#"
	emote[":puke"]="#~e,397,puke,20,25~#"
	emote[":punch"]="#~e,398,punch,18,18~#"
	emote[":pussy"]="#~e,62,pussy,18,18~#"
	emote[":question"]="#~e,400,question,19,19~#"
	emote[":question1"]="#~e,399,question1,20,20~#"
	emote[":ranting_w"]="#~e,401,ranting_w,28,24~#"
	emote[":rasta"]="#~e,402,rasta,30,27~#"
	emote[":redface"]="#~e,404,redface,16,16~#"
	emote[":red_bandana"]="#~e,403,red_bandana,23,19~#"
	emote[":red_indian"]="#~e,405,red_indian,24,29~#"
	emote[":renske"]="#~e,406,renske,18,18~#"
	emote[":respect"]="#~e,407,respect,44,22~#"
	emote[":respekt"]="#~e,408,respekt,43,18~#"
	emote[":retard"]="#~e,29,retard,26,18~#"
	emote[":rev"]="#~e,409,rev,40,25~#"
	emote[":rinoa"]="#~e,410,rinoa,45,33~#"
	emote[":rip"]="#~e,411,rip,20,20~#"
	emote[":rofl"]="#~e,412,rofl,46,18~#"
	emote[":rolleyes"]="#~e,10,rolleyes,20,20~#"
	emote[":rose"]="#~e,65,rose,18,18~#"
	emote[":rotate"]="#~e,414,rotate,15,15~#"
	emote[":row"]="#~e,415,row,36,15~#"
	emote[":rupor"]="#~e,416,rupor,38,18~#"
	emote[":sad"]="#~e,26,sad,18,18~#"
	emote[":sadbye"]="#~e,3,sadbye,26,18~#"
	emote[":saddam"]="#~e,420,saddam,18,25~#"
	emote[":sad_1"]="#~e,417,sad_1,20,20~#"
	emote[":sad_2"]="#~e,418,sad_2,43,27~#"
	emote[":sad_3"]="#~e,419,sad_3,18,18~#"
	emote[":samurai"]="#~e,44,samurai,18,18~#"
	emote[":santa"]="#~e,423,santa,20,22~#"
	emote[":santa_1"]="#~e,422,santa_1,24,27~#"
	emote[":schmoll"]="#~e,424,schmoll,20,20~#"
	emote[":schnauz"]="#~e,425,schnauz,20,20~#"
	emote[":scooter"]="#~e,426,scooter,40,33~#"
	emote[":search"]="#~e,427,search,38,25~#"
	emote[":shifty"]="#~e,428,shifty,20,20~#"
	emote[":shit"]="#~e,429,shit,16,16~#"
	emote[":shock"]="#~e,33,shock,18,18~#"
	emote[":shocked"]="#~e,432,shocked,18,18~#"
	emote[":shocking"]="#~e,434,shocking,18,18~#"
	emote[":shock_1"]="#~e,430,shock_1,18,19~#"
	emote[":shok"]="#~e,435,shok,20,20~#"
	emote[":showoff"]="#~e,436,showoff,40,21~#"
	emote[":shrug"]="#~e,437,shrug,32,20~#"
	emote[":shuriken"]="#~e,438,shuriken,37,24~#"
	emote[":shutup"]="#~e,439,shutup,20,20~#"
	emote[":sick"]="#~e,441,sick,20,20~#"
	emote[":sick_1"]="#~e,440,sick_1,18,18~#"
	emote[":slap"]="#~e,442,slap,49,23~#"
	emote[":sleep"]="#~e,444,sleep,20,20~#"
	emote[":sleepy"]="#~e,47,sleepy,20,20~#"
	emote[":sleep_1"]="#~e,443,sleep_1,38,23~#"
	emote[":sly"]="#~e,446,sly,20,20~#"
	emote[":smartass"]="#~e,447,smartass,25,22~#"
	emote[":smile"]="#~e,453,smile,20,20~#"
	emote[":smilewink"]="#~e,454,smilewink,22,22~#"
	emote[":smile_1"]="#~e,452,smile_1,18,18~#"
	emote[":smilie"]="#~e,458,smilie,25,25~#"
	emote[":smilie1"]="#~e,455,smilie1,18,18~#"
	emote[":smilie3"]="#~e,456,smilie3,18,18~#"
	emote[":smilie4"]="#~e,457,smilie4,18,18~#"
	emote[":smilie_osx"]="#~e,459,smilie_osx,17,18~#"
	emote[":smilie_palm"]="#~e,460,smilie_palm,12,18~#"
	emote[":smilie_tux"]="#~e,461,smilie_tux,15,18~#"
	emote[":smilie_xp"]="#~e,462,smilie_xp,18,16~#"
	emote[":smoke"]="#~e,465,smoke,46,20~#"
	emote[":smoker"]="#~e,13,smoker,18,18~#"
	emote[":smoke_1"]="#~e,464,smoke_1,21,20~#"
	emote[":smoking"]="#~e,13,smoking,18,18~#"
	emote[":smurf"]="#~e,466,smurf,20,24~#"
	emote[":sm_clap"]="#~e,448,sm_clap,40,27~#"
	emote[":sm_crazy"]="#~e,449,sm_crazy,20,27~#"
	emote[":sm_fool"]="#~e,450,sm_fool,29,23~#"
	emote[":sm_haha"]="#~e,451,sm_haha,28,20~#"
	emote[":sm_lol"]="#~e,463,sm_lol,28,23~#"
	emote[":sm_victory"]="#~e,467,sm_victory,28,23~#"
	emote[":sm_yahoo"]="#~e,468,sm_yahoo,42,27~#"
	emote[":sneaktongue"]="#~e,469,sneaktongue,20,20~#"
	emote[":sneaky"]="#~e,470,sneaky,20,20~#"
	emote[":snorkel"]="#~e,471,snorkel,18,25~#"
	emote[":sombrero2"]="#~e,472,sombrero2,30,25~#"
	emote[":sorry"]="#~e,473,sorry,24,22~#"
	emote[":spidy"]="#~e,474,spidy,18,18~#"
	emote[":sp_ike"]="#~e,475,sp_ike,22,22~#"
	emote[":sq_yellow_angry"]="#~e,476,sq_yellow_angry,18,18~#"
	emote[":sq_yellow_arg"]="#~e,477,sq_yellow_arg,18,18~#"
	emote[":sq_yellow_biggrin"]="#~e,478,sq_yellow_biggrin,18,18~#"
	emote[":sq_yellow_blink"]="#~e,479,sq_yellow_blink,18,18~#"
	emote[":sq_yellow_blush"]="#~e,480,sq_yellow_blush,18,18~#"
	emote[":sq_yellow_closedeyes"]="#~e,481,sq_yellow_closedeyes,18,18~#"
	emote[":sq_yellow_cool"]="#~e,482,sq_yellow_cool,18,18~#"
	emote[":sq_yellow_cry"]="#~e,483,sq_yellow_cry,18,18~#"
	emote[":sq_yellow_dry"]="#~e,484,sq_yellow_dry,18,18~#"
	emote[":sq_yellow_glare"]="#~e,485,sq_yellow_glare,18,18~#"
	emote[":sq_yellow_goodmood"]="#~e,486,sq_yellow_goodmood,18,18~#"
	emote[":sq_yellow_happy"]="#~e,487,sq_yellow_happy,18,18~#"
	emote[":sq_yellow_huh"]="#~e,488,sq_yellow_huh,18,18~#"
	emote[":sq_yellow_laugh"]="#~e,489,sq_yellow_laugh,18,18~#"
	emote[":sq_yellow_mellow"]="#~e,490,sq_yellow_mellow,18,18~#"
	emote[":sq_yellow_notti"]="#~e,491,sq_yellow_notti,18,18~#"
	emote[":sq_yellow_ohmy"]="#~e,492,sq_yellow_ohmy,18,18~#"
	emote[":sq_yellow_playful"]="#~e,493,sq_yellow_playful,18,18~#"
	emote[":sq_yellow_sad"]="#~e,494,sq_yellow_sad,18,18~#"
	emote[":sq_yellow_sick"]="#~e,495,sq_yellow_sick,18,18~#"
	emote[":sq_yellow_smile"]="#~e,496,sq_yellow_smile,18,18~#"
	emote[":sq_yellow_specky"]="#~e,497,sq_yellow_specky,18,18~#"
	emote[":sq_yellow_surprise"]="#~e,498,sq_yellow_surprise,18,18~#"
	emote[":sq_yellow_tongue"]="#~e,499,sq_yellow_tongue,18,18~#"
	emote[":sq_yellow_unhappy"]="#~e,500,sq_yellow_unhappy,18,18~#"
	emote[":sq_yellow_unsure"]="#~e,501,sq_yellow_unsure,18,18~#"
	emote[":sq_yellow_wink"]="#~e,502,sq_yellow_wink,18,18~#"
	emote[":strongsad"]="#~e,503,strongsad,18,18~#"
	emote[":suck"]="#~e,504,suck,18,18~#"
	emote[":sumo"]="#~e,505,sumo,30,27~#"
	emote[":sun_smiley"]="#~e,506,sun_smiley,31,31~#"
	emote[":super"]="#~e,507,super,26,28~#"
	emote[":superlol"]="#~e,508,superlol,15,15~#"
	emote[":surrender"]="#~e,509,surrender,28,20~#"
	emote[":suspect"]="#~e,510,suspect,20,20~#"
	emote[":sweatdrop"]="#~e,511,sweatdrop,18,18~#"
	emote[":td"]="#~e,51,td,18,18~#"
	emote[":teehee"]="#~e,512,teehee,18,18~#"
	emote[":throb"]="#~e,513,throb,16,14~#"
	emote[":thumb"]="#~e,515,thumb,24,17~#"
	emote[":thumbdown"]="#~e,514,thumbdown,29,20~#"
	emote[":thumbs-up"]="#~e,516,thumbs-up,30,18~#"
	emote[":thumbsdown"]="#~e,51,thumbsdown,18,18~#"
	emote[":thumbsup"]="#~e,518,thumbsup,38,20~#"
	emote[":thumbup"]="#~e,517,thumbup,25,18~#"
	emote[":thumb_yello"]="#~e,519,thumb_yello,27,20~#"
	emote[":tired"]="#~e,47,tired,20,20~#"
	emote[":tongue"]="#~e,523,tongue,20,20~#"
	emote[":tongue1"]="#~e,520,tongue1,18,18~#"
	emote[":tongue2"]="#~e,521,tongue2,18,18~#"
	emote[":tongue5"]="#~e,522,tongue5,20,20~#"
	emote[":tongue_ss"]="#~e,524,tongue_ss,20,20~#"
	emote[":tooth"]="#~e,525,tooth,30,20~#"
	emote[":tounge"]="#~e,11,tounge,18,18~#"
	emote[":toxic"]="#~e,58,toxic,18,18~#"
	emote[":trumpet"]="#~e,526,trumpet,35,18~#"
	emote[":tu"]="#~e,50,tu,18,18~#"
	emote[":turned"]="#~e,527,turned,18,18~#"
	emote[":tv"]="#~e,60,tv,18,18~#"
	emote[":um"]="#~e,24,um,18,18~#"
	emote[":umnik"]="#~e,528,umnik,25,19~#"
	emote[":unknw"]="#~e,529,unknw,33,26~#"
	emote[":unlock"]="#~e,530,unlock,32,23~#"
	emote[":unsure"]="#~e,531,unsure,20,20~#"
	emote[":up"]="#~e,532,up,15,15~#"
	emote[":v"]="#~e,535,v,25,23~#"
	emote[":vertag"]="#~e,533,vertag,25,26~#"
	emote[":verysad"]="#~e,534,verysad,20,20~#"
	emote[":w00t"]="#~e,538,w00t,20,21~#"
	emote[":w00t1"]="#~e,536,w00t1,28,28~#"
	emote[":w00t2"]="#~e,537,w00t2,28,28~#"
	emote[":wacko"]="#~e,539,wacko,20,20~#"
	emote[":wallbash"]="#~e,540,wallbash,30,23~#"
	emote[":wassat"]="#~e,541,wassat,18,18~#"
	emote[":watsup"]="#~e,542,watsup,20,21~#"
	emote[":wave"]="#~e,139,wave,26,18~#"
	emote[":weep"]="#~e,543,weep,21,15~#"
	emote[":weight_lift"]="#~e,545,weight_lift,35,21~#"
	emote[":weight_lift2"]="#~e,544,weight_lift2,32,18~#"
	emote[":whatsthat"]="#~e,546,whatsthat,20,18~#"
	emote[":wheelchair"]="#~e,547,wheelchair,29,31~#"
	emote[":whistle"]="#~e,28,whistle,28,18~#"
	emote[":whistlesmile"]="#~e,548,whistlesmile,24,24~#"
	emote[":whistling"]="#~e,28,whistling,28,18~#"
	emote[":wiggle"]="#~e,549,wiggle,32,27~#"
	emote[":wince"]="#~e,30,wince,18,18~#"
	emote[":wink"]="#~e,556,wink,20,20~#"
	emote[":wink_1"]="#~e,550,wink_1,18,18~#"
	emote[":wink_2"]="#~e,551,wink_2,18,18~#"
	emote[":wink_3"]="#~e,552,wink_3,20,20~#"
	emote[":wink_5"]="#~e,553,wink_5,18,18~#"
	emote[":wink_6"]="#~e,554,wink_6,18,18~#"
	emote[":wink_7"]="#~e,555,wink_7,20,20~#"
	emote[":wolfwood"]="#~e,557,wolfwood,31,31~#"
	emote[":wolverine"]="#~e,559,wolverine,20,20~#"
	emote[":wolverine2"]="#~e,558,wolverine2,26,26~#"
	emote[":wounded1"]="#~e,560,wounded1,18,18~#"
	emote[":wounded2"]="#~e,561,wounded2,18,18~#"
	emote[":wow"]="#~e,5,wow,18,18~#"
	emote[":wub"]="#~e,563,wub,22,29~#"
	emote[":wub2"]="#~e,562,wub2,22,29~#"
	emote[":x"]="#~e,42,x,18,18~#"
	emote[":xmas"]="#~e,564,xmas,21,23~#"
	emote[":yak"]="#~e,565,yak,20,20~#"
	emote[":yaright"]="#~e,10,yaright,20,20~#"
	emote[":yawn"]="#~e,566,yawn,18,18~#"
	emote[":yeahright"]="#~e,567,yeahright,20,20~#"
	emote[":yel"]="#~e,568,yel,40,24~#"
	emote[":yes"]="#~e,569,yes,20,20~#"
	emote[":yikes"]="#~e,570,yikes,32,33~#"
	emote[":yinyang"]="#~e,571,yinyang,20,20~#"
	emote[":ymca"]="#~e,572,ymca,18,18~#"
	emote[":yucky"]="#~e,573,yucky,20,20~#"
	emote[":yuk1"]="#~e,574,yuk1,20,20~#"
	emote[":zip"]="#~e,575,zip,28,28~#"
	emote[":zippy"]="#~e,576,zippy,18,18~#"
	emote[":zoo_cat"]="#~e,577,zoo_cat,29,25~#"
	emote[":zoo_donatello"]="#~e,578,zoo_donatello,32,31~#"
	emote[":zoo_fox"]="#~e,583,zoo_fox,22,21~#"
	emote[":zoo_fox4"]="#~e,582,zoo_fox4,22,21~#"
	emote[":zoo_fox_1"]="#~e,579,zoo_fox_1,22,21~#"
	emote[":zoo_fox_2"]="#~e,580,zoo_fox_2,22,21~#"
	emote[":zoo_fox_3"]="#~e,581,zoo_fox_3,22,21~#"
	emote[":zoo_homestar"]="#~e,584,zoo_homestar,25,24~#"
	emote[":zoo_taz"]="#~e,585,zoo_taz,32,32~#"
	emote[":zorro"]="#~e,586,zorro,26,22~#"
	emote[":_)"]="#~e,6,_),18,18~#"
	emote[":_d"]="#~e,6,_d,18,18~#"
	emote[":|"]="#~e,18,|,18,18~#"
	emote[";)"]="#~e,2,;),18,18~#"
	emote["=;"]="#~e,27,=;,20,20~#"
	emote["=o/"]="#~e,10,=o/,20,20~#"
	emote["=]"]="#~e,34,=],18,18~#"
	emote[":-D"]="#~e,6,-D,18,18~#"
	emote[":D"]="#~e,6,D,18,18~#"
	emote["8D"]="#~e,5,8D,18,18~#"
	emote[":G"]="#~e,260,G,25,23~#"
	emote[":_D"]="#~e,6,_D,18,18~#"
	emote[":P"]="#~e,11,P,18,18~#"
	emote[":noperm"]="#~u,73b49864.gif,noperm~#"
	#resizeable emotes
	emote["b(:"]="#~e,9,(:,"+x+","+y+"~#"
	emote["b8)"]="#~e,12,8),"+x+","+y+"~#"
	emote["b8d"]="#~e,5,8d,"+x+","+y+"~#"
	emote[":b("]="#~e,26,(,"+x+","+y+"~#"
	emote[":b)"]="#~e,1,),"+x+","+y+"~#"
	emote[":b*"]="#~e,64,*,"+x+","+y+"~#"
	emote[":b-$"]="#~e,37,-$,"+x+","+y+"~#"
	emote[":b-)"]="#~e,1,-),"+x+","+y+"~#"
	emote[":b-*"]="#~e,64,-*,"+x+","+y+"~#"
	emote[":b-d"]="#~e,6,-d,"+x+","+y+"~#"
	emote[":b08"]="#~e,67,08,"+x+","+y+"~#"
	emote[":b1"]="#~e,69,1,"+x+","+y+"~#"
	emote[":b1eye"]="#~e,68,1eye,"+x+","+y+"~#"
	emote[":b2"]="#~e,70,2,"+x+","+y+"~#"
	emote[":b34"]="#~e,71,34,"+x+","+y+"~#"
	emote[":b48"]="#~e,72,48,"+x+","+y+"~#"
	emote[":b59"]="#~e,74,59,"+x+","+y+"~#"
	emote[":b838261"]="#~e,75,838261,"+x+","+y+"~#"
	emote[":b?"]="#~e,46,?,"+x+","+y+"~#"
	emote[":bablow"]="#~e,76,ablow,"+x+","+y+"~#"
	emote[":badmin"]="#~e,77,admin,"+x+","+y+"~#"
	emote[":bafro"]="#~e,79,afro,"+x+","+y+"~#"
	emote[":bafro2"]="#~e,78,afro2,"+x+","+y+"~#"
	emote[":bagasi"]="#~e,80,agasi,"+x+","+y+"~#"
	emote[":baggressive"]="#~e,81,aggressive,"+x+","+y+"~#"
	emote[":bala"]="#~e,82,ala,"+x+","+y+"~#"
	emote[":balien"]="#~e,45,alien,"+x+","+y+"~#"
	emote[":balien2"]="#~e,83,alien2,"+x+","+y+"~#"
	emote[":balucard"]="#~e,85,alucard,"+x+","+y+"~#"
	emote[":bangel"]="#~e,86,angel,"+x+","+y+"~#"
	emote[":bangel_hypocrite"]="#~e,87,angel_hypocrite,"+x+","+y+"~#"
	emote[":bangel_innocent"]="#~e,88,angel_innocent,"+x+","+y+"~#"
	emote[":bangel_not"]="#~e,89,angel_not,"+x+","+y+"~#"
	emote[":bangrier"]="#~e,90,angrier,"+x+","+y+"~#"
	emote[":bangry"]="#~e,92,angry,"+x+","+y+"~#"
	emote[":bangry2"]="#~e,91,angry2,"+x+","+y+"~#"
	emote[":bangst"]="#~e,93,angst,"+x+","+y+"~#"
	emote[":banimals_bunny1"]="#~e,95,animals_bunny1,"+x+","+y+"~#"
	emote[":banimals_bunny2"]="#~e,96,animals_bunny2,"+x+","+y+"~#"
	emote[":banimal_rooster"]="#~e,94,animal_rooster,"+x+","+y+"~#"
	emote[":bappl"]="#~e,97,appl,"+x+","+y+"~#"
	emote[":barabia"]="#~e,98,arabia,"+x+","+y+"~#"
	emote[":bargue3"]="#~e,99,argue3,"+x+","+y+"~#"
	emote[":barrow"]="#~e,48,arrow,"+x+","+y+"~#"
	emote[":barrow_1"]="#~e,100,arrow_1,"+x+","+y+"~#"
	emote[":barrow_2"]="#~e,101,arrow_2,"+x+","+y+"~#"
	emote[":barrow_3"]="#~e,102,arrow_3,"+x+","+y+"~#"
	emote[":barrow_4"]="#~e,103,arrow_4,"+x+","+y+"~#"
	emote[":barrow_5"]="#~e,104,arrow_5,"+x+","+y+"~#"
	emote[":barrow_6"]="#~e,105,arrow_6,"+x+","+y+"~#"
	emote[":bbadair"]="#~e,106,badair,"+x+","+y+"~#"
	emote[":bbag"]="#~e,107,bag,"+x+","+y+"~#"
	emote[":bballoon"]="#~e,108,balloon,"+x+","+y+"~#"
	emote[":bbash"]="#~e,109,bash,"+x+","+y+"~#"
	emote[":bbasketball"]="#~e,110,basketball,"+x+","+y+"~#"
	emote[":bbatman"]="#~e,111,batman,"+x+","+y+"~#"
	emote[":bbb"]="#~e,112,bb,"+x+","+y+"~#"
	emote[":bbeaver"]="#~e,41,beaver,"+x+","+y+"~#"
	emote[":bbee"]="#~e,113,bee,"+x+","+y+"~#"
	emote[":bbeer"]="#~e,52,beer,"+x+","+y+"~#"
	emote[":bbiggrin"]="#~e,115,biggrin,"+x+","+y+"~#"
	emote[":bbiggrin2"]="#~e,114,biggrin2,"+x+","+y+"~#"
	emote[":bbiggrinthumb"]="#~e,116,biggrinthumb,"+x+","+y+"~#"
	emote[":bbigsmile"]="#~e,117,bigsmile,"+x+","+y+"~#"
	emote[":bbird"]="#~e,59,bird,"+x+","+y+"~#"
	emote[":bbleh"]="#~e,118,bleh,"+x+","+y+"~#"
	emote[":bblink"]="#~e,31,blink,"+x+","+y+"~#"
	emote[":bblink2"]="#~e,119,blink2,"+x+","+y+"~#"
	emote[":bblue_bandana"]="#~e,120,blue_bandana,"+x+","+y+"~#"
	emote[":bblush"]="#~e,123,blush,"+x+","+y+"~#"
	emote[":bblush-anim-cl"]="#~e,122,blush-anim-cl,"+x+","+y+"~#"
	emote[":bblush2"]="#~e,121,blush2,"+x+","+y+"~#"
	emote[":bblushing"]="#~e,125,blushing,"+x+","+y+"~#"
	emote[":bblushing2"]="#~e,124,blushing2,"+x+","+y+"~#"
	emote[":bboat"]="#~e,126,boat,"+x+","+y+"~#"
	emote[":bbomb"]="#~e,127,bomb,"+x+","+y+"~#"
	emote[":bbook"]="#~e,128,book,"+x+","+y+"~#"
	emote[":bbored"]="#~e,130,bored,"+x+","+y+"~#"
	emote[":bbored2"]="#~e,129,bored2,"+x+","+y+"~#"
	emote[":bborg"]="#~e,131,borg,"+x+","+y+"~#"
	emote[":bbot"]="#~e,132,bot,"+x+","+y+"~#"
	emote[":bboxed"]="#~e,134,boxed,"+x+","+y+"~#"
	emote[":bboxed2"]="#~e,133,boxed2,"+x+","+y+"~#"
	emote[":bbrokeheart"]="#~e,63,brokeheart,"+x+","+y+"~#"
	emote[":bbusted_blue"]="#~e,136,busted_blue,"+x+","+y+"~#"
	emote[":bbusted_cop"]="#~e,137,busted_cop,"+x+","+y+"~#"
	emote[":bbusted_red"]="#~e,138,busted_red,"+x+","+y+"~#"
	emote[":bbye2"]="#~e,140,bye2,"+x+","+y+"~#"
	emote[":bbye"]="#~e,142,bye,"+x+","+y+"~#"
	emote[":bcanadian"]="#~e,143,canadian,"+x+","+y+"~#"
	emote[":bcaptain"]="#~e,144,captain,"+x+","+y+"~#"
	emote[":bcat"]="#~e,62,cat,"+x+","+y+"~#"
	emote[":bcensored"]="#~e,146,censored,"+x+","+y+"~#"
	emote[":bcensored2"]="#~e,145,censored2,"+x+","+y+"~#"
	emote[":bchef"]="#~e,147,chef,"+x+","+y+"~#"
	emote[":bchefsp"]="#~e,148,chefsp,"+x+","+y+"~#"
	emote[":bchih"]="#~e,149,chih,"+x+","+y+"~#"
	emote[":bchinese"]="#~e,150,chinese,"+x+","+y+"~#"
	emote[":bchipmunk"]="#~e,41,chipmunk,"+x+","+y+"~#"
	emote[":bchris"]="#~e,151,chris,"+x+","+y+"~#"
	emote[":bcig"]="#~e,53,cig,"+x+","+y+"~#"
	emote[":bcigarette"]="#~e,53,cigarette,"+x+","+y+"~#"
	emote[":bclap_1"]="#~e,152,clap_1,"+x+","+y+"~#"
	emote[":bclear"]="#~e,15151515,LeoLovesDongs,"+x+","+y+"~#"
	emote[":bclosedeyes"]="#~e,154,closedeyes,"+x+","+y+"~#"
	emote[":bclosedeyes2"]="#~e,153,closedeyes2,"+x+","+y+"~#"
	emote[":bcloud9"]="#~e,155,cloud9,"+x+","+y+"~#"
	emote[":bclover"]="#~e,156,clover,"+x+","+y+"~#"
	emote[":bclown"]="#~e,158,clown,"+x+","+y+"~#"
	emote[":bclown2"]="#~e,157,clown2,"+x+","+y+"~#"
	emote[":bcoffee"]="#~e,54,coffee,"+x+","+y+"~#"
	emote[":bcoke"]="#~e,55,coke,"+x+","+y+"~#"
	emote[":bcold"]="#~e,160,cold,"+x+","+y+"~#"
	emote[":bcold2"]="#~e,159,cold2,"+x+","+y+"~#"
	emote[":bconfused"]="#~e,162,confused,"+x+","+y+"~#"
	emote[":bconfused_1"]="#~e,161,confused_1,"+x+","+y+"~#"
	emote[":bconfuzzled"]="#~e,163,confuzzled,"+x+","+y+"~#"
	emote[":bconsole"]="#~e,164,console,"+x+","+y+"~#"
	emote[":bconstruction"]="#~e,165,construction,"+x+","+y+"~#"
	emote[":bcool"]="#~e,169,cool,"+x+","+y+"~#"
	emote[":bcool1"]="#~e,166,cool1,"+x+","+y+"~#"
	emote[":bcool2"]="#~e,167,cool2,"+x+","+y+"~#"
	emote[":bcool3"]="#~e,168,cool3,"+x+","+y+"~#"
	emote[":bcoolsmoker"]="#~e,13,coolsmoker,"+x+","+y+"~#"
	emote[":bcowboy"]="#~e,170,cowboy,"+x+","+y+"~#"
	emote[":bcranky"]="#~e,171,cranky,"+x+","+y+"~#"
	emote[":bcrash"]="#~e,172,crash,"+x+","+y+"~#"
	emote[":bcray"]="#~e,173,cray,"+x+","+y+"~#"
	emote[":bcrazy"]="#~e,174,crazy,"+x+","+y+"~#"
	emote[":bcry"]="#~e,26,cry,"+x+","+y+"~#"
	emote[":bcryin_smilie"]="#~e,177,cryin_smilie,"+x+","+y+"~#"
	emote[":bcryss"]="#~e,178,cryss,"+x+","+y+"~#"
	emote[":bcry_1"]="#~e,175,cry_1,"+x+","+y+"~#"
	emote[":bcuckoo"]="#~e,29,cuckoo,"+x+","+y+"~#"
	emote[":bcupidarrow"]="#~e,179,cupidarrow,"+x+","+y+"~#"
	emote[":bcurlers"]="#~e,180,curlers,"+x+","+y+"~#"
	emote[":bd"]="#~e,6,d,"+x+","+y+"~#"
	emote[":bdance"]="#~e,181,dance,"+x+","+y+"~#"
	emote[":bdarthvader"]="#~e,182,darthvader,"+x+","+y+"~#"
	emote[":bdeath"]="#~e,183,death,"+x+","+y+"~#"
	emote[":bdetective"]="#~e,185,detective,"+x+","+y+"~#"
	emote[":bdetective2"]="#~e,184,detective2,"+x+","+y+"~#"
	emote[":bdevil"]="#~e,188,devil,"+x+","+y+"~#"
	emote[":bdevil_1"]="#~e,186,devil_1,"+x+","+y+"~#"
	emote[":bdevil_2"]="#~e,187,devil_2,"+x+","+y+"~#"
	emote[":bdirector"]="#~e,189,director,"+x+","+y+"~#"
	emote[":bdirol"]="#~e,190,dirol,"+x+","+y+"~#"
	emote[":bdisguise"]="#~e,192,disguise,"+x+","+y+"~#"
	emote[":bdisguise2"]="#~e,191,disguise2,"+x+","+y+"~#"
	emote[":bdisgust"]="#~e,194,disgust,"+x+","+y+"~#"
	emote[":bdisgust1"]="#~e,193,disgust1,"+x+","+y+"~#"
	emote[":bdoc"]="#~e,195,doc,"+x+","+y+"~#"
	emote[":bdont"]="#~e,197,dont,"+x+","+y+"~#"
	emote[":bdontgetit"]="#~e,196,dontgetit,"+x+","+y+"~#"
	emote[":bdork"]="#~e,35,dork,"+x+","+y+"~#"
	emote[":bdoublef"]="#~e,198,doublef,"+x+","+y+"~#"
	emote[":bdribble"]="#~e,200,dribble,"+x+","+y+"~#"
	emote[":bdrinks_nologo"]="#~e,201,drinks_nologo,"+x+","+y+"~#"
	emote[":bdrinks_pepsi"]="#~e,202,drinks_pepsi,"+x+","+y+"~#"
	emote[":bdrool"]="#~e,203,drool,"+x+","+y+"~#"
	emote[":bdry"]="#~e,204,dry,"+x+","+y+"~#"
	emote[":bdr_evil"]="#~e,199,dr_evil,"+x+","+y+"~#"
	emote[":bdulya"]="#~e,205,dulya,"+x+","+y+"~#"
	emote[":bdunno"]="#~e,206,dunno,"+x+","+y+"~#"
	emote[":bdurak"]="#~e,207,durak,"+x+","+y+"~#"
	emote[":beat"]="#~e,208,eat,"+x+","+y+"~#"
	emote[":bee"]=""
	emote[":beek"]="#~e,210,eek,"+x+","+y+"~#"
	emote[":beek_yello"]="#~e,211,eek_yello,"+x+","+y+"~#"
	emote[":begg"]="#~e,212,egg,"+x+","+y+"~#"
	emote[":begypt"]="#~e,213,egypt,"+x+","+y+"~#"
	emote[":beh"]="#~e,214,eh,"+x+","+y+"~#"
	emote[":belvis"]="#~e,215,elvis,"+x+","+y+"~#"
	emote[":bembarrassed"]="#~e,14,embarrassed,"+x+","+y+"~#"
	emote[":berm"]="#~e,24,erm,"+x+","+y+"~#"
	emote[":bermm"]="#~e,216,ermm,"+x+","+y+"~#"
	emote[":bessen"]="#~e,217,essen,"+x+","+y+"~#"
	emote[":beuro"]="#~e,218,euro,"+x+","+y+"~#"
	emote[":bevil"]="#~e,222,evil,"+x+","+y+"~#"
	emote[":bevilguy"]="#~e,223,evilguy,"+x+","+y+"~#"
	emote[":bevil_1"]="#~e,219,evil_1,"+x+","+y+"~#"
	emote[":bevil_3"]="#~e,220,evil_3,"+x+","+y+"~#"
	emote[":bevil_4"]="#~e,221,evil_4,"+x+","+y+"~#"
	emote[":bexcl"]="#~e,225,excl,"+x+","+y+"~#"
	emote[":bexclamation"]="#~e,224,exclamation,"+x+","+y+"~#"
	emote[":beye_red"]="#~e,226,eye_red,"+x+","+y+"~#"
	emote[":bfart"]="#~e,227,fart,"+x+","+y+"~#"
	emote[":bfartnew"]="#~e,229,fartnew,"+x+","+y+"~#"
	emote[":bfartnew2"]="#~e,228,fartnew2,"+x+","+y+"~#"
	emote[":bfear"]="#~e,232,fear,"+x+","+y+"~#"
	emote[":bfear2"]="#~e,231,fear2,"+x+","+y+"~#"
	emote[":bfear_1"]="#~e,230,fear_1,"+x+","+y+"~#"
	emote[":bfiga"]="#~e,233,figa,"+x+","+y+"~#"
	emote[":bfingal"]="#~e,234,fingal,"+x+","+y+"~#"
	emote[":bfireman"]="#~e,236,fireman,"+x+","+y+"~#"
	emote[":bfireman_1"]="#~e,235,fireman_1,"+x+","+y+"~#"
	emote[":bflag_austria"]="#~e,237,flag_austria,"+x+","+y+"~#"
	emote[":bflag_french"]="#~e,238,flag_french,"+x+","+y+"~#"
	emote[":bflag_germany"]="#~e,239,flag_germany,"+x+","+y+"~#"
	emote[":bflag_schweiz"]="#~e,240,flag_schweiz,"+x+","+y+"~#"
	emote[":bflipoff"]="#~e,59,flipoff,"+x+","+y+"~#"
	emote[":bflower"]="#~e,65,flower,"+x+","+y+"~#"
	emote[":bflowers"]="#~e,587,flowers,"+x+","+y+"~#"
	emote[":bflush"]="#~e,242,flush,"+x+","+y+"~#"
	emote[":bfootball"]="#~e,243,football,"+x+","+y+"~#"
	emote[":bfootinmouth"]="#~e,244,footinmouth,"+x+","+y+"~#"
	emote[":bfoyer"]="#~e,245,foyer,"+x+","+y+"~#"
	emote[":bfredy"]="#~e,246,fredy,"+x+","+y+"~#"
	emote[":bfrown"]="#~e,247,frown,"+x+","+y+"~#"
	emote[":bfruits_apple"]="#~e,248,fruits_apple,"+x+","+y+"~#"
	emote[":bfruits_cherry"]="#~e,249,fruits_cherry,"+x+","+y+"~#"
	emote[":bfruits_orange"]="#~e,250,fruits_orange,"+x+","+y+"~#"
	emote[":bfrusty"]="#~e,251,frusty,"+x+","+y+"~#"
	emote[":bfullmop"]="#~e,252,fullmop,"+x+","+y+"~#"
	emote[":bfunny"]="#~e,8,funny,"+x+","+y+"~#"
	emote[":bfurious"]="#~e,253,furious,"+x+","+y+"~#"
	emote[":bfuyou_1"]="#~e,254,fuyou_1,"+x+","+y+"~#"
	emote[":bfuyou_2"]="#~e,255,fuyou_2,"+x+","+y+"~#"
	emote[":bfyou"]="#~e,256,fyou,"+x+","+y+"~#"
	emote[":bg"]="#~e,260,g,"+x+","+y+"~#"
	emote[":bgeek"]="#~e,35,geek,"+x+","+y+"~#"
	emote[":bgent"]="#~e,258,gent,"+x+","+y+"~#"
	emote[":bgeorge"]="#~e,259,george,"+x+","+y+"~#"
	emote[":bghost1"]="#~e,261,ghost1,"+x+","+y+"~#"
	emote[":bghost2"]="#~e,262,ghost2,"+x+","+y+"~#"
	emote[":bghostface"]="#~e,263,ghostface,"+x+","+y+"~#"
	emote[":bgigi"]="#~e,264,gigi,"+x+","+y+"~#"
	emote[":bglare"]="#~e,265,glare,"+x+","+y+"~#"
	emote[":bgood"]="#~e,266,good,"+x+","+y+"~#"
	emote[":bgoss"]="#~e,267,goss,"+x+","+y+"~#"
	emote[":bgreedy"]="#~e,268,greedy,"+x+","+y+"~#"
	emote[":bgrin"]="#~e,6,grin,"+x+","+y+"~#"
	emote[":bgulp"]="#~e,271,gulp,"+x+","+y+"~#"
	emote[":bgun2"]="#~e,272,gun2,"+x+","+y+"~#"
	emote[":bgun_guns"]="#~e,273,gun_guns,"+x+","+y+"~#"
	emote[":bgun_rifle"]="#~e,274,gun_rifle,"+x+","+y+"~#"
	emote[":bha"]="#~e,325,ha,"+x+","+y+"~#"
	emote[":bhammer"]="#~e,276,hammer,"+x+","+y+"~#"
	emote[":bhammer_1"]="#~e,275,hammer_1,"+x+","+y+"~#"
	emote[":bhappy"]="#~e,278,happy,"+x+","+y+"~#"
	emote[":bhappybirth"]="#~e,277,happybirth,"+x+","+y+"~#"
	emote[":bharhar"]="#~e,279,harhar,"+x+","+y+"~#"
	emote[":bhat"]="#~e,280,hat,"+x+","+y+"~#"
	emote[":bhb"]="#~e,281,hb,"+x+","+y+"~#"
	emote[":bheart"]="#~e,282,heart,"+x+","+y+"~#"
	emote[":bhehe"]="#~e,283,hehe,"+x+","+y+"~#"
	emote[":bhello"]="#~e,285,hello,"+x+","+y+"~#"
	emote[":bhelpsmilie"]="#~e,284,helpsmilie,"+x+","+y+"~#"
	emote[":bhi"]="#~e,285,hi,"+x+","+y+"~#"
	emote[":bhippi"]="#~e,286,hippi,"+x+","+y+"~#"
	emote[":bhit"]="#~e,287,hit,"+x+","+y+"~#"
	emote[":bhitler"]="#~e,288,hitler,"+x+","+y+"~#"
	emote[":bhmm"]="#~e,289,hmm,"+x+","+y+"~#"
	emote[":bholloween"]="#~e,290,holloween,"+x+","+y+"~#"
	emote[":bhorns"]="#~e,291,horns,"+x+","+y+"~#"
	emote[":bhorny"]="#~e,27,horny,"+x+","+y+"~#"
	emote[":bhug"]="#~e,292,hug,"+x+","+y+"~#"
	emote[":bhuh"]="#~e,293,huh,"+x+","+y+"~#"
	emote[":bibdrool"]="#~e,294,ibdrool,"+x+","+y+"~#"
	emote[":bicecream"]="#~e,295,icecream,"+x+","+y+"~#"
	emote[":bicon6"]="#~e,296,icon6,"+x+","+y+"~#"
	emote[":bidea"]="#~e,298,idea,"+x+","+y+"~#"
	emote[":bidea_1"]="#~e,297,idea_1,"+x+","+y+"~#"
	emote[":bidiot"]="#~e,299,idiot,"+x+","+y+"~#"
	emote[":bimage"]="#~e,588,image,"+x+","+y+"~#"
	emote[":binfo"]="#~e,300,info,"+x+","+y+"~#"
	emote[":binlove"]="#~e,43,inlove,"+x+","+y+"~#"
	emote[":bin_love"]="#~e,301,in_love,"+x+","+y+"~#"
	emote[":bispug"]="#~e,302,ispug,"+x+","+y+"~#"
	emote[":bjc"]="#~e,303,jc,"+x+","+y+"~#"
	emote[":bjerk"]="#~e,304,jerk,"+x+","+y+"~#"
	emote[":bjester"]="#~e,305,jester,"+x+","+y+"~#"
	emote[":bjockey"]="#~e,306,jockey,"+x+","+y+"~#"
	emote[":bjumpy"]="#~e,307,jumpy,"+x+","+y+"~#"
	emote[":bkamikaze"]="#~e,308,kamikaze,"+x+","+y+"~#"
	emote[":bkar"]="#~e,309,kar,"+x+","+y+"~#"
	emote[":bkenshin2"]="#~e,310,kenshin2,"+x+","+y+"~#"
	emote[":bkicher"]="#~e,311,kicher,"+x+","+y+"~#"
	emote[":bkid"]="#~e,312,kid,"+x+","+y+"~#"
	emote[":bking"]="#~e,313,king,"+x+","+y+"~#"
	emote[":bkiss"]="#~e,64,kiss,"+x+","+y+"~#"
	emote[":bkiss1"]="#~e,314,kiss1,"+x+","+y+"~#"
	emote[":bkisss"]="#~e,315,kisss,"+x+","+y+"~#"
	emote[":bkosoy"]="#~e,316,kosoy,"+x+","+y+"~#"
	emote[":bkrider"]="#~e,317,krider,"+x+","+y+"~#"
	emote[":bkrilin"]="#~e,318,krilin,"+x+","+y+"~#"
	emote[":bkuss"]="#~e,319,kuss,"+x+","+y+"~#"
	emote[":bkwasny"]="#~e,320,kwasny,"+x+","+y+"~#"
	emote[":blac"]="#~e,321,lac,"+x+","+y+"~#"
	emote[":blady"]="#~e,322,lady,"+x+","+y+"~#"
	emote[":blamer"]="#~e,323,lamer,"+x+","+y+"~#"
	emote[":blaugh"]="#~e,325,laugh,"+x+","+y+"~#"
	emote[":blaugh_1"]="#~e,324,laugh_1,"+x+","+y+"~#"
	emote[":blicklips"]="#~e,326,licklips,"+x+","+y+"~#"
	emote[":blips"]="#~e,327,lips,"+x+","+y+"~#"
	emote[":blmao1"]="#~e,328,lmao1,"+x+","+y+"~#"
	emote[":block"]="#~e,329,lock,"+x+","+y+"~#"
	emote[":blol"]="#~e,325,lol,"+x+","+y+"~#"
	emote[":blol1"]="#~e,331,lol1,"+x+","+y+"~#"
	emote[":blol_1"]="#~e,330,lol_1,"+x+","+y+"~#"
	emote[":blookaround"]="#~e,333,lookaround,"+x+","+y+"~#"
	emote[":blu"]="#~e,334,lu,"+x+","+y+"~#"
	emote[":bmad"]="#~e,336,mad,"+x+","+y+"~#"
	emote[":bmad_2"]="#~e,335,mad_2,"+x+","+y+"~#"
	emote[":bmail1"]="#~e,337,mail1,"+x+","+y+"~#"
	emote[":bmail2"]="#~e,338,mail2,"+x+","+y+"~#"
	emote[":bman"]="#~e,339,man,"+x+","+y+"~#"
	emote[":bmarinheiro"]="#~e,340,marinheiro,"+x+","+y+"~#"
	emote[":bmatrix2"]="#~e,341,matrix2,"+x+","+y+"~#"
	emote[":bmegalol"]="#~e,342,megalol,"+x+","+y+"~#"
	emote[":bmellow"]="#~e,343,mellow,"+x+","+y+"~#"
	emote[":bmobile"]="#~e,344,mobile,"+x+","+y+"~#"
	emote[":bmog"]="#~e,345,mog,"+x+","+y+"~#"
	emote[":bmoptop"]="#~e,346,moptop,"+x+","+y+"~#"
	emote[":bmug"]="#~e,52,mug,"+x+","+y+"~#"
	emote[":bmushy"]="#~e,348,mushy,"+x+","+y+"~#"
	emote[":bmusic"]="#~e,351,music,"+x+","+y+"~#"
	emote[":bmusic_blues"]="#~e,349,music_blues,"+x+","+y+"~#"
	emote[":bmusic_dj"]="#~e,350,music_dj,"+x+","+y+"~#"
	emote[":bmusic_walkman"]="#~e,352,music_walkman,"+x+","+y+"~#"
	emote[":bmusic_whistling"]="#~e,354,music_whistling,"+x+","+y+"~#"
	emote[":bmusic_whistling_1"]="#~e,353,music_whistling_1,"+x+","+y+"~#"
	emote[":bnative"]="#~e,355,native,"+x+","+y+"~#"
	emote[":bnerd"]="#~e,35,nerd,"+x+","+y+"~#"
	emote[":bnew"]="#~e,360,new,"+x+","+y+"~#"
	emote[":bnewconfus"]="#~e,359,newconfus,"+x+","+y+"~#"
	emote[":bnigger"]="#~e,355,nigger,"+x+","+y+"~#"
	emote[":bninja"]="#~e,361,ninja,"+x+","+y+"~#"
	emote[":bno"]="#~e,364,no,"+x+","+y+"~#"
	emote[":bnoexpression"]="#~e,363,noexpression,"+x+","+y+"~#"
	emote[":bnoimageemot"]="#~e,365,noimageemot,"+x+","+y+"~#"
	emote[":bnono"]="#~e,366,nono,"+x+","+y+"~#"
	emote[":bnosweat"]="#~e,367,nosweat,"+x+","+y+"~#"
	emote[":bnotify"]="#~e,368,notify,"+x+","+y+"~#"
	emote[":bnotworthy"]="#~e,369,notworthy,"+x+","+y+"~#"
	emote[":bnovicok"]="#~e,370,novicok,"+x+","+y+"~#"
	emote[":bno_1"]="#~e,362,no_1,"+x+","+y+"~#"
	emote[":bnuke"]="#~e,371,nuke,"+x+","+y+"~#"
	emote[":bo)"]="#~e,4,o),"+x+","+y+"~#"
	emote[":bohmy"]="#~e,372,ohmy,"+x+","+y+"~#"
	emote[":bohplease"]="#~e,10,ohplease,"+x+","+y+"~#"
	emote[":bomg"]="#~e,33,omg,"+x+","+y+"~#"
	emote[":bonline2long"]="#~e,373,online2long,"+x+","+y+"~#"
	emote[":bosama"]="#~e,374,osama,"+x+","+y+"~#"
	emote[":bp"]="#~e,11,p,"+x+","+y+"~#"
	emote[":bpaperbag1"]="#~e,375,paperbag1,"+x+","+y+"~#"
	emote[":bpaperbag3"]="#~e,376,paperbag3,"+x+","+y+"~#"
	emote[":bpardon"]="#~e,377,pardon,"+x+","+y+"~#"
	emote[":bpartytime"]="#~e,378,partytime,"+x+","+y+"~#"
	emote[":bpeace"]="#~e,379,peace,"+x+","+y+"~#"
	emote[":bpepsi"]="#~e,56,pepsi,"+x+","+y+"~#"
	emote[":bphone"]="#~e,381,phone,"+x+","+y+"~#"
	emote[":bphone_1"]="#~e,380,phone_1,"+x+","+y+"~#"
	emote[":bphoto"]="#~e,382,photo,"+x+","+y+"~#"
	emote[":bpig"]="#~e,383,pig,"+x+","+y+"~#"
	emote[":bpilot"]="#~e,384,pilot,"+x+","+y+"~#"
	emote[":bpimp"]="#~e,385,pimp,"+x+","+y+"~#"
	emote[":bpinch"]="#~e,386,pinch,"+x+","+y+"~#"
	emote[":bpipe1"]="#~e,387,pipe1,"+x+","+y+"~#"
	emote[":bpirate"]="#~e,40,pirate,"+x+","+y+"~#"
	emote[":bpirate2"]="#~e,388,pirate2,"+x+","+y+"~#"
	emote[":bpissed"]="#~e,22,pissed,"+x+","+y+"~#"
	emote[":bplane"]="#~e,390,plane,"+x+","+y+"~#"
	emote[":bplay_ball"]="#~e,391,play_ball,"+x+","+y+"~#"
	emote[":bpleasantry"]="#~e,392,pleasantry,"+x+","+y+"~#"
	emote[":bpoint"]="#~e,48,point,"+x+","+y+"~#"
	emote[":bpolice"]="#~e,393,police,"+x+","+y+"~#"
	emote[":bpoo"]="#~e,61,poo,"+x+","+y+"~#"
	emote[":bpoop"]="#~e,61,poop,"+x+","+y+"~#"
	emote[":bpop"]="#~e,55,pop,"+x+","+y+"~#"
	emote[":bpotty"]="#~e,394,potty,"+x+","+y+"~#"
	emote[":bpray"]="#~e,395,pray,"+x+","+y+"~#"
	emote[":bprop"]="#~e,396,prop,"+x+","+y+"~#"
	emote[":bpuke"]="#~e,397,puke,"+x+","+y+"~#"
	emote[":bpunch"]="#~e,398,punch,"+x+","+y+"~#"
	emote[":bpussy"]="#~e,62,pussy,"+x+","+y+"~#"
	emote[":bquestion"]="#~e,400,question,"+x+","+y+"~#"
	emote[":bquestion1"]="#~e,399,question1,"+x+","+y+"~#"
	emote[":branting_w"]="#~e,401,ranting_w,"+x+","+y+"~#"
	emote[":brasta"]="#~e,402,rasta,"+x+","+y+"~#"
	emote[":bredface"]="#~e,404,redface,"+x+","+y+"~#"
	emote[":bred_bandana"]="#~e,403,red_bandana,"+x+","+y+"~#"
	emote[":bred_indian"]="#~e,405,red_indian,"+x+","+y+"~#"
	emote[":brenske"]="#~e,406,renske,"+x+","+y+"~#"
	emote[":brespect"]="#~e,407,respect,"+x+","+y+"~#"
	emote[":brespekt"]="#~e,408,respekt,"+x+","+y+"~#"
	emote[":bretard"]="#~e,29,retard,"+x+","+y+"~#"
	emote[":brev"]="#~e,409,rev,"+x+","+y+"~#"
	emote[":brinoa"]="#~e,410,rinoa,"+x+","+y+"~#"
	emote[":brip"]="#~e,411,rip,"+x+","+y+"~#"
	emote[":brofl"]="#~e,412,rofl,"+x+","+y+"~#"
	emote[":brolleyes"]="#~e,10,rolleyes,"+x+","+y+"~#"
	emote[":brose"]="#~e,65,rose,"+x+","+y+"~#"
	emote[":brotate"]="#~e,414,rotate,"+x+","+y+"~#"
	emote[":brow"]="#~e,415,row,"+x+","+y+"~#"
	emote[":brupor"]="#~e,416,rupor,"+x+","+y+"~#"
	emote[":bsad"]="#~e,26,sad,"+x+","+y+"~#"
	emote[":bsadbye"]="#~e,3,sadbye,"+x+","+y+"~#"
	emote[":bsaddam"]="#~e,420,saddam,"+x+","+y+"~#"
	emote[":bsad_1"]="#~e,417,sad_1,"+x+","+y+"~#"
	emote[":bsad_2"]="#~e,418,sad_2,"+x+","+y+"~#"
	emote[":bsad_3"]="#~e,419,sad_3,"+x+","+y+"~#"
	emote[":bsamurai"]="#~e,44,samurai,"+x+","+y+"~#"
	emote[":bsanta"]="#~e,423,santa,"+x+","+y+"~#"
	emote[":bsanta_1"]="#~e,422,santa_1,"+x+","+y+"~#"
	emote[":bschmoll"]="#~e,424,schmoll,"+x+","+y+"~#"
	emote[":bschnauz"]="#~e,425,schnauz,"+x+","+y+"~#"
	emote[":bscooter"]="#~e,426,scooter,"+x+","+y+"~#"
	emote[":bsearch"]="#~e,427,search,"+x+","+y+"~#"
	emote[":bshifty"]="#~e,428,shifty,"+x+","+y+"~#"
	emote[":bshit"]="#~e,429,shit,"+x+","+y+"~#"
	emote[":bshock"]="#~e,33,shock,"+x+","+y+"~#"
	emote[":bshocked"]="#~e,432,shocked,"+x+","+y+"~#"
	emote[":bshocking"]="#~e,434,shocking,"+x+","+y+"~#"
	emote[":bshock_1"]="#~e,430,shock_1,"+x+","+y+"~#"
	emote[":bshok"]="#~e,435,shok,"+x+","+y+"~#"
	emote[":bshowoff"]="#~e,436,showoff,"+x+","+y+"~#"
	emote[":bshrug"]="#~e,437,shrug,"+x+","+y+"~#"
	emote[":bshuriken"]="#~e,438,shuriken,"+x+","+y+"~#"
	emote[":bshutup"]="#~e,439,shutup,"+x+","+y+"~#"
	emote[":bsick"]="#~e,441,sick,"+x+","+y+"~#"
	emote[":bsick_1"]="#~e,440,sick_1,"+x+","+y+"~#"
	emote[":bslap"]="#~e,442,slap,"+x+","+y+"~#"
	emote[":bsleep"]="#~e,444,sleep,"+x+","+y+"~#"
	emote[":bsleepy"]="#~e,47,sleepy,"+x+","+y+"~#"
	emote[":bsleep_1"]="#~e,443,sleep_1,"+x+","+y+"~#"
	emote[":bsly"]="#~e,446,sly,"+x+","+y+"~#"
	emote[":bsmartass"]="#~e,447,smartass,"+x+","+y+"~#"
	emote[":bsmile"]="#~e,453,smile,"+x+","+y+"~#"
	emote[":bsmilewink"]="#~e,454,smilewink,"+x+","+y+"~#"
	emote[":bsmile_1"]="#~e,452,smile_1,"+x+","+y+"~#"
	emote[":bsmilie"]="#~e,458,smilie,"+x+","+y+"~#"
	emote[":bsmilie1"]="#~e,455,smilie1,"+x+","+y+"~#"
	emote[":bsmilie3"]="#~e,456,smilie3,"+x+","+y+"~#"
	emote[":bsmilie4"]="#~e,457,smilie4,"+x+","+y+"~#"
	emote[":bsmilie_osx"]="#~e,459,smilie_osx,"+x+","+y+"~#"
	emote[":bsmilie_palm"]="#~e,460,smilie_palm,"+x+","+y+"~#"
	emote[":bsmilie_tux"]="#~e,461,smilie_tux,"+x+","+y+"~#"
	emote[":bsmilie_xp"]="#~e,462,smilie_xp,"+x+","+y+"~#"
	emote[":bsmoke"]="#~e,465,smoke,"+x+","+y+"~#"
	emote[":bsmoker"]="#~e,13,smoker,"+x+","+y+"~#"
	emote[":bsmoke_1"]="#~e,464,smoke_1,"+x+","+y+"~#"
	emote[":bsmoking"]="#~e,13,smoking,"+x+","+y+"~#"
	emote[":bsmurf"]="#~e,466,smurf,"+x+","+y+"~#"
	emote[":bsm_clap"]="#~e,448,sm_clap,"+x+","+y+"~#"
	emote[":bsm_crazy"]="#~e,449,sm_crazy,"+x+","+y+"~#"
	emote[":bsm_fool"]="#~e,450,sm_fool,"+x+","+y+"~#"
	emote[":bsm_haha"]="#~e,451,sm_haha,"+x+","+y+"~#"
	emote[":bsm_lol"]="#~e,463,sm_lol,"+x+","+y+"~#"
	emote[":bsm_victory"]="#~e,467,sm_victory,"+x+","+y+"~#"
	emote[":bsm_yahoo"]="#~e,468,sm_yahoo,"+x+","+y+"~#"
	emote[":bsneaktongue"]="#~e,469,sneaktongue,"+x+","+y+"~#"
	emote[":bsneaky"]="#~e,470,sneaky,"+x+","+y+"~#"
	emote[":bsnorkel"]="#~e,471,snorkel,"+x+","+y+"~#"
	emote[":bsombrero2"]="#~e,472,sombrero2,"+x+","+y+"~#"
	emote[":bsorry"]="#~e,473,sorry,"+x+","+y+"~#"
	emote[":bspidy"]="#~e,474,spidy,"+x+","+y+"~#"
	emote[":bsp_ike"]="#~e,475,sp_ike,"+x+","+y+"~#"
	emote[":bsq_yellow_angry"]="#~e,476,sq_yellow_angry,"+x+","+y+"~#"
	emote[":bsq_yellow_arg"]="#~e,477,sq_yellow_arg,"+x+","+y+"~#"
	emote[":bsq_yellow_biggrin"]="#~e,478,sq_yellow_biggrin,"+x+","+y+"~#"
	emote[":bsq_yellow_blink"]="#~e,479,sq_yellow_blink,"+x+","+y+"~#"
	emote[":bsq_yellow_blush"]="#~e,480,sq_yellow_blush,"+x+","+y+"~#"
	emote[":bsq_yellow_closedeyes"]="#~e,481,sq_yellow_closedeyes,"+x+","+y+"~#"
	emote[":bsq_yellow_cool"]="#~e,482,sq_yellow_cool,"+x+","+y+"~#"
	emote[":bsq_yellow_cry"]="#~e,483,sq_yellow_cry,"+x+","+y+"~#"
	emote[":bsq_yellow_dry"]="#~e,484,sq_yellow_dry,"+x+","+y+"~#"
	emote[":bsq_yellow_glare"]="#~e,485,sq_yellow_glare,"+x+","+y+"~#"
	emote[":bsq_yellow_goodmood"]="#~e,486,sq_yellow_goodmood,"+x+","+y+"~#"
	emote[":bsq_yellow_happy"]="#~e,487,sq_yellow_happy,"+x+","+y+"~#"
	emote[":bsq_yellow_huh"]="#~e,488,sq_yellow_huh,"+x+","+y+"~#"
	emote[":bsq_yellow_laugh"]="#~e,489,sq_yellow_laugh,"+x+","+y+"~#"
	emote[":bsq_yellow_mellow"]="#~e,490,sq_yellow_mellow,"+x+","+y+"~#"
	emote[":bsq_yellow_notti"]="#~e,491,sq_yellow_notti,"+x+","+y+"~#"
	emote[":bsq_yellow_ohmy"]="#~e,492,sq_yellow_ohmy,"+x+","+y+"~#"
	emote[":bsq_yellow_playful"]="#~e,493,sq_yellow_playful,"+x+","+y+"~#"
	emote[":bsq_yellow_sad"]="#~e,494,sq_yellow_sad,"+x+","+y+"~#"
	emote[":bsq_yellow_sick"]="#~e,495,sq_yellow_sick,"+x+","+y+"~#"
	emote[":bsq_yellow_smile"]="#~e,496,sq_yellow_smile,"+x+","+y+"~#"
	emote[":bsq_yellow_specky"]="#~e,497,sq_yellow_specky,"+x+","+y+"~#"
	emote[":bsq_yellow_surprise"]="#~e,498,sq_yellow_surprise,"+x+","+y+"~#"
	emote[":bsq_yellow_tongue"]="#~e,499,sq_yellow_tongue,"+x+","+y+"~#"
	emote[":bsq_yellow_unhappy"]="#~e,500,sq_yellow_unhappy,"+x+","+y+"~#"
	emote[":bsq_yellow_unsure"]="#~e,501,sq_yellow_unsure,"+x+","+y+"~#"
	emote[":bsq_yellow_wink"]="#~e,502,sq_yellow_wink,"+x+","+y+"~#"
	emote[":bstrongsad"]="#~e,503,strongsad,"+x+","+y+"~#"
	emote[":bsuck"]="#~e,504,suck,"+x+","+y+"~#"
	emote[":bsumo"]="#~e,505,sumo,"+x+","+y+"~#"
	emote[":bsun_smiley"]="#~e,506,sun_smiley,"+x+","+y+"~#"
	emote[":bsuper"]="#~e,507,super,"+x+","+y+"~#"
	emote[":bsuperlol"]="#~e,508,superlol,"+x+","+y+"~#"
	emote[":bsurrender"]="#~e,509,surrender,"+x+","+y+"~#"
	emote[":bsuspect"]="#~e,510,suspect,"+x+","+y+"~#"
	emote[":bsweatdrop"]="#~e,511,sweatdrop,"+x+","+y+"~#"
	emote[":btd"]="#~e,51,td,"+x+","+y+"~#"
	emote[":bteehee"]="#~e,512,teehee,"+x+","+y+"~#"
	emote[":bthrob"]="#~e,513,throb,"+x+","+y+"~#"
	emote[":bthumb"]="#~e,515,thumb,"+x+","+y+"~#"
	emote[":bthumbdown"]="#~e,514,thumbdown,"+x+","+y+"~#"
	emote[":bthumbs-up"]="#~e,516,thumbs-up,"+x+","+y+"~#"
	emote[":bthumbsdown"]="#~e,51,thumbsdown,"+x+","+y+"~#"
	emote[":bthumbsup"]="#~e,518,thumbsup,"+x+","+y+"~#"
	emote[":bthumbup"]="#~e,517,thumbup,"+x+","+y+"~#"
	emote[":bthumb_yello"]="#~e,519,thumb_yello,"+x+","+y+"~#"
	emote[":btired"]="#~e,47,tired,"+x+","+y+"~#"
	emote[":btongue"]="#~e,523,tongue,"+x+","+y+"~#"
	emote[":btongue1"]="#~e,520,tongue1,"+x+","+y+"~#"
	emote[":btongue2"]="#~e,521,tongue2,"+x+","+y+"~#"
	emote[":btongue5"]="#~e,522,tongue5,"+x+","+y+"~#"
	emote[":btongue_ss"]="#~e,524,tongue_ss,"+x+","+y+"~#"
	emote[":btooth"]="#~e,525,tooth,"+x+","+y+"~#"
	emote[":btounge"]="#~e,11,tounge,"+x+","+y+"~#"
	emote[":btoxic"]="#~e,58,toxic,"+x+","+y+"~#"
	emote[":btrumpet"]="#~e,526,trumpet,"+x+","+y+"~#"
	emote[":btu"]="#~e,50,tu,"+x+","+y+"~#"
	emote[":bturned"]="#~e,527,turned,"+x+","+y+"~#"
	emote[":btv"]="#~e,60,tv,"+x+","+y+"~#"
	emote[":bum"]="#~e,24,um,"+x+","+y+"~#"
	emote[":bumnik"]="#~e,528,umnik,"+x+","+y+"~#"
	emote[":bunknw"]="#~e,529,unknw,"+x+","+y+"~#"
	emote[":bunlock"]="#~e,530,unlock,"+x+","+y+"~#"
	emote[":bunsure"]="#~e,531,unsure,"+x+","+y+"~#"
	emote[":bup"]="#~e,532,up,"+x+","+y+"~#"
	emote[":bv"]="#~e,535,v,"+x+","+y+"~#"
	emote[":bvertag"]="#~e,533,vertag,"+x+","+y+"~#"
	emote[":bverysad"]="#~e,534,verysad,"+x+","+y+"~#"
	emote[":bw00t"]="#~e,538,w00t,"+x+","+y+"~#"
	emote[":bw00t1"]="#~e,536,w00t1,"+x+","+y+"~#"
	emote[":bw00t2"]="#~e,537,w00t2,"+x+","+y+"~#"
	emote[":bwacko"]="#~e,539,wacko,"+x+","+y+"~#"
	emote[":bwallbash"]="#~e,540,wallbash,"+x+","+y+"~#"
	emote[":bwassat"]="#~e,541,wassat,"+x+","+y+"~#"
	emote[":bwatsup"]="#~e,542,watsup,"+x+","+y+"~#"
	emote[":bwave"]="#~e,139,wave,"+x+","+y+"~#"
	emote[":bweep"]="#~e,543,weep,"+x+","+y+"~#"
	emote[":bweight_lift"]="#~e,545,weight_lift,"+x+","+y+"~#"
	emote[":bweight_lift2"]="#~e,544,weight_lift2,"+x+","+y+"~#"
	emote[":bwhatsthat"]="#~e,546,whatsthat,"+x+","+y+"~#"
	emote[":bwheelchair"]="#~e,547,wheelchair,"+x+","+y+"~#"
	emote[":bwhistle"]="#~e,28,whistle,"+x+","+y+"~#"
	emote[":bwhistlesmile"]="#~e,548,whistlesmile,"+x+","+y+"~#"
	emote[":bwhistling"]="#~e,28,whistling,"+x+","+y+"~#"
	emote[":bwiggle"]="#~e,549,wiggle,"+x+","+y+"~#"
	emote[":bwince"]="#~e,30,wince,"+x+","+y+"~#"
	emote[":bwink"]="#~e,556,wink,"+x+","+y+"~#"
	emote[":bwink_1"]="#~e,550,wink_1,"+x+","+y+"~#"
	emote[":bwink_2"]="#~e,551,wink_2,"+x+","+y+"~#"
	emote[":bwink_3"]="#~e,552,wink_3,"+x+","+y+"~#"
	emote[":bwink_5"]="#~e,553,wink_5,"+x+","+y+"~#"
	emote[":bwink_6"]="#~e,554,wink_6,"+x+","+y+"~#"
	emote[":bwink_7"]="#~e,555,wink_7,"+x+","+y+"~#"
	emote[":bwolfwood"]="#~e,557,wolfwood,"+x+","+y+"~#"
	emote[":bwolverine"]="#~e,559,wolverine,"+x+","+y+"~#"
	emote[":bwolverine2"]="#~e,558,wolverine2,"+x+","+y+"~#"
	emote[":bwounded1"]="#~e,560,wounded1,"+x+","+y+"~#"
	emote[":bwounded2"]="#~e,561,wounded2,"+x+","+y+"~#"
	emote[":bwow"]="#~e,5,wow,"+x+","+y+"~#"
	emote[":bwub"]="#~e,563,wub,"+x+","+y+"~#"
	emote[":bwub2"]="#~e,562,wub2,"+x+","+y+"~#"
	emote[":bx"]="#~e,42,x,"+x+","+y+"~#"
	emote[":bxmas"]="#~e,564,xmas,"+x+","+y+"~#"
	emote[":byak"]="#~e,565,yak,"+x+","+y+"~#"
	emote[":byaright"]="#~e,10,yaright,"+x+","+y+"~#"
	emote[":byawn"]="#~e,566,yawn,"+x+","+y+"~#"
	emote[":byeahright"]="#~e,567,yeahright,"+x+","+y+"~#"
	emote[":byel"]="#~e,568,yel,"+x+","+y+"~#"
	emote[":byes"]="#~e,569,yes,"+x+","+y+"~#"
	emote[":byikes"]="#~e,570,yikes,"+x+","+y+"~#"
	emote[":byinyang"]="#~e,571,yinyang,"+x+","+y+"~#"
	emote[":bymca"]="#~e,572,ymca,"+x+","+y+"~#"
	emote[":byucky"]="#~e,573,yucky,"+x+","+y+"~#"
	emote[":byuk1"]="#~e,574,yuk1,"+x+","+y+"~#"
	emote[":bzip"]="#~e,575,zip,"+x+","+y+"~#"
	emote[":bzippy"]="#~e,576,zippy,"+x+","+y+"~#"
	emote[":bzoo_cat"]="#~e,577,zoo_cat,"+x+","+y+"~#"
	emote[":bzoo_donatello"]="#~e,578,zoo_donatello,"+x+","+y+"~#"
	emote[":bzoo_fox"]="#~e,583,zoo_fox,"+x+","+y+"~#"
	emote[":bzoo_fox4"]="#~e,582,zoo_fox4,"+x+","+y+"~#"
	emote[":bzoo_fox_1"]="#~e,579,zoo_fox_1,"+x+","+y+"~#"
	emote[":bzoo_fox_2"]="#~e,580,zoo_fox_2,"+x+","+y+"~#"
	emote[":bzoo_fox_3"]="#~e,581,zoo_fox_3,"+x+","+y+"~#"
	emote[":bzoo_homestar"]="#~e,584,zoo_homestar,"+x+","+y+"~#"
	emote[":bzoo_taz"]="#~e,585,zoo_taz,"+x+","+y+"~#"
	emote[":bzorro"]="#~e,586,zorro,"+x+","+y+"~#"
	emote[":b_)"]="#~e,6,_),"+x+","+y+"~#"
	emote[":b_d"]="#~e,6,_d,"+x+","+y+"~#"
	emote[":b|"]="#~e,18,|,"+x+","+y+"~#"
	emote[";)"]="#~e,2,;),"+x+","+y+"~#"
	emote["=;"]="#~e,27,=;,"+x+","+y+"~#"
	emote["=o/"]="#~e,10,=o/,"+x+","+y+"~#"
	emote["=]"]="#~e,34,=],"+x+","+y+"~#"
	emote[":b-D"]="#~e,6,-D,"+x+","+y+"~#"
	emote[":bD"]="#~e,6,D,"+x+","+y+"~#"
	emote["8D"]="#~e,5,8D,"+x+","+y+"~#"
	emote[":bG"]="#~e,260,G,"+x+","+y+"~#"
	emote[":b_D"]="#~e,6,_D,"+x+","+y+"~#"
	emote[":bP"]="#~e,11,P,"+x+","+y+"~#"
	emote[":bnoperm"]="#~u,73b49864.gif,noperm~#"
	#Basic/Premium Emotes
	emote[":b4laugh"]="#~ue,59ae42d1.gif,4laugh,"+x+","+y+"~#"
	emote[":baaliyahmad"]="#~ue,9ffa0781.jpg,aaliyahmad,"+x+","+y+"~#" 
	emote[":bariaclap1"]="#~ue,a0883253.gif,AriaNinaClap1,"+x+","+y+"~#" 
	emote[":bbackdoor"]="#~ue,8a7dfd3f.gif,backdoor,"+x+","+y+"~#" 
	emote[":bbanmebitch"]="#~ue,9cedc8f2.jpg,banmebitch,"+x+","+y+"~#"
	emote[":bbbc123"]="#~ue,06b63c1c.gif,bbc123,"+x+","+y+"~#"
	emote[":bbbcweapon"]="#~ue,3b825fc5.gif,bbcweapon,"+x+","+y+"~#"
	emote[":bbeach"]="#~ue,ef5b6dd6.gif,beach,"+x+","+y+"~#"
	emote[":bbongo1"]="#~ue,1b5125f6.gif,bongo1,"+x+","+y+"~#" 
	emote[":bboomrage"]="#~ue,7c12ff7d.gif,boomrage,"+x+","+y+"~#"
	emote[":bbouncee"]="#~ue,9007ff1e.gif,bouncee,"+x+","+y+"~#"
	emote[":bbuddy"]="#~ue,614b056e.gif,buddy,"+x+","+y+"~#"
	emote[":bbunnyballoon"]="#~ue,6e37f82f.gif,bunnyballoon,"+x+","+y+"~#"
	emote[":bbumsexy2"]="#~ue,a2c4da54.gif,bumsexy2,"+x+","+y+"~#"
	emote[":bcamera"]="#~ue,6d4d06db.gif,camera,"+x+","+y+"~#"
	emote[":bcamera2"]="#~ue,8fd678ea.gif,camera2,"+x+","+y+"~#"
	emote[":bcaptaincaveman"]="#~ue,9aed8c44.jpg,captaincaveman,"+x+","+y+"~#"
	emote[":bcatkat"]="#~ue,a05b7b92.gif,catkat,"+x+","+y+"~#"
	emote[":bchicken"]="#~ue,79935194.gif,chicken,"+x+","+y+"~#"
	emote[":bczywtf"]="#~ue,60920ccb.gif,czymwtf,"+x+","+y+"~#"
	emote[":bdayum"]="#~ue,289708d2.gif,dayum,"+x+","+y+"~#"
	emote[":bdeathcoreplz"]="#~ue,27bd790a.jpg,deathcoreplz,"+x+","+y+"~#"
	emote[":bdildoswap"]="#~ue,f727b2d3.gif,dildoswap,"+x+","+y+"~#"
	emote[":bebass1"]="#~ue,9a1e569d.jpg,ebass1,"+x+","+y+"~#"
	emote[":bebatemyfood"]="#~ue,c527381b.gif,ebatemyfood,"+x+","+y+"~#"
	emote[":bebbigmacs"]="#~ue,ce42098d.gif,ebbigmacs,"+x+","+y+"~#"
	emote[":bebday"]="#~ue,b163ca32.gif,ebday,"+x+","+y+"~#"
	emote[":bebeat"]="#~ue,db1d0034.jpg,ebeat,"+x+","+y+"~#"
	emote[":bebhorns"]="#~ue,e1c3f406.gif,ebhorns,"+x+","+y+"~#" 
	emote[":bebleovoid"]="#~ue,bdb8d740.gif,ebleovoid,"+x+","+y+"~#"
	emote[":bebpoon"]="#~ue,63010453.gif,bigebpoon,"+x+","+y+"~#" 
	emote[":bebsaggy"]="#~ue,96cbe921.gif,ebsaggy,"+x+","+y+"~#" 
	emote[":bebsuck05"]="#~ue,905bcd28.jpg,ebsuck05,"+x+","+y+"~#" 
	emote[":bebtwerk"]="#~ue,707b09fd.gif,bigebtwerk,"+x+","+y+"~#" 
	emote[":bfans"]="#~ue,d9b77f7a.gif,fans,"+x+","+y+"~#"
	emote[":bfap"]="#~ue,08daab98.gif,hugefap,"+x+","+y+"~#"
	emote[":bgrumpycat"]="#~ue,4283dfbc.jpg,grumpycat1,"+x+","+y+"~#"
	emote[":bhehe"]="#~ue,fee113a9.gif,hehe,"+x+","+y+"~#"
	emote[":bhi5"]="#~ue,589cc8c0.gif,hi5,"+x+","+y+"~#"
	emote[":bhide"]="#~ue,33dab01b.gif,hide,"+x+","+y+"~#"
	emote[":bimfuckinidiot"]="#~ue,efa982a5.gif,imfuckinidiot,"+x+","+y+"~#"
	emote[":binajar"]="#~ue,f56d4f71.gif,inajar,"+x+","+y+"~#"
	emote[":bitsdark"]="#~ue,d0f0f5d4.gif,itsdark,"+x+","+y+"~#"
	emote[":bjayzzzz"]="#~ue,3f8c67d5.gif,jayzzzz,"+x+","+y+"~#"
	emote[":bjerk0"]="#~ue,bc832e8a.gif,jerk0,"+x+","+y+"~#"
	emote[":bkarlbullshit"]="#~ue,65fa7f7d.gif,karlbullshit,"+x+","+y+"~#"
	emote[":bksclap"]="#~ue,2eb16fd0.gif,ksclap,"+x+","+y+"~#" 
	emote[":bkshammer"]="#~ue,73f893ce.gif,kshammer,"+x+","+y+"~#"
	emote[":blistentasty"]="#~ue,0f97596a.jpg,listenstasty,"+x+","+y+"~#" 
	emote[":blivfaint"]="#~ue,24fbd5c2.gif,livfaint,"+x+","+y+"~#"
	emote[":bllc"]="#~ue,0bb20cb9.gif,llc,"+x+","+y+"~#"
	emote[":blolol"]="#~ue,d6a7d304.gif,biglolol,"+x+","+y+"~#" 
	emote[":bmarielick"]="#~ue,9185bbe5.gif,marielick,"+x+","+y+"~#"
	emote[":bmdunno"]="#~ue,0547f5c1.gif,mdunno,"+x+","+y+"~#"
	emote[":bmonkeyfuck"]="#~ue,a89dcf33.gif,monkeyfuck,"+x+","+y+"~#"
	emote[":bmuseblamesrudy"]="#~ue,b5343f76.gif,museblamesrudy,"+x+","+y+"~#"
	emote[":bnaturalqueen"]="#~e,322,NaturalQueen,"+x+","+y+"~#"
	emote[":bnigger"]="#~e,355,NIGGER,"+x+","+y+"~#"
	emote[":bnormafingerdance"]="#~ue,de2f519e.gif,normafingerdance,"+x+","+y+"~#"
	emote[":boliviathumb"]="#~ue,a199cd6d.jpg,oliviathumb,"+x+","+y+"~#"
	emote[":boliviathumbzoom"]="#~ue,0557eba4.gif,oliviathumbzoom,"+x+","+y+"~#"
	emote[":bonedayy"]="#~ue,0395144f.gif,onedayy,"+x+","+y+"~#"
	emote[":bpbbt"]="#~ue,4cd8fb92.gif,pbbt,"+x+","+y+"~#"
	emote[":bpingubutt"]="#~ue,d9d3798f.gif,pingubutt,"+x+","+y+"~#" 
	emote[":bpoppyshot"]="#~ue,852790a7.gif,poppyshot,"+x+","+y+"~#"
	emote[":bpstears"]="#~ue,aac311b2.gif,pstears,"+x+","+y+"~#"
	emote[":bpumpkin1"]="#~ue,dd8616a7.gif,pumpkin1,"+x+","+y+"~#"
	emote[":brudygardener"]="#~eu,14ee066e.jpg,rudygardener,"+x+","+y+"~#"
	emote[":bsackofdicks"]="#~ue,5953bf4a.jpg,sackofdicks,"+x+","+y+"~#"
	emote[":bsadwalkwall"]="#~ue,c596f700.gif,sadwalkwall,"+x+","+y+"~#" 
	emote[":bshitface"]="#~ue,93ae5f8d.gif,shitface,"+x+","+y+"~#" 
	emote[":bskullokerbuddies"]="#~ue,1af20f8d.jpg,skullokerbuddies,"+x+","+y+"~#"
	emote[":bsljsnitches"]="#~ue,27ac5b98.gif,sljsnitches,"+x+","+y+"~#"
	emote[":bsmallfap"]="#~ue,fecbc9b4.gif,smallfap,"+x+","+y+"~#"
	emote[":bsosad3"]="#~ue,a1ea7664.gif,sosad3,"+x+","+y+"~#"
	emote[":bswingingdong"]="#~ue,3cacfa3c.gif,swingingdong,"+x+","+y+"~#"
	emote[":btakedump"]="#~ue,d319c333.gif,takedump,"+x+","+y+"~#"
	emote[":btazs"]="#~ue,1ecebf51.gif,tazs,"+x+","+y+"~#" 
	emote[":btheking"]="#~ue,80ebbeb4.gif,theking,"+x+","+y+"~#"
	emote[":btipcrime"]="#~ue,cb53536f.gif,tipcrime,"+x+","+y+"~#"
	emote[":btrollface"]="#~ue,8fea360a.jpg,trollface,"+x+","+y+"~#"
	emote[":bturkchain"]="#~ue,b69c8867.gif,turkchain,"+x+","+y+"~#"
	emote[":bturkchain2"]="#~ue,dee44895.gif,turkchain2,"+x+","+y+"~#"
	emote[":bzippyw"]="#~ue,0138e90f.gif,zippyw,"+x+","+y+"~#"
	emote[":bzippyseizure"]="#~ue,c6eba178.gif,zippyseizure,"+x+","+y+"~#"
	emote[":bzombiebrain"]="#~ue,b9c2d3a0.gif,zombiebrain,"+x+","+y+"~#"


def cli_out (f_arg, *argv):
	msg=f_arg
	for arg in argv:
		msg=msg+arg
	print (msg)

class guest_client(WebSocketBaseClient):
	def handshake_ok(self): 
		#self.main_session=self.userdata[0]
		self.is_joined_room=0
		self.main_session.gbot.add(self)
		self.ws=self.main_session.gbot.websockets[self.sock.fileno()]
		self.ws.send("hello fcserver\n\0")
		self.ws.send("1 0 0 20071025 0 guest:guest\n\0")
		self.main_session.gcount=self.main_session.gcount+1

	def received_message (self,data):
		if self.is_joined_room == 1:
			return
		i=1
		data=str(data)
		while i==1:
			hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", data)
			if bool(hdr) == 0:
				cli_out ("error: parse_response failed %s" % data)
				break
			msgtype = hdr.group(1)
			msg_len=int(msgtype[0:4])
			msgtype=int(msgtype[4:])
			Message=data[4:4+msg_len]
			Message=urllib.unquote(Message)
			if msgtype == 1:
				self.main_session.join_room (self.ws)
			elif msgtype == 5:
				Message=Message[Message.find("{")+1:]
				dump=re.match(r'(\"lv\"):(?P<LEVEL>\d+),(\"nm\"):(?P<NAME>.+?),(\"sid\"):(?P<SID>\d+)', Message)
				if bool(dump):
					guest_name=dump.group('NAME')
					self.Name=guest_name
					s_id=int(dump.group('SID'))
					self.main_session.GuestsSID[guest_name]=[self.ws, s_id]
				self.is_joined_room=1
			#process next message
			data=data[4+msg_len:]
			if len(data) == 0:
				break

	def connection_closed(self):
		if self.Name==None:
			return
		try:
			del self.main_session.GuestsSID[self.Name]
		except KeyError:
			pass
		if self.is_joined_room == 1:
			self.main_session.gcount=self.main_session.gcount-1
			self.main_session.g_conn_count -= 1
			cli_out("Removed guest %s from %s room (%d)\n" % 
				(self.Name, self.main_session.model_name, self.main_session.g_conn_count))

def main_keep_alive():
	while True:
		s_time=(math.floor(10 * random.random()) + 10)
		time.sleep(s_time);
		try:
       			for ws in main_session.websockets.itervalues():
				if not ws.terminated:
					try:	
						ws.send("0 0 0 0 0 -\n\0")
					except:
						e, t, tb = sys.exc_info()
						print("Closing session to %s(%d) %s" 
							% (self.model_name, self.index, t))
		except:
			pass

class mfcsession(WebSocketBaseClient):
	def handshake_ok(self): 
		global gindex
		global gpasscode
		global guser
		self.gbot=None
		self.g_conn_count = 0
		main_session.add(self)
		self.model_name = self.userdata[0]
		self.ws_main=main_session.websockets[self.sock.fileno()]
		self.mchanid = 0
		self.total_tips = 0
		self.tippers={}
		self.reconnect=0
		self.gbot_ka_thr=None
		self.index=gindex
		self.modeluid=-1
		self.state="OFFLINE"
		self.m_index=0
		self.message_Q=collections.deque(maxlen=25)
		gindex += 1
		try:
			re_conn=self.userdata[1]
		except IndexError:
			re_conn=0

		if re_conn != 0:
			self.tippers = self.userdata[2]
			self.total_tips = self.userdata[3]
			self.reconnect=1
			
		self.sess_id=0
		self.user_level=0
		self.Incomplete_Buf=""
		self.gcount=0
		self.is_joined_room=0
		self.members = {}
		self.ignoredusers = []
		self.GuestsSID={}
		self.rank=0
		self.guests_count=0
		self.enable_dbg=0
		self.session_IO=0
		self.connected_on=datetime.datetime.utcnow().strftime("%H:%M:%S %b %d,%Y")+" UTC"
		file_name=self.model_name+"-"+str(datetime.datetime.utcnow().strftime("%H-%M-%S-%b-%d-%Y"))+"-UTC.txt"
		self.token_log = open("token_logs/"+file_name,'w+')
		self.start = int(time.time())
		self.ws_main.send("hello fcserver\n\0")
		self.ws_main.send("1 0 0 20071025 0 "+guser+":"+gpasscode+"\n\0")
		self.user_terminated=0
		self.gcount=self.gcount+1

	def close_session(self):
		self.ws_main.send("98 0 0 0 0 -\n\0")
		self.user_terminated=1
		self.session_IO=0
		self.ws_main.close()

	def connection_closed(self):
		global client
		if self.Name==None:
			return
		cli_out(fg.green+"Connection to \"%s\" (%s) closed%s\n" % (self.model_name, self.Name, attr.reset))
		del self.GuestsSID['"'+self.Name+'"']
		self.gcount=self.gcount-1
		self.g_conn_count=self.g_conn_count-1

		now = int(time.time())
		self.guests_remove (-1)
		cli_out (fg.red+"*** Session Details ***"+attr.reset)
		cli_out("Tokens          : %-05d" % self.total_tips)
		people_count=len(self.members.keys())
		cli_out("Premiums/Basics : %-05d" % people_count)
		cli_out("Guests          : %-05d" % self.guests_count)
		cli_out("Active for      : %-05s(hrs:mins:secs)" % 
			str(datetime.timedelta(seconds=now-self.start)))
		self.show_tip_details()
		self.write_tip_details()
		self.token_log.close()
#		self.user_terminated=1
		self.session_IO=0
		cli_out(fg.red+attr.bold+"Closed %s's session ...%s" 
			% (self.model_name, attr.reset))
		time.sleep(1)
		if self.gbot_ka_thr != None:
			self.gbot.close_all()
			self.gbot.stop()
			self.gbot_ka=0

		time.sleep(1)
		try:
			client.remove(self)
		except ValueError:
			pass
		if self.user_terminated == 0:
			cli_out(fg.green+"Re-Connecting to %s ... %s" % (self.model_name, attr.reset))
			host = get_chat_host()
		       	session = mfcsession(host, userdata=[self.model_name, 1, self.tippers, self.total_tips])
			session.guest_name=None
			try:
				session.connect ()
			except:
				e, t, tb = sys.exc_info()
				print("Could not connect guest session to \"%s\"" % (t))
		del self

	def run_guest_cli_keep_alive(self):
		while self.gbot_ka == 1:
			s_time=(math.floor(10 * random.random()) + 10)
			time.sleep(s_time);
			try:
				for ws in self.gbot.websockets.itervalues():
					if not ws.terminated:
						try:	
							ws.send("0 0 0 0 0 -\n\0")
						except:
							e, t, tb = sys.exc_info()
							print("Closing guest session to %s(%d) %s" 
								% (self.model_name, self.index, t))
							ws.close()
			except:
				pass
	def __del__(self):
		class_name = self.__class__.__name__
		pass

	def cli_out (self, f_arg, *argv):
		if self.session_IO == 0:
			return
		msg=f_arg
		for arg in argv:
			msg=msg+arg
		print msg

	def tip_msg(self, m):
		buf=""
		lbuf=""
		msg_pattern = \
                	r"(\d+) (\d+) (\d+) (\d+) (\d+) " + \
	                r"{(\"\w+\"):(\d+),(\"\w+\"):(\d+)(\,)" + \
        	        r"(\"\m\")(\:)(\[)(\d+),(\d+),(?P<Model>\"\w+\")(\])," + \
                	r"(\"msg\"):(?P<tipnote>.+?)," + \
	                r"(\"sesstype\"):(\d+),(\"\w+\"):(\d+),(\"\w+\"):(?P<tokens>\d+)," + \
        	        r"(\"\u\")(\:)(\[)(\d+),(?P<uid>\d+),(?P<Member>\"\w+\")(\])}"

		pattern = \
			r"(\d+) (\d+) (\d+) (\d+) (\d+) " + \
			r"(\{)(\w+):(\d+),(\w+):(\d+)(\,)" + \
			r"(\m)(\:)(\[)(\d+),(\d+),(?P<Model>\w+)(\])," + \
			r"(\w+):(\d+),(\w+):(\d+),(\w+):(?P<tokens>\d+)," + \
			r"(\u)(\:)(\[)(\d+),(?P<uid>\d+),(?P<Member>\w+)(\])"

		hdr=re.match (msg_pattern , m)
		if bool(hdr):
			buf="%s%s%s%s has tipped %s %s tokens: '%s'%s" % (attr.bold, fg.green,
			       bg.red, hdr.group('Member').replace('"', ''), hdr.group('Model').replace('"', ''), 
			       hdr.group('tokens'), hdr.group('tipnote').replace('"', ''), attr.reset)
			lbuf="%s has tipped %s %s tokens: '%s'" % (
			       hdr.group('Member').replace('"', ''), hdr.group('Model').replace('"', ''), 
			       hdr.group('tokens'), hdr.group('tipnote').replace('"', ''))

		else:
			m=m.replace('"', '')
			hdr=re.match (pattern , m)
			buf="%s%s%s%s has tipped %s %s tokens%s" % (attr.bold, fg.green,
			    bg.red, hdr.group('Member'), hdr.group('Model'), hdr.group('tokens'), attr.reset)

			lbuf="%s has tipped %s %s tokens" % (hdr.group('Member'), hdr.group('Model'), 
								hdr.group('tokens'))

		self.cli_out (buf)
		self.token_log.write (lbuf)
		self.token_log.write ("\n")
		self.token_log.flush()
		tipped=int(hdr.group('tokens'))
		self.total_tips += tipped
		member=hdr.group('Member').replace('"', '')
		try:
			tips=self.tippers[member]
		except KeyError:
			self.tippers[member]=0

		tips=self.tippers[member]
		tips += tipped
		self.tippers[member]=tips

		userid=hdr.group('uid')
		mem_entry=db_get(db_members, db_ml, userid)
		if mem_entry==None:
			u_data=[member, 2 , tipped, "NA", "NA", "NA"]
			db_add(db_members, db_ml, userid, u_data) 
			db_sync(db_members, db_ml)
		else:
			mem_entry[2] += tipped
			db_update (db_members, db_ml, userid, mem_entry)
			if not member in mem_entry:
				db_append (db_members, db_ml, userid, member)
			db_sync(db_members, db_ml)

		mem_entry=db_get(db_models, db_wl, str(self.modeluid))
		if mem_entry!=None:
			mem_entry[2] += tipped
			db_update (db_models, db_wl, str(self.modeluid), mem_entry)
			db_sync(db_models, db_wl)


	def process_FCServer_msg(self, m, chat_opt):
		fcsrv_pattern = \
			r"(\d+) (\d+) (\d+) (\d+) (\d+) " + \
			r"{(\"\w+\"):(\d+)," + \
			r"(\"\w+\"):(\d+)," + \
			r"(\"\w+\"):(\"\w+\")," + \
			r"(\"\w+\"):(\-\d+)," + \
			r"(\"\w+\"):(\d+)," +\
			r"(\"\w+\"):(?P<MSG>.+?)}" 

		hdr=re.match (fcsrv_pattern , m)
		if bool(hdr):
			if chat_opt==32:
				buf="%sTOPIC: %s%s%s%s" % (fg.green, attr.reset, 
					 fg.red,
					hdr.group('MSG').replace('"','')
					,attr.reset)
			else:
				buf="%s%s%s" % (fg.red, hdr.group('MSG').replace('"',''), attr.reset)
			self.cli_out(buf)
		else:
			fcsrv_pattern = \
				r"(\d+) (\d+) (\d+) (\d+) (\d+)"
			hdr=re.match (fcsrv_pattern , m)
			if bool(hdr):
				info=hdr.group(0).split(' ')
				if info[3] == '1' and info[4] == '4':
					if self.user_level==0:
						self.cli_out(fg.green+g_mute+attr.reset)
					if self.user_level==1:
						self.cli_out(fg.green+b_mute+attr.reset)
	def update_user_info(self, m):
		m=m[m.find("{")+1:]
		dump=re.match(r'(\"lv\"):(?P<LEVEL>\d+),(\"nm\"):(?P<NAME>.+?),(\"sid\"):(?P<SID>\d+)', m)
		if bool(dump):
			guest_name=dump.group('NAME')
			self.Name=guest_name.replace('"', '')
			s_id=int(dump.group('SID'))
			self.GuestsSID[guest_name]=[self.ws_main ,s_id]
			self.user_level=int(dump.group('LEVEL'))

	def process_chat_message(self, ws, m):
		cmsg_pattern = \
			r"(\d+) (\d+) (\d+) (\d+) (\d+) " + \
			r"{(\"\w+\"):(?P<LEVEL>\d+)," + \
			r"(\"\w+\"):(?P<MSG>.+?)," + \
			r"(\"\w+\"):(?P<NAME>.+?)," + \
			r"(\"\w+\"):(?P<SESSIONID>\d+)," + \
			r"(\"\w+\"):(?P<USERID>\d+),"

		hdr=re.match (cmsg_pattern , m)
		if bool(hdr):
			usrid=hdr.group('USERID')
			if usrid in self.ignoredusers:
				return
			usr=hdr.group('NAME')[1:-1]
			lvl=int(hdr.group('LEVEL'))
			fmt="%s%-12s%s: %s%s%s"
			msg=(hdr.group('MSG'))
			msg=msg[1:-1]
			msg=msg.replace('&quot;', '"')
			msg=msg.replace('\\"', '"')
			msg=textwrapper.fill(msg)
			#msg=update_code_2_emote(msg)
			buf=""
			if lvl == 4:
				buf=fmt % (fg.magenta + attr.bold, usr, attr.reset, fg.red, msg,attr.reset)
			elif lvl == 2:
				buf=fmt % (fg.cyan , usr, attr.reset, fg.green, msg,attr.reset)
			elif lvl == 1:
				buf=fmt % (fg.yellow , usr, attr.reset, fg.cyan, msg,attr.reset)
			elif lvl == 0:
				buf=fmt % (fg.red, usr, "", fg.yellow , msg,attr.reset)
			self.message_Q.append(buf)
			self.cli_out (buf)
		else:
			print "error chat msg", m

	def leave_channel(self, m):
		cmsg_pattern = \
			r"(\d+) (?P<SID>\d+) (\d+) (\d+) (\d+)"

		hdr=re.match (cmsg_pattern , m)
		if bool(hdr):
			fmt="%s has left %s%s's%s room"
			sid=hdr.group('SID')
			for usr, [lvl, s_sid, userid] in sorted(self.members.items(),  reverse=True):
				if s_sid==sid:
					del self.members[usr]
					if lvl == 4:
						if self.modeluid==int(userid):
							m="{"+m
							self.process_user_info(m, 0)
						usr=fg.magenta + attr.bold + usr+"("+userid+")" + attr.reset
					elif lvl == 2:
						usr=fg.cyan + usr+"("+userid+")" + attr.reset
					elif lvl == 1:
						usr=fg.yellow + usr+"("+userid+")" + attr.reset
					elif lvl == 0:
						usr=fg.red + usr+"("+userid+")" + attr.reset
					buf=fmt % (usr, fg.red, self.model_name,attr.reset)
					if self.enable_dbg == 1:
						self.cli_out (buf)
					break
		else:
			print "error leave chan", m

	def join_channel(self, m):
		global db_members
		m=m[m.find("{")+1:]
		dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{(?P<USERINFO>.+?)}}', m)
		if bool(dump):
			s_info=dump.group('SESSION_INFO')
			session_info = dict(s_info.split(":") for s_info in s_info.split(","))
			try:
				usr=session_info['"nm"']
			except KeyError:
				return
			usr=usr.replace('"', '')
			lvl=int(session_info['"lv"'])
			userid=(session_info['"uid"'])
			session_id=(session_info['"sid"'])

			u_info=dump.group('USERINFO')
			if u_info.find("\"age\":") != -1:
				age=(u_info[u_info.find("\"age\":")+len("\"age\":"):].split(",")[0])
			else:
				age=None

			if u_info.find("\"country\":") != -1:
				Country=(u_info[u_info.find("\"country\":")+len("\"country\":"):].split(",")[0]).replace('"','')
			else:
				Country=None

			if u_info.find("\"creation\":") != -1:
				timestamp=int(u_info[u_info.find("\"creation\":")+len("\"creation\":"):].split(",")[0].replace('}',''))
				acct=time.strftime("%H:%M:%S %b %d,%Y", time.gmtime(timestamp))+" UTC"
			else:
				acct=None

			fmt="%s has joined %s%s's%s room"

			self.members[usr]=[lvl ,session_id, userid]
			mem_entry=db_get(db_members, db_ml, userid)
			if mem_entry==None:
				u_data=[usr, lvl ,0, age, Country, acct]
				db_add(db_members, db_ml, userid, u_data) 
				db_sync(db_members, db_ml)
			else:
				if mem_entry[5] == "NA":
					mem_entry[5]=acct
					db_sync(db_members, db_ml)
				if not usr in mem_entry:
					db_append (db_members, db_ml, userid, usr)
					db_sync(db_members, db_ml)
			if lvl == 4:
				if self.modeluid==int(userid):
					if self.model_name != usr:
						self.model_name=usr
					m="{"+m
					self.process_user_info(m, 0)
				usr=fg.magenta + attr.bold + usr+"("+userid+")" + attr.reset
			elif lvl == 2:
				usr=fg.cyan + usr+"("+userid+")" + attr.reset
			elif lvl == 1:
				usr=fg.yellow + usr+"("+userid+")" + attr.reset
			elif lvl == 0:
				usr=fg.red + usr+"("+userid+")" + attr.reset
			buf=fmt % (usr, fg.red, self.model_name,attr.reset)
			if self.enable_dbg == 1:
				self.cli_out(buf)

	def process_room_data(self, msg):
		msg=msg[msg.find("{")+1:]
		if msg.find("\"countdown\":") != -1:
			countdown=(msg[msg.find("\"countdown\":")+len("\"countdown\":"):].split(",")[0])
			if countdown=="true":
				countdown=1
			else:
				countdown=0
		else:
			return

		if msg.find("\"sofar\":") != -1:
			sofar=msg[msg.find("\"sofar\":")+len("\"sofar\":"):].split(",")[0]

		if msg.find("\"total\":") != -1:
			total=msg[msg.find("\"total\":")+len("\"total\":"):].split(",")[0].replace('}','')

		if countdown==1:
			self.cli_out(fg.red+"%s's countdown @ %s/%s%s" % (self.model_name, sofar, total, attr.reset))
		else:
			self.cli_out(fg.red+"%s's countdown Stopped: %s/%s%s" %(self.model_name, sofar, total, attr.reset))


	def process_session_state_change (self, msg, uid):
		dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{(?P<USERINFO>.+?)},"m":{(?P<MODELINFO>.+?)}}', msg)
		if bool(dump):
			s_info=dump.group('SESSION_INFO')
			m_info=dump.group('MODELINFO')
			u_info=dump.group('USERINFO')

			session_info = dict(s_info.split(":") for s_info in s_info.split(","))
			model_id=str(int(session_info['"uid"']))

			try:
				modelinfo = dict(m_info.split(":") for m_info in m_info.split(","))
			except ValueError:
				return
			try:
				v_state=int(session_info['"vs"'])
			except KeyError:
				pass

			if uid==self.modeluid:
				try:
					self.show_model_video_state (int(session_info['"vs"']), 0)
				except KeyError:
					pass

				if m_info != None and m_info.find("\"rank\":") != -1:
					rank=(m_info[m_info.find("\"rank\":")+len("\"rank\":"):].split(",")[0])
					rank=int(rank)
					if rank != self.rank:
						cli_out(fg.green+"%s's rank changed from %d to %d%s"
							% (self.model_name, self.rank, rank, attr.reset))
						self.rank=rank 


	def process_online_model_session_state(self, msg, display, uid):
		global db_models
		msg=msg[msg.find("{")+1:]
		dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{(?P<USERINFO>.+?)},"m":{(?P<MODELINFO>.+?)}}', msg)
		if bool(dump):
			s_info=dump.group('SESSION_INFO')
			session_info = dict(s_info.split(":") for s_info in s_info.split(","))
			model_id=str(int(session_info['"uid"']))
			try:
				name=session_info['"nm"']
			except KeyError:
				self.process_session_state_change (msg, uid)
				return

			m_info=dump.group('MODELINFO')
			topic_dump=re.search(r'"topic":(?P<TOPIC>.+?)}', m_info)
			if bool(topic_dump):
				topic=topic_dump.group(0)
				topic=topic[topic.find("\"topic\":")+len("\"topic\":"):].replace('"', '')
				m_info=m_info[:m_info.find(",\"topic\"")]
			else:
				topic="TOPIC: none"
			try:
				modelinfo = dict(m_info.split(":") for m_info in m_info.split(","))
			except ValueError:
				return
			flags=int(modelinfo['"flags"'])
			missmfc=(modelinfo['"missmfc"'])

			try:
				hide_camscore=modelinfo['"hidecs"']
				if hide_camscore  == "true":
					hide_camscore="(model hides camscore)"
			except KeyError:
				hide_camscore=""

			u_info=dump.group('USERINFO')
			if u_info.find("\"age\":") != -1:
				age=(u_info[u_info.find("\"age\":")+len("\"age\":"):].split(",")[0])
			else:
				age="NA"
			if u_info.find("\"ethnic\":") != -1:
				Ethnic=(u_info[u_info.find("\"ethnic\":")+len("\"ethnic\":"):].split(",")[0])
			else:
				Ethnic="NA"
			if u_info.find("\"country\":") != -1:
				Country=(u_info[u_info.find("\"country\":")+len("\"country\":"):].split(",")[0])
			else:
				Country="NA"

			if u_info.find("\"creation\":") != -1:
				timestamp=int(u_info[u_info.find("\"creation\":")+len("\"creation\":"):].split(",")[0])
				acct=time.strftime("%H:%M:%S %b %d,%Y", time.gmtime(timestamp))+" UTC"
			else:
				acct="NA"

			if u_info.find("\"camserv\":") != -1:
				Camserv=(u_info[u_info.find("\"camserv\":")+len("\"camserv\":"):].split(",")[0])
			else:
				Camserv=0

			Camserv = int(Camserv)
		
			if Camserv >= 500:
				Camserv = Camserv - 500

			chan_id=100000000+int(model_id)
			new_model=int(modelinfo['"new_model"'])

			if new_model == 1:
				new_model=" *NEW MODEL*"
			else:
				new_model=""

			usr=session_info['"nm"'].replace('"','')
			continent=modelinfo['"continent"'].replace('"','')
			try:
				cs=float(modelinfo['"camscore"'])
			except KeyError:
				cs=0
			country=Country.replace('"','')
			v_state=int(session_info['"vs"'])
			if Camserv == 0:
				v_state=90
			rank=modelinfo['"rank"']
			ethn= Ethnic.replace('"','')
			topic=topic.replace('}','')
			m_data=[usr, new_model, v_state, age, acct, cs, rank, ethn, country, continent, Camserv, flags, topic]
			online_models[model_id]=m_data

			mem_entry=db_get(db_models, db_wl, model_id)
			if mem_entry==None:
									  # cur, lest, best
				u_data=[usr, model_id, 0, missmfc, age, acct, country, continent, cs, cs, cs]
				db_add(db_models, db_wl, model_id, u_data) 
				db_sync(db_models, db_wl)
			else:
				if not usr in mem_entry:
					db_append (db_models, db_wl, model_id, usr)
					db_sync(db_models, db_wl)
				if cs > 0:
					if mem_entry[9] > cs:
						mem_entry[9]=cs
					elif mem_entry[10] < cs:
						mem_entry[10]=cs
					if mem_entry[8] != cs:
						mem_entry[8]=cs
						db_update(db_models, db_wl, model_id, mem_entry)
						db_sync(db_models, db_wl)
		else:
			session_info=None
			m_info=None
			dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{', msg)
			if bool(dump):
				s_info=dump.group('SESSION_INFO')
				session_info = dict(s_info.split(":") for s_info in s_info.split(","))
				model_id=str(int(session_info['"uid"']))
				try:
					v_state=int(session_info['"vs"'])
				except KeyError:
					pass
			
			dump=re.match(r'(?P<SESSION_INFO>.+?),"m":{(?P<MODELINFO>.+?)}}', msg)
			if bool(dump):
				s_info=dump.group('SESSION_INFO')
				session_info = dict(s_info.split(":") for s_info in s_info.split(","))
				m_info=dump.group('MODELINFO')
				topic_dump=re.search(r'"topic":(?P<TOPIC>.+?)}', m_info)
				if bool(topic_dump):
					topic=topic_dump.group(0)
					topic=topic[topic.find("\"topic\":")+len("\"topic\":"):].replace('"', '')
					m_info=m_info[:m_info.find(",\"topic\"")]

				model_id=str(int(session_info['"uid"']))
				chan_id=100000000+int(model_id)
				try:
					v_state=int(session_info['"vs"'])
				except KeyError:
					pass

	def process_session_state(self, msg, display, uid):
		global db_models
		msg=msg[msg.find("{")+1:]
		dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{(?P<USERINFO>.+?)},"m":{(?P<MODELINFO>.+?)}}', msg)
		if bool(dump):
			s_info=dump.group('SESSION_INFO')
			session_info = dict(s_info.split(":") for s_info in s_info.split(","))
			try:
				name=session_info['"nm"']
			except KeyError:
				self.process_session_state_change(msg, uid)
				return

			m_info=dump.group('MODELINFO')
			topic_dump=re.search(r'"topic":(?P<TOPIC>.+?)}', m_info)
			if bool(topic_dump):
				topic=topic_dump.group(0)
				topic=topic[topic.find("\"topic\":")+len("\"topic\":"):].replace('"', '')
				m_info=m_info[:m_info.find(",\"topic\"")]
			else:
				topic="TOPIC: none"
			modelinfo = dict(m_info.split(":") for m_info in m_info.split(","))
			flags=int(modelinfo['"flags"'])
			missmfc=(modelinfo['"missmfc"'])

			try:
				hide_camscore=modelinfo['"hidecs"']
				if hide_camscore  == "true":
					hide_camscore="(model hides camscore)"
			except KeyError:
				hide_camscore=""

			u_info=dump.group('USERINFO')
			if u_info.find("\"age\":") != -1:
				age=(u_info[u_info.find("\"age\":")+len("\"age\":"):].split(",")[0])
			else:
				age="NA"
			if u_info.find("\"ethnic\":") != -1:
				Ethnic=(u_info[u_info.find("\"ethnic\":")+len("\"ethnic\":"):].split(",")[0])
			else:
				Ethnic="NA"
			if u_info.find("\"country\":") != -1:
				Country=(u_info[u_info.find("\"country\":")+len("\"country\":"):].split(",")[0])
			else:
				Country="NA"

			if u_info.find("\"creation\":") != -1:
				timestamp=int(u_info[u_info.find("\"creation\":")+len("\"creation\":"):].split(",")[0])
				acct=time.strftime("%H:%M:%S %b %d,%Y", time.gmtime(timestamp))+" UTC"
			else:
				acct="NA"

			if u_info.find("\"camserv\":") != -1:
				Camserv=(u_info[u_info.find("\"camserv\":")+len("\"camserv\":"):].split(",")[0])
			else:
				Camserv=0

			Camserv = int(Camserv)
		
			if Camserv >= 500:
				Camserv = Camserv - 500

			model_id=str(int(session_info['"uid"']))
			chan_id=100000000+int(model_id)
			new_model=int(modelinfo['"new_model"'])

			if new_model == 1:
				new_model=" *NEW MODEL*"
			else:
				new_model=""

			usr=session_info['"nm"'].replace('"','')
			continent=modelinfo['"continent"'].replace('"','')
			try:
				cs=float(modelinfo['"camscore"'])
			except KeyError:
				cs=0
				
			country=Country.replace('"','')
			v_state = int(session_info['"vs"'])
			truepvt = ((flags & 8) == 8)

			if Camserv == 0:
				v_state=90

			if display == 1:
				print "\nName           : ", usr, new_model
				print "Age            : ", age
				print "Created on     : ", acct
				print "CamScore       : ", cs, hide_camscore
				print "CurrentRank    : ", modelinfo['"rank"']
				print "Miss MFC       : ", missmfc
				print "Ethnic         : ", Ethnic.replace('"','')
				print "Country        : ", country
				print "Continent      : ", continent
				print "User ID        : ", model_id
				print "Video Server   : ", Camserv
				try:
					if truepvt == 1:
						self.state="TRUEPVT"
					else:
						self.state=video_state[v_state]
					print "Video State    : ", self.state
				except KeyError:
					self.state="Unknown"
					print "Unknown"
				print "Topic          : ", topic.replace('}','')
				buf=""
				guest = flags & 4096
				basic = flags & 8192
				if guest:
					buf = "Guests"
				if basic:
					if guest:
						buf=buf+"/"
					buf = buf+"Basics"
				if guest or basic:
					print ("%-15s:  Muted" % buf)
				Url="http://video"+str(Camserv)+".myfreecams.com:1935/NxServer/mfc_"+str(chan_id)+".f4v_aac/playlist.m3u8"
				if Camserv != 0:
					print "Video Stream   : ", Url

			self.show_model_video_state (v_state, truepvt)
			mem_entry=db_get(db_models, db_wl, model_id)
			if mem_entry==None:
									  # cur, lest, best
				u_data=[usr, model_id, 0, missmfc, age, acct, country, continent, cs, cs, cs]
				db_add(db_models, db_wl, model_id, u_data) 
				db_sync(db_models, db_wl)
			else:
				if not usr in mem_entry:
					db_append (db_models, db_wl, model_id, usr)
					db_sync(db_models, db_wl)
				if cs > 0:
					if mem_entry[9] > cs:
						mem_entry[9]=cs
					elif mem_entry[10] < cs:
						mem_entry[10]=cs
					if mem_entry[8] != cs:
						mem_entry[8]=cs
						db_update(db_models, db_wl, model_id, mem_entry)
						db_sync(db_models, db_wl)
		else:
			session_info=None
			m_info=None
			dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{', msg)
			if bool(dump):
				s_info=dump.group('SESSION_INFO')
				session_info = dict(s_info.split(":") for s_info in s_info.split(","))
			
			dump=re.match(r'(?P<SESSION_INFO>.+?),"m":{(?P<MODELINFO>.+?)}}', msg)
			if bool(dump):
				s_info=dump.group('SESSION_INFO')
				session_info = dict(s_info.split(":") for s_info in s_info.split(","))
				m_info=dump.group('MODELINFO')
			
			try:
				self.show_model_video_state (int(session_info['"vs"']), 0)
			except KeyError:
				pass

			if m_info != None and m_info.find("\"rank\":") != -1:
				rank=(m_info[m_info.find("\"rank\":")+len("\"rank\":"):].split(",")[0])
				rank=int(rank)
				if rank != self.rank:
					cli_out(fg.green+"%s's rank changed from %d to %d%s"
						% (self.model_name, self.rank, rank, attr.reset))
					self.rank=rank 

	def show_model_video_state (self, st, tp):
		try:
			if tp == 1:
				state = "TRUEPVT"
			else:
				state=video_state[st]
			if state != self.state:
				if st == 0 or st == 12 or st == 13:
					self.cli_out(fg.red+attr.bold+"%s is in %s%s" 
						% (self.model_name, state, attr.reset))
				elif st == 90:
					self.cli_out(fg.red+attr.bold+"%s's %s%s" 
						% (self.model_name, state, attr.reset))
				elif st == 127:
					self.cli_out(fg.red+attr.bold+"%s went %s%s" 
						% (self.model_name, state, attr.reset))
				elif st == 2:
					self.cli_out(fg.red+attr.bold+"%s is %s%s" 
						% (self.model_name, state, attr.reset))
			self.state=state
		except KeyError:
			pass

	def process_user_info(self, msg, response_code):
		msg=msg[msg.find("{")+1:]
		dump=re.match(r'(?P<SESSION_INFO>.+?),"u":{(?P<USERINFO>.+?)},"m":{(?P<MODELINFO>.+?)}}', msg)
		if bool(dump):
			s_info=dump.group('SESSION_INFO')
			session_info = dict(s_info.split(":") for s_info in s_info.split(","))

			m_info=dump.group('MODELINFO')
			topic=m_info[m_info.find("\"topic\":")+len("\"topic\":"):].replace('"', '')
			m_info=m_info[:m_info.find(",\"topic\"")]
			modelinfo = dict(m_info.split(":") for m_info in m_info.split(","))
			flags=int(modelinfo['"flags"'])
			missmfc=int(modelinfo['"missmfc"'])

			try:
				hide_camscore=modelinfo['"hidecs"']
				if hide_camscore  == "true":
					hide_camscore="(model hides camscore)"
			except KeyError:
				hide_camscore=""

			u_info=dump.group('USERINFO')
			if u_info.find("\"age\":") != -1:
				age=(u_info[u_info.find("\"age\":")+len("\"age\":"):].split(",")[0])
			else:
				age="NA"
			if u_info.find("\"ethnic\":") != -1:
				Ethnic=(u_info[u_info.find("\"ethnic\":")+len("\"ethnic\":"):].split(",")[0])
			else:
				Ethnic="NA"
			if u_info.find("\"country\":") != -1:
				Country=(u_info[u_info.find("\"country\":")+len("\"country\":"):].split(",")[0])
			else:
				Country="NA"

			if u_info.find("\"creation\":") != -1:
				timestamp=int(u_info[u_info.find("\"creation\":")+len("\"creation\":"):].split(",")[0])
				acct=time.strftime("%H:%M:%S %b %d,%Y", time.gmtime(timestamp))+" UTC"
			else:
				acct="NA"

			if u_info.find("\"camserv\":") != -1:
				Camserv=(u_info[u_info.find("\"camserv\":")+len("\"camserv\":"):].split(",")[0])
			else:
				Camserv=500
			model_id=int(session_info['"uid"'])+100000000
			uid=session_info['"uid"']
			new_model=int(modelinfo['"new_model"'])

			if new_model == 1:
				new_model=" *NEW MODEL*"
			else:
				new_model=""

			Camserv = int(Camserv)
		
			if Camserv >= 500:
				Camserv = Camserv - 500

			usr=session_info['"nm"'].replace('"','')
			continent=modelinfo['"continent"'].replace('"','')
			try:
				cs=float(modelinfo['"camscore"'])
			except KeyError:
				cs=0
			country=Country.replace('"','')
			ethic=Ethnic.replace('"','')
			self.rank=int(modelinfo['"rank"'])
			guest = flags & 4096
			basic = flags & 8192
			truepvt = flags & 8

			print "\nName           : ", usr, new_model
			print "Age            : ", age
			print "Created on     : ", acct
			print "CamScore       : ", cs, hide_camscore
			print "CurrentRank    : ", modelinfo['"rank"']
			print "Miss MFC       : ", missmfc
			print "Ethnic         : ", ethic
			print "Country        : ", country
			print "Continent      : ", continent
			print "User ID        : ", model_id
			print "Video Server   : ", Camserv
			try:
				if truepvt == 8:
					print "Video State    : ", "TRUEPVT"
					self.state = "TRUEPVT"
				else:
					print "Video State    : ", video_state[int(session_info['"vs"'])]
					self.state=video_state[int(session_info['"vs"'])]
			except KeyError:
				self.state="Unknown"
				print "Unknown"
			print "Topic          : ", topic
			buf=""
			if guest:
				buf = "Guests"
			if basic:
				if guest:
					buf=buf+"/"
				buf = buf+"Basics"
			if guest or basic:
				print ("%-15s:  Muted" % buf)
			Url="http://video"+str(Camserv)+".myfreecams.com:1935/NxServer/mfc_"+str(model_id)+".f4v_aac/playlist.m3u8"
			if Camserv != 0:
				print "Video Stream   : ", Url

			mem_entry=db_get(db_models, db_wl, uid)
			if mem_entry==None:
									  # cur, lest, best
				u_data=[usr, uid, 0, missmfc, age, acct, country, continent, cs, cs, cs]
				db_add(db_models, db_wl, uid, u_data) 
				db_sync(db_models, db_wl)
			else:
				if not usr in mem_entry:
					db_append (db_models, db_wl, uid, usr)
					db_sync(db_models, db_wl)
				if cs > 0:
					if mem_entry[9] > cs:
						mem_entry[9]=cs
					elif mem_entry[10] < cs:
						mem_entry[10]=cs
					if mem_entry[8] != cs:
						mem_entry[8]=cs
						db_update(db_models, db_wl, uid, mem_entry)
						db_sync(db_models, db_wl)
		else:
			Name=None
			uid=None
			if msg.find("\"nm\":") != -1:
				Name=(msg[msg.find("\"nm\":")+len("\"nm\":"):].split(",")[0])
				Name=Name.replace('"','')
			else:
				return

			if msg.find("\"sid\":") != -1:
				SID=int(msg[msg.find("\"sid\":")+len("\"sid\":"):].split(",")[0])

			if msg.find("\"lv\":") != -1:
				level=int(msg[msg.find("\"lv\":")+len("\"lv\":"):].split(",")[0])

			account={}
			account[1]="Basic"
			account[2]="Premium"
			account[4]="Model"
			account[5]="Admin"

			rcode={}
			rcode[2]="NOTICE"
			rcode[3]="SUSPEND"
			rcode[4]="SHUT OFF"
			rcode[5]="WARNING"

			print "\nName         : ", Name
			if msg.find("\"age\":") != -1:
				print "Age          : ", int(msg[msg.find("\"age\":")+len("\"age\":"):].split(",")[0])
			if msg.find("\"creation\":") != -1:
				timestamp=int(msg[msg.find("\"creation\":")+len("\"creation\":"):].split(",")[0].replace('}',''))
				acct=time.strftime("%H:%M:%S %b %d,%Y", time.gmtime(timestamp))+" UTC"
				print "Created on   : ", acct
			if msg.find("\"country\":") != -1:
				print "Country      : ", msg[msg.find("\"country\":")+len("\"country\":"):].split(",")[0].replace('"','').lstrip(' ')
			if msg.find("\"uid\":") != -1:
				uid=msg[msg.find("\"uid\":")+len("\"uid\":"):].split(",")[0]

			if SID==0:
				print "Status       :  OFFLINE"
				if level==4:
					self.state="OFFLINE"
					if uid != None:
						mem_entry=db_get(db_models, db_wl, uid)
						if mem_entry==None:
							u_data=[Name, uid, 0, "NA" , "NA", "NA", "NA", "NA", 0,0,0]
							db_add(db_models, db_wl, uid, u_data) 
							db_sync(db_models, db_wl)
						else:
							if not Name in mem_entry:
								db_append (db_models, db_wl, uid, Name)
								db_sync(db_models, db_wl)

			else:
				print "Status       :  ONLINE"
			print "AccountType  : ", account[level] 
			if response_code > 1 and response_code < 6:
				print "Account Status: ", rcode[response_code] 
			if response_code == 0:
				print "Account Status: ", "Active"



	def received_message (self,data):
		self.parse_response(self.ws_main, str(data))

	def parse_response (self, ws, data):
		i=1
		if self.Incomplete_Buf != "":
			data=self.Incomplete_Buf+data
			self.Incomplete_Buf=""
		while i==1:
			hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", data)
			if bool(hdr) == 0:
				self.cli_out ("error: parse_response failed %s" % data)
				break
			msgtype = hdr.group(1)
			try:
				model_id=int(hdr.group(2))
				session_id=hdr.group(3)
				msg_len=int(msgtype[0:4])
				msgtype=int(msgtype[4:])
				response_code=int(hdr.group(5))
			except KeyError:
				print "Key error", data 
				return
			Message=data[4:4+msg_len]
		
			if len(Message) < msg_len:
				self.Incomplete_Buf=''.join(data)
				break

			Message=urllib.unquote(Message)
			if msgtype == 1:
				self.sess_id=int(session_id)
				if self.mchanid==0:
					info=db_getvaluelookup(db_models, db_wl, str(self.model_name));
					if info != None:
						self.modeluid=int(info[1])
						self.mchanid=100000000+int(info[1])
						self.join_room (ws)
						if self.reconnect == 0:
							self.session_IO=1
						client.append(self)
					else:
						ws.send("10 0 0 20 0 %s\n\0" % self.model_name)
			elif msgtype == 50:
				session_id = hdr.group(2)
				chat_opt=hdr.group(5)
				Message=urllib.unquote(Message)
				if int(session_id) == 0:
					self.process_FCServer_msg(Message, int(chat_opt))
				else:
					self.process_chat_message(ws, Message)
			elif msgtype == 10:
				if model_id != 0 and response_code == 0:
					self.modeluid=model_id
					print model_id
					self.process_user_info(Message, response_code)
					if self.mchanid==0:
						self.mchanid=100000000+int(model_id)
						self.join_room (ws)
						if self.reconnect == 0:
							self.session_IO=1
						client.append(self)
				elif response_code == 10 or response_code == 1:
					Message=Message.split(' ')
					cli_out (fg.red + attr.bold + Message[5] + " is not a valid user" + attr.reset)
					if self.mchanid == 0:
						self.session_IO=2
						time.sleep(1)
						self.Name=None
						self.close_session()
						break
				else:
					self.process_user_info(Message, response_code)
			elif msgtype == 20:
				code=int(hdr.group(4))
				mid=int(hdr.group(5))
				if self.modeluid==mid:
					self.process_session_state(Message, 0, mid)
				elif mid==0:
					global guser
					global gpasscode	
					cli_out (fg.red+"Failed to login to chat server - "
						"invalid \""+guser+"\" account"+attr.reset)
					guser="guest"
					gpasscode="guest"
					self.session_IO=2
					time.sleep(1)
					self.Name=None
					self.close_session()
					break
				#else:
				#	self.process_online_model_session_state(Message, 0, mid)
			elif msgtype == 6:
				self.tip_msg (Message)
			elif msgtype == 5:
				self.update_user_info (Message)
			elif msgtype == 51:
				lorj = hdr.group(5)
				lorj=int(lorj)
				if lorj == 1:
					self.join_channel (Message)
				if lorj == 2:
					self.leave_channel (Message)
			elif msgtype == 46:
				self.guests_count=int(hdr.group(4))
			elif msgtype == 44:
				self.process_room_data (Message)
			data=data[4+msg_len:]
			if len(data) == 0:
				break
		
	def guests_remove(self, count):
		i=0
		for guests, [ws, s_sid] in self.GuestsSID.items():
			if ws == self.ws_main:
				continue
			ws.send("98 0 0 0 0 -\n\0")
			ws.close()
			i += 1
			if i == count:
				break
	def show_members(self):
		i=0
		member=sorted(self.members.keys(), key=lambda x: self.members[x], reverse=True)
		for usr in member:
			try:
				lvl=self.members[usr][0]
				userid=self.members[usr][2]
				if userid in self.ignoredusers:
					ignore_user=fg.red+"(Ignored)"
				else:
					ignore_user=""
				if lvl == 4:
					usr=fg.magenta + attr.bold + usr+ ignore_user + attr.reset
				elif lvl == 2:
					usr=fg.cyan + usr + ignore_user + attr.reset
				elif lvl == 1:
					usr=fg.yellow + usr+ ignore_user + attr.reset
				elif lvl == 0:
					usr=fg.red + usr+"("+userid+")" + attr.reset
				cli_out(usr)
				i += 1
			except KeyError:
				pass
		mem_coun=i
		cli_out ("(%d guests)" % self.guests_count)
		cli_out ("(%d prem/basics)" % mem_coun)
		mem_coun += self.guests_count
		cli_out("%d People\n" % mem_coun);

	def join_room(self, ws):
		if self.g_conn_count == 0:
			cli_out("Connecting to \"%s\" room"  % (self.model_name))
			self.g_conn_count += 1
		else:
			self.g_conn_count += 1
			cli_out("Connecting to \"%s\" room - guests added %d" 
				% (self.model_name, self.g_conn_count))
		ws.send("51 0 0 %d 9 -\n\0" % (self.mchanid)); 
		self.is_joined_room=1

	def write_tip_details(self):
		self.token_log.write("**************  %s  ****************\n" %(self.model_name))
		self.token_log.write("Rank            : %-05d\n" % self.rank)
		self.token_log.write("Tokens          : %-05d\n" % self.total_tips)
		people_count=len(self.members.keys())
		self.token_log.write("Premiums/Basics : %-05d\n" % people_count)
		self.token_log.write("Guests          : %-05d\n" % self.guests_count)
		total=people_count+self.guests_count
		self.token_log.write("Total People    : %-05d\n" % total)
		self.token_log.write("Connected on    : %-05s\n" % self.connected_on)
		now = int(time.time())
		self.token_log.write("Active for      : %-05s(hrs:mins:secs)\n" % 
			str(datetime.timedelta(seconds=now-self.start)))
		if self.total_tips == 0:
			self.token_log.flush()
			return
		self.token_log.write("--------------Members Cumulative Tips --------------------\n")
		for mem_key in self.tippers.keys():
			self.token_log.write ("%-24s : %8d\n" % (mem_key, self.tippers[mem_key]))
		self.token_log.write("----------------------------------------------------------\n")
		self.token_log.flush()

	def show_tip_details(self):
		cli_out("Tokens          : %-05d" % self.total_tips)
		if self.total_tips == 0:
			return
		cli_out("--------------Members Cumulative Tips --------------------")
		for mem_key in self.tippers.keys():
			cli_out ("%-24s : %8d" % (mem_key, self.tippers[mem_key]))
		cli_out("----------------------------------------------------------")

	def connect_2_mfc_chat_server_chat(self, host):
		#cli_out("Connecting to Chat Server... %d" % (self.g_conn_count))
            	client = guest_client(host, userdata=[self])
		client.guest_name=None
		client.main_session=self
		try:
			client.connect ()
		except:
			#e, t, tb = sys.exc_info()
			#print("Could not connect guest session to \"%s\"" % (t))
			print("Could not able to connect to chat server")

	def add_guest (self, count):
		global gbot_ka_thr
		if self.gbot_ka_thr == None:
			self.gbot=WebSocketManager()
			self.gbot.start()
			self.gbot_ka=1
			self.gbot_ka_thr=threading.Thread(target=self.run_guest_cli_keep_alive)
			self.gbot_ka_thr.setDaemon(True)
			self.gbot_ka_thr.start()

		i=0
		while True:
			self.connect_2_mfc_chat_server_chat(get_chat_host())
			i += 1
			if i >= count:
				time.sleep(2)
				print "Total Guests count added",  self.g_conn_count
				return
		time.sleep(2)
		print "Total Guests count added", self.g_conn_count
		return

	def display_chat_messages_stored(self):
		q_len=len(self.message_Q)
		if q_len != 0:
			i = 0
			while i < q_len:
				self.cli_out (self.message_Q[i])
				i+=1

	def ignore_user(self, user):
		i=0
		member=sorted(self.members.keys(), key=lambda x: self.members[x], reverse=True)
		for usr in member:
			if usr.lower() == user.lower():
				userid=self.members[usr][2]
				self.ignoredusers.append(userid)
				cli_out(fg.red+"Ignored User \"%s\"%s" % (usr, attr.reset))
				return
		cli_out(fg.red+"Invalid user name \"%s\"" % user)

	def dont_ignore_user(self, user):
		i=0
		member=sorted(self.members.keys(), key=lambda x: self.members[x], reverse=True)
		for usr in member:
			if usr.lower() == user.lower():
				userid=self.members[usr][2]
				self.ignoredusers.remove(userid)
				cli_out(fg.red+"Stopped ignoring User \"%s\"%s" % (usr, attr.reset))
				return
		cli_out(fg.red+"Invalid user name \"%s\"" % user)

	def session_handle_command(self, line, websk, sid):
		help_string="Help : \n/g <count> - Add guest(s)\n" \
			     "/r <count> - Remove guest(s)\n/s <account_name> - online status of a member/model\n"\
			     "/m - Members in the room \n" \
			    "/i - To ignore a user\n/u - To stop ignoring user\n/t - tokens info\n"\
				 "/S - Regular Spam\n/c - Counting Spam\n/e - Change the Size of bEmotes\nTo send bEmotes.. Type :b(name of emote) and that will send resized bEmotes.\nTo send regular Emotes just type the name normally.\n/d - Leo Loves Dongs Multi Line Spam"
		if line[0] == '/':
			if len(line) >= 2:
				if line[1] == 't':
					self.show_tip_details ()
					print "Total Guests count ", self.g_conn_count, self.gcount
				elif line[1] == 'g':
					line=line.split()
					try:
						count=line[1]
						count=s2i(count)
						self.add_guest (count)
					except IndexError:
						self.add_guest (1)
				elif line[1] == 'r':
					line=line.split()
					try:
						count=line[1]
						count=s2i(count)
						self.guests_remove (count)
					except IndexError:
						self.guests_remove (1)
				elif line[1] == 'i':
					user=raw_input("Enter Username to ignore > ")
					if len(user) == 0:
						cli_out(fg.red+ "Not a valid username"+attr.reset)
						return
					user=user.strip()
					self.ignore_user(user)
				elif line[1] == 'u':
					user=raw_input("Enter Username to stop ignoring > ")
					if len(user) == 0:
						cli_out(fg.red+ "Not a valid username"+attr.reset)
						return
					user=user.strip()
					self.dont_ignore_user(user)
				elif line[1] == 'm':
					self.show_members()
				elif line[1] == 'h':
					cli_out(help_string)
				elif line[1]=='s':
					Name=line[3:]
					if len(Name) == 0:
						cli_out(fg.red+ "Not a valid username"+attr.reset)
						return
					self.ws_main.send("10 0 0 20 0 %s\n\0" % Name)
					time.sleep(2)
				elif line[1] == 'S':
					n = int(input('Number of lines to spam: '))
					interval = int(input('Interval line is to be posted in seconds: '))
					spam = raw_input('Type your spam: ')
					for i in range(n):
						spam=update_emote_2_code(spam)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid,spam))
						time.sleep(interval)		
				elif line[1] == 'c':
					n = int(input('Number of lines to spam: '))
					interval = int(input('Interval line is to be posted in seconds: '))
					spam = raw_input('Type your spam: ')
					for i in range(1, n, 1):
						spam=update_emote_2_code(spam)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid,'{0} '.format(i)+spam))
						time.sleep(interval)
				elif line[1] == 'e':
					emote_init()
				elif line[1] == 'd':
					n = int(input('Number of lines to spam: '))
					interval = int(input('Interval line is to be posted in seconds: '))
					for i in range(n):
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid, emote[":bdance"]))
						time.sleep(interval)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid,'LEO'))
						time.sleep(interval)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid,'LOVES'))
						time.sleep(interval)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid,'DONGS'))
						time.sleep(interval)
						websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid, emote[":bdance"]))
						time.sleep(interval)
				elif line[1]=='q':
					self.session_IO=0
					return
				else:
					cli_out(help_string)
		else:
			line=update_emote_2_code(line)
			websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid, line))
			time.sleep(.01)

	def session_input(self):
		retry=0
		while self.mchanid == 0:
			if self.session_IO == 2:
				self.ws_main.close()
				del self
				return
			elif self.session_IO == 1:
				break
			retry += 1
			time.sleep(.01)
			if retry == 60:
				self.ws_main.close()
				self.session_IO=2
				del self
				return
		while self.session_IO:
			try:
				rand=random.randint(1, self.g_conn_count)
			except ValueError:
				if self.g_conn_count == 0:
					return
			sid=self.sess_id
			guest=self.Name
			websk=self.ws_main
			for guests, [websock, s_sid] in self.GuestsSID.items():
				rand -= 1
				if rand==0:
					sid=s_sid
					guest=guests
					websk=websock
					break
			line = raw_input(fg.green + str(guest).strip('"')+">"+attr.reset)
			if len(line) > 1:
				self.session_handle_command(line, websk, sid)

def update_emote_2_code(msg):
	#msg=re.sub('#[^#]+#', '', msg)
	for i in sorted(emote.iterkeys(), key=len, reverse=True):
		msg = msg.replace(i, emote[i])
	return msg

"""def update_code_2_emote(msg):
	for i in sorted(emote.iterkeys(), key=len, reverse=True):
		msg = msg.replace(emote[i], i)
	return msg.replace('#~e,1000,too_many_images_posted_in_a_short_period_of_time~#', '')"""

	
def session_info_header():
	cli_out(fg.red+"** Active Session(s) **"+attr.reset)
	cli_out("%-05s     %-10s" % ("Id", "Name"))
	cli_out(fg.red+"***********************"+attr.reset)

def probe_models_room ():
	keys = online_models.keys()
	for key in keys:
		try:
			print "Connecting to model ", online_models[key][0]
			client = connect_xchat_server(online_models[key][0])
			if client != None:
				time.sleep(10)
				client.close_session()
		except KeyError:
			pass

def get_chat_host():
	global xchat_index
	host = "ws://xchat"+str(xchat[xchat_index])+".myfreecams.com:8080/fcsl"
	xchat_index += 1
	if xchat_index >= len(xchat):
		xchat_index=0
	return host

def connect_xchat_server (model_name):
	cli_out("Connecting to Chat Server...")
	host = get_chat_host()
       	client = mfcsession(host, userdata=[model_name])
	client.model_name=model_name
	client.Name=None
	try:
		client.connect ()
	except:
		e, t, tb = sys.exc_info()
		cli_out(fg.red+"Could not able connect to chat server : \"%s\"%s\n" % (t, attr.reset))
		client=None
	return client

def send_user_login_form(username, password):
	url = 'http://www.myfreecams.com/mfc2/php/login.php'
	UID=int(random.random() * 99999999999999)
	screen_size=ss[random.randint(0, len(ss)-1)]
	tz=utc_offset[random.randint(0, len(utc_offset)-1)]

	print ("Logging in with username %s and password %s timezone UTC offset %s screen size %s" 
		%(username, password, tz, screen_size))

	values = {'submit_login' : '67',
        	  'uid': UID,
	          'tz' : tz,
        	  'ss' : screen_size,
		  'username' : username,
        	  'password' : password }

	data = urllib.urlencode(values)
	cookies = cookielib.CookieJar()
	opener = urllib2.build_opener(  urllib2.HTTPRedirectHandler(),
					urllib2.HTTPHandler(debuglevel=0),
					urllib2.HTTPSHandler(debuglevel=0),
					urllib2.HTTPCookieProcessor(cookies))
	response = opener.open(url, data)
	http_headers = response.info()
	cookie = Cookie.SimpleCookie()
	try:
		cookie.load(http_headers['set-cookie'])
		Passcode = cookie['passcode'].value
	except KeyError:
		return None
	return Passcode

def login():
	global gpasscode
	global guser
	username=raw_input("Enter your username > ")
	if len(username) == 0:
		cli_out(fg.red+ "Not a valid username"+attr.reset)
		return
	username=username.strip()
	password=raw_input("Enter your password > ")
	if len(password) == 0:
		cli_out(fg.red+ "Not a valid password"+attr.reset)
		return
	password=password.strip()
	passcode=send_user_login_form (username, password)
	if passcode==None:
		cli_out(fg.red+ "Faild to get user passcode"+attr.reset)
	else:
		gpasscode=passcode
		guser=username
		cli_out(fg.red+ "Received user passcode for user \"%s\" - Now you can connect to model's chat room%s" 
			% (guser, attr.reset))

def create_account():
	username=raw_input("Enter username > ")
	username=username.strip()
	if len(username) < 5:
		cli_out(fg.red+"Your username is too short"+attr.reset)
		return
	if len(username) > 14:
		cli_out(fg.red+"Your username is too long"+attr.reset)
		return
	if username[0].isdigit():
		cli_out(fg.red+"Your username cannot begin with a number"+attr.reset)
		return

	password=raw_input("Enter password > ")
	password=password.strip()
	if len(password) < 7:
		cli_out(fg.red+"Your password is too short"+attr.reset)
		return
	if len(password) > 32:
		cli_out(fg.red+"Your password is too long"+attr.reset)
		return

	email=raw_input("Enter email > ")
	if len(email) == 0:
		cli_out(fg.red+"Not a valid email"+attr.reset)
		return
	email=email.strip()
	url = 'http://www.myfreecams.com/php/signup.php'

	UID=int(random.random() * 99999999999999)

	screen_size=ss[random.randint(0, len(ss)-1)]
	tz=utc_offset[random.randint(0, len(utc_offset)-1)]
	gnum="%05d" % random.randint(10,90000)
	Guest="Guest"+str(gnum)

	print ("Creating an account with username %s and password %s\n" %(username, password))

	values = {'submit_login' : '3',
		  'submit_signup' : '1',
		  'terms' : '1',
		  'request' : 'register',
		  'USERNAME' : Guest,
		  'models_per_page' : '200',
        	  'uid': UID,
	          'tz' : tz,
        	  'ss' : screen_size,
		  'email' : email,
		  'user_invoked' : '1',
		  'model_id' : '',
		  'mode' : '',
		  'username' : username,
        	  'password' : password,
		  'confirm_password': password}

	data = urllib.urlencode(values)
	cookies = cookielib.CookieJar()
	opener = urllib2.build_opener(  urllib2.HTTPRedirectHandler(),
					urllib2.HTTPHandler(debuglevel=0),
					urllib2.HTTPSHandler(debuglevel=0),
					urllib2.HTTPCookieProcessor(cookies))
	response = opener.open(url, data)
	content = response.read()
	soup = BeautifulSoup(content)
	for script in soup(["script", "style"]):
	    script.extract()
	text = soup.getText()
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	text = '\n'.join(chunk for chunk in chunks if chunk)
	for i in re1:
		text=re.sub('<[^<]+?>', '', text).replace(i,' ')
	cli_out(fg.red+text.encode('utf-8')+attr.reset)

def Verify_Account (url2):
        global gpasscode
        global guser
        #url = raw_input('Enter MFC Verification URL: ')
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(  urllib2.HTTPRedirectHandler(),
                                        urllib2.HTTPHandler(debuglevel=0),
                                        urllib2.HTTPSHandler(debuglevel=0),
                                        urllib2.HTTPCookieProcessor(cookies))
        response = opener.open(url2)
        http_headers = response.info()
        cookie = Cookie.SimpleCookie()
        try:
                cookie.load(http_headers['set-cookie'])
                User=cookie['username'].value
                Passcode = cookie['passcode'].value
                UID=cookie['user_id'].value
        except KeyError:
                return
        print ("Account Verified for user %s and received passcode %s user id %s\n"
                % ( User, Passcode, UID))
        guser=User
        gpasscode=Passcode
        print ("You can connect to the room ..")

def process_global_commands(line):
	global client
	help_string="Help : \n/c - Connect to Model's Room (new session)\n/j - Join Model's active session \n" \
                     "/l - List active sessions\n/t - Close an active session\n/s - Active sesssions info\n"\
		     "/L - Sign in to your member account\n"\
		     "/N - Create FREE Account\n"\
		     "/V - Veriify New Account\n"\
			 "/R - Reset User login to GUEST\n"\
		     "/m <model_name> - Model Look up in local database\n" \
		     "/u <memebr_name> - Member Look up in local database\n" \
		     "/q - Quit the program \n"
	if line[0] == '?':
		cli_out(help_string)
	elif line[0] == '/':
		if len(line) >= 2:
			if line[1] == 'h':
				cli_out(help_string)
			elif line[1]=='s':
				i = 0
				now = int(time.time())
				for session in client:
					i += 1
					people_count=len(session.members.keys())
					cli_out(fg.green+"%-05d%-10s (%s)%s" %
						(i, session.model_name, session.Name, attr.reset))
					cli_out("     Cam State       : %-05s" % session.state)
					cli_out("     Rank            : %-05d" % session.rank)
					cli_out("     Tokens          : %-05d" % session.total_tips)
					cli_out("     Premiums/Basics : %-05d" % people_count)
					cli_out("     Guests          : %-05d" % session.guests_count)
					total=people_count+session.guests_count
					cli_out("     Total People    : %-05d" % total)
					cli_out("     Connected on    : %-05s" % session.connected_on)
					cli_out("     Active for      : %-05s(hrs:mins:secs)" % 
						str(datetime.timedelta(seconds=now-session.start)))
					cli_out("     Guests added    : %-05d" % (session.g_conn_count))
				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
				cli_out("\nProgram running for  : %-05s(hrs:mins:secs)" % 
					str(datetime.timedelta(seconds=now-startup_time)))
			elif line[1]=='l':
				i = 0
				now = int(time.time())
				for session in client:
					if i == 0:
						session_info_header()
					i += 1
					cli_out(fg.green+"%-05d     %-10s %s(%s)%s" %(i, 
							session.model_name, fg.red, session.state, attr.reset))
				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
				cli_out("\nProgram running for  : %-05s(hrs:mins:secs)" % 
					str(datetime.timedelta(seconds=now-startup_time)))
			elif line[1]=='j' or line[1]=='t':
				i=0
				for session in client:
					if i == 0:
						session_info_header()
					i += 1
					cli_out(fg.green+"%-05d     %-10s%s" %(i, session.model_name, attr.reset))
				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
					return
				model=raw_input("Model Id (1 - "+str(i)+") (0/Enter to quit)> ")
				if model.isdigit() == False:
					return
				if int(model) == 0:
					return
				model=int(model)
				if model < 1 or model > i:
					cli_out ("Invalid Model Id \""+str(model)+"\".... :( ")
				else:
					j=1
					for session in client:
						if j==model:
							if line[1]=='j':
								session.session_IO=1
								cli_out("Joined %s's room" % session.model_name)
								session.display_chat_messages_stored()
								session.session_input()
							elif line[1]=='t':
								session.close_session()
								client.remove(session)
							return
						j += 1
			elif line[1]=='r':
				global main_ka_thr
				file_1 = open('models.txt', 'r')
				for model in file_1:
					model=model.strip('\n')
					model=model.strip()
					for session in client:
						if session.model_name.lower() == model.lower():
							continue
					session=connect_xchat_server(model)
					if session==None:
						return
					if main_ka_thr == None:
						main_session.start()
						main_ka_thr=threading.Thread(target=main_keep_alive)
						main_ka_thr.setDaemon(True)
						main_ka_thr.start()
					time.sleep(5)
					session.session_IO=0
			elif line[1] == 'c':
				j=1
				model=raw_input("Enter Model's Name > ")
				if len(model) == 0:
					cli_out(fg.red+ "Not a valid username"+attr.reset)
					return
				model=model.strip()
				#for session in client:
				#	if session.model_name.lower() == model.lower():
				#		cli_out(fg.red+"Active session for model '%s' is running (%d)" %(model, j))
				#		return
				#	j += 1
				session=connect_xchat_server(model)
				if session==None:
					return
				if main_ka_thr == None:
					main_session.start()
					main_ka_thr=threading.Thread(target=main_keep_alive)
					main_ka_thr.setDaemon(True)
					main_ka_thr.start()
				session.session_input()
			elif line[1]=='u':
				Name=line[3:]
				if len(Name)!=0:
					db_valuelookup(db_members, db_ml, Name, print_user_info)
				else:
					cli_out(fg.red+ "Not a valid username"+attr.reset)
			elif line[1]=='L':
				cli_out (fg.green+"Sign in to your account"+attr.reset)
				login()
			elif line[1]=='N':
				cli_out (fg.green+"Create New account"+attr.reset)
				create_account()
			elif line[1]=='V':
				url2 = raw_input('Enter MFC Verification URL: ')
				Verify_Account(url2)
			elif line[1]=='R':
				global gpasscode
				global guser
				cli_out (fg.green+"Resetting user login to guest"+attr.reset)
				guser="guest"
				gpasscode="guest"
			elif line[1]=='m':
				Name=line[3:]
				if len(Name)!=0:
					db_valuelookup(db_models, db_wl, Name, print_model_info)
				else:
					cli_out(fg.red+ "Not a valid username"+attr.reset)
			elif line[1]=='d':
				if line[2] == 'm':
					db_dumpall(db_models, db_wl, show_model_info)
				elif line[2] == 'u':
					db_dumpall(db_members, db_ml, show_member_info)
			elif line[1]=='q':
				key=raw_input(fg.red+"Do you really want to exit program ? <y/n> : "+attr.reset)
				if len(key) > 0:
					if key[0] == 'y':
						for session in client:
							session.close_session()
						cli_out("Exiting in 60 seconds ...")
						time.sleep(60)
						main_session.close_all()
						main_session.stop()
						time.sleep(2)
						sys.exit()
			else:
				cli_out(help_string)

def show_model_info(value, key):
	print "Name         : ", value[0]
	print "Age          : ", value[4]
	print "Country      : ", value[6]
	print "Continent    : ", value[7]
	print "Created On   : ", value[5]
	print "Camscore     : "
	print "    Current  : ", value[8]
	print "    Lowest   : ", value[9]
	print "    Highest  : ", value[10]
	elem=len(value)
	if elem >= 11:
		sys.stdout.write("Name changes :  ")
		for i in range(11, elem):
			sys.stdout.write(value[i]+", ")
		print ""
	print ""

def show_member_info(value, key):
	if len(value) < 6:
		return
	print value


def print_model_info(key, value):
	print "Name         : ", value[0]
	print "Age          : ", value[4]
	print "Country      : ", value[6]
	print "Continent    : ", value[7]
	print "Created On   : ", value[5]
	print "Camscore     : "
	print "    Current  : ", value[8]
	print "    Lowest   : ", value[9]
	print "    Highest  : ", value[10]
	elem=len(value)
	if elem > 11:
		sys.stdout.write("Name changes :  ")
		for i in range(11, elem):
			sys.stdout.write(value[i]+", ")
		print ""
	tokens=value[2]
	if tokens != 0:
		print "Tokens Made: ", tokens
	print ""

def print_user_info(key, value):
	tokens=None
	print "Name         : ", value[0]
	print "Age          : ", value[3]
	print "Country      : ", value[4]
	print "Created On   : ", value[5]
	tokens=value[2]
	if tokens != 0:
		print "Tokens Tipped: ", tokens
	elem=len(value)
	if elem > 6:
		sys.stdout.write("Name changes :  ")
		for i in range(6, elem):
			sys.stdout.write(value[i]+", ")
		print ""
	print ""

def runforever():
	while True:
		line = raw_input(fg.green + ""+" #> "+attr.reset)
		if len(line) > 0:
			process_global_commands(line)
def init_default():
	global db_members
	global db_models
	global db_ml
	global db_wl
	global main_ka_thr
	logging.basicConfig()
	init(autoreset=False)
	main_ka_thr=None
	db_members=db_open("db/"+"mfcmembers")
	db_models=db_open("db/"+"mfcmodels")
	db_wl = threading.Semaphore()
	db_ml = threading.Semaphore()

def stack_trace_dump():
	print >> sys.stderr, "\n*** STACKTRACE - START ***\n"
	code = []
	for threadId, stack in sys._current_frames().items():
	    code.append("\n# ThreadID: %s" % threadId)
	    for filename, lineno, name, line in traceback.extract_stack(stack):
		code.append('File: "%s", line %d, in %s' % (filename,
							    lineno, name))
		if line:
		    code.append("  %s" % (line.strip()))

	for line in code:
	    print >> sys.stderr, line
	print >> sys.stderr, "\n*** STACKTRACE - END ***\n"

def handle_signal(signum, frame):
	cli_out("Session Interrupted %d" % signum)
	db_sync(db_members, db_ml)
	db_members.close()
	db_sync(db_models, db_wl)
	db_models.close()
	stack_trace_dump()
	time.sleep(2)
	main_session.close_all()
	main_session.stop()
	sys.exit()

def echo_test():
	cli_out (fg.green+"**************************************************************")
	#cli_out (fg.green+"❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤")
	cli_out (fg.green+"*           MFC GUEST CHAT-CLIENT/BOT/TOKEN-TRACKER          *")
	cli_out (fg.green+"*                       CREATED BY                           *")
	cli_out (fg.green+"*               INTERNET SENSATION & HACKER                  *")
	cli_out (fg.green+"*"+fg.red+"                       EGYPTBEAUTY                          "+fg.green+"*")
	cli_out ("*                                                            *")
        cli_out ("*                      ,:',:`,:'                             *")
        cli_out ("*                    __||_||_||_||___                        *")
        cli_out ("*              ____[\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"]___                     *")
        cli_out ("*             \ \" ''L'''''E'''''O''''' \                     *")
        cli_out ("*       ~^~^~^~^~ ~^~^~~^~^~^^~^~^~^~^~^~^~^~~^~^~^~         *")
	cli_out ("*                                                            *")
	cli_out (fg.green+"*                                                            *")
	#cli_out (fg.green+"*       ❤     凸( •̀_•́ )凸 LEO  凸( •̀_•́ )凸      ❤            *")
	#cli_out (fg.green+"❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤")
	cli_out (fg.green+"**************************************************************")
	cli_out ("Type /h for Help")

def s2i(buf):
	try:
		ivalue=int(buf)
	except ValueError:
		ivalue=1
	return ivalue

if __name__ == "__main__":
	path="token_logs"
	if not os.path.exists(path):
		os.makedirs(path)
	path="db"
	if not os.path.exists(path):
		os.makedirs(path)
	print len(xchat)
	init_default()
	echo_test()
	emote_init()
	try:
		runforever()
	except KeyboardInterrupt:
		handle_signal(0,0)
