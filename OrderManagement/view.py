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
import datetime

def getItemPrice(item):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"price.txt","r")
	for line in f:
		i,p=line.split(',')
		if item.lower()==i.lower():
			return float(p)
	return 0

def getOptionPrice(option):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"option.txt","r")
	for line in f:
		o,p=line.split(',')
		if option.lower()==o.lower():
			return float(p)
	return 0

def getPrice(item,options):
	p=getItemPrice(item)
	for o in options.split(','):
		p+=getOptionPrice(o)
	return p

def nextNumber():
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"orders.txt",'r')
	return len(f.readlines())

def receive(buf):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"orders.txt",'a')
	try:
		js=json.loads(buf)
		if "intent" not in js or "delivery method" not in js or "items" not in js:
			return
		for item in js["items"]:
		 	if "name" not in item or "options" not in item or "amount" not in item:
		 		return
	except:
		return
	f.write('#'.join([buf,"not paid",((datetime.datetime.now()-datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H:%M:%S'),str(nextNumber())])+"\n")

def decodeJSON(record):
	try:
		buf,orderStatus,orderTime,orderNumber=record.split('#')
		js=json.loads(buf)
		if "intent" not in js:
			return ""
		if js["intent"]=="OrderFood":
			order={}
			order["idx"]=orderNumber
			order["status"]=orderStatus
			order["deliveryMethod"]=js["delivery method"]
			order["time"]=orderTime
			order["totalPrice"]=0
			parts=[]
			for item in js["items"]:
				part={}
				part["item"]=item["name"]
				part["option"]=", ".join(item["options"])
				part["count"]=item["amount"]
				part["price"]=getPrice(part["item"],part["option"])
				parts.append(part)
				order["totalPrice"]+=part["count"]*part["price"]
			order["parts"]=parts
			order["tax"]=round(order["totalPrice"]*0.0775,2)
			order["total"]=order["totalPrice"]+order["tax"]
			return order
		else:
			return ""
	except:
		return ""

def getOrders(status):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"orders.txt","r")
	orders=[]
	for line in f:
		o=decodeJSON(line)
		if o and o["status"]==status:
			orders.append(o)
	return orders

def changeStatus(number,status):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"orders.txt",'r')
	lines=f.readlines()
	f=open(db+"orders.txt",'w')
	for line in lines:
		buf,orderStatus,orderTime,orderNumber=line.strip('\n').split('#')
		print orderNumber,number
		if orderNumber!=number:	
			f.write(line)
	f.write('#'.join([buf,status,orderTime,number])+"\n")

def getDetailIp(ipp):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"ip.txt","r")
	for line in f:
		ip,username,position=line.split()
		if ip==ipp:
			return (username,position)
	return ("","")

def getOrder(request,orderdetail):
	try:
		json.loads(orderdetail)
	except:
		return HttpResponse("Not JSON format!")
	receive(orderdetail)
	return HttpResponse(orderdetail)

def index(request):
	return render(request,'logIn.html')

def verifyAccount(username,password):
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"user.txt",'r')
	for line in f:
		u,p,j=line.split()
		if u==username and p==password:
			return j
	return ""

def getIP(request):
	x_forwarded_for=request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		return x_forwarded_for.split(',')[0]
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
		db=os.path.dirname(os.path.abspath(__file__))+"/database/"
		f=open(db+"ip.txt",'r')
		lines=f.readlines()
		f=open(db+"ip.txt",'w')
		for line in lines:
			if ip in line:
				continue
			f.write(line)
		f.write(" ".join([ip,username,va])+"\n")
		return redirect("/"+va+"/")

def goRegister(request):
	return render(request,'register.html')

def register(request):
	username=request.GET['username']
	password=request.GET['password']
	confirm_password=request.GET['confirm_password']
	position=request.GET['position']
	db=os.path.dirname(os.path.abspath(__file__))+"/database/"
	f=open(db+"user.txt",'r')
	for line in f:
		u,p,j=line.split()
		if username==u:
			return HttpResponse("Existing user name!")
	if password!=confirm_password:
	 	return HttpResponse("Different password!")
	f=open(db+"user.txt",'a')
	f.write(" ".join([username,password,position])+"\n")
	return redirect("/")

def cashier(request):
	ip=getIP(request)
	username,position=getDetailIp(ip)
	if position!="cashier":
                return HttpResponse("Please log in!")
	para={'username':username,'orders':getOrders("not paid")}
	return render(request,'cashier.html',para)

def check(request,idx):
	changeStatus(idx,"not cooked")
	return redirect("/cashier/")

def chef(request):
	ip=getIP(request)
	username,position=getDetailIp(ip)
	if position!="chef":
                 return HttpResponse("Please log in!")
	para={'username':username,'orders':getOrders("not cooked")}
	return render(request,'chef.html',para)

def cook(request,idx):
	changeStatus(idx,"not delivered")
	return redirect("/chef/")

def deliverer(request):
	ip=getIP(request)
	username,position=getDetailIp(ip)
	if position!="deliverer":
		return HttpResponse("Please log in!")
	para={'username':username,'orders':getOrders("not delivered")}
	return render(request,'deliverer.html',para)

def deliver(request,idx):
	changeStatus(idx,"finish")
	return redirect("/deliverer/")
