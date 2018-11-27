from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
import random
import socket
import threading
import time
import os
import sys
import collections
import json
import pymysql

orders=[]
ipToUserName=collections.defaultdict(str)
ipToPosition=collections.defaultdict(str)
path=sys.path[0]+"/OrderManagement/"
prices=collections.defaultdict(float)
optionPrices=collections.defaultdict(float)

def getPrice(item,options):
	p=prices[item.lower()]
	for o in options.split(','):
		p+=optionPrices[o.lower()]
	return p

def receive(buf):
	js=json.loads(buf)
	if js['intent']=="OrderFood":
		order={}
		order["idx"]=len(orders)
		order["status"]="not paid"
		order["deliveryMethod"]="For here"
		order["time"]=time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
		parts=[]
		for item in js["items"]:
			part={}
			part["item"]=item["name"]
			part["option"]=",".join(item["options"])
			part["count"]=item["amount"]
			part["price"]=getPrice(part["item"],part["option"])
			for _ in range(item["amount"]):
				parts.append(part)
		order["parts"]=parts
		orders.append(order)
	elif js['intent']=="QueryOptions":
		pass
	else:
		pass

class server(threading.Thread):
	def run(self):
		sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.bind((socket.gethostbyname(socket.gethostname()),2900))
		sock.listen(100)
		while True:
			connection,address=sock.accept()
			try:
				while True:
					buf=connection.recv(1024)
					receive(buf)
			except socket.timeout:
			  	print 'time out'
			connection.close()
s=server()
s.start()

def index(request):
	return render(request,'logIn.html')

def verifyAccount(username,password):
	f=open(os.path.dirname(__file__)+"/database/user.txt","r")
	for line in f:
		u,p,j=line.split()
		if username==u and password==p:
			return j
	return ""

def getIP(request):
	x_forwarded_for=request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		return x_forward_for.split(',')[0]
	else:
		return request.META.get('REMOTE_ADDR')

def logIn(request):
	username=request.GET['username']
	password=request.GET['password']
	va=verifyAccount(username,password)
	if not va:
		return render(request,'logIn.html')
	else:
		ip=getIP(request)
		ipToUserName[ip]=username
		ipToPosition[ip]=va
		return redirect("/"+va+"/")

def goRegister(request):
	para={"positions":["chef","cashier","deliverer"]}
	return render(request,'register.html',para)

def register(request):
	username=request.GET['username']
	password=request.GET['password']
	confirm_password=request.GET['confirm_password']
	position=request.GET['position']
	f=open(path+"user/user.txt",'r')
	for line in f:
		u,p,j=line.split()
		if username==u:
			return HttpResponse("Existing user name!")
	if password!=confirm_password:
	 	return HttpResponse("Different password!")
	f=open(path+"user/user.txt",'a')
	f.write(" ".join([username,password,position])+"\n")
	return redirect("/")

def cashier(request):
	ip=getIP(request)
	if ipToPosition[ip]!="cashier":
		return HttpResponse("Please log in!")
	tmp=[]
	for i,o in enumerate(orders):
		if o["status"]!="not paid":
			pass
		else:
			tmp.append(o)
	para={'username':ipToUserName[ip],'orders':tmp}
	return render(request,'cashier.html',para)

def check(request,idx):
	idx=int(idx)
	orders[idx]["status"]="not cooked"
	return redirect("/cashier/")

def chef(request):
	ip=getIP(request)
	if ipToPosition[ip]!="chef":
		return HttpResponse("Please log in!")
	tmp=[]
	for i,o in enumerate(orders):
		if o["status"]!="not cooked":
			pass
		else:
			tmp.append(o)
	para={'username':ipToUserName[ip],'orders':tmp}
	return render(request,'chef.html',para)

def cook(request,idx):
	idx=int(idx)
	orders[idx]["status"]="not delivered"
	return redirect("/chef/")

def deliverer(request):
	ip=getIP(request)
	if ipToPosition[ip]!="deliverer":
		return HttpResponse("Please log in!")
	tmp=[]
	for i,o in enumerate(orders):
		if o["status"]!="not delivered":
			pass
		else:
			tmp.append(o)
	para={'username':ipToUserName[ip],'orders':tmp}
	return render(request,'deliverer.html',para)

def deliver(request,idx):
	idx=int(idx)
	orders[idx]["status"]="finish"
	return redirect("/deliverer/")
