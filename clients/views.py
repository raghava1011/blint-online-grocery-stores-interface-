from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Outlets,Products,Orders
from django.contrib.auth import authenticate,logout as user_logout,login as user_login
import json
from django.core import serializers
from django.db import DatabaseError, transaction
# Create your views here.


def login(req):
    if(req.user.is_authenticated):
        return redirect('homepage')
    
    if(req.method=='POST'):
        print(req.POST.get('email'))
        print(req.POST.get('pass'))
        user_auth=authenticate(password=req.POST.get('pass'),username=req.POST.get('username'))
        user_login(req,user_auth)
        return redirect('homepage')
    else:
        return render(req,'login.html')
def logout(req):
    user_logout(req)
    return redirect('homepage')

def register(req):

    if(req.user.is_authenticated):
        return redirect('homepage')
    print("---------------------------------------------------------")
    if(req.method=='POST'):
        fname=req.POST.get('fname')
        lname=req.POST.get('lname')
        email=req.POST.get('email')
        username=req.POST.get('username')
        pswd=req.POST.get('pswd')
        try:
            user = User.objects.create_user(username=username,email=email,password=pswd,first_name=fname,last_name=lname)
            user.save()
            user_auth=authenticate(password=req.POST.get('pswd'),username=req.POST.get('username'))
            user_login(req,user_auth)
        except:
            print('An exception occured')
            return render(req,'register.html')
        print('---------------------------------------------------------------')
        return redirect('homepage')
    else:
        return render(req,'register.html')

def homepage(req):
    print("hjhjhjhjhhjhjhjh")
    if(req.user.is_authenticated):
        print("fALSEEEEEE")
        if(req.user.is_staff):
            return redirect('vhome')
        
        
        return render(req,'home.html')
    else:
        return redirect('login')
'''def home(req):
    if(req.user.is_staff):
        print("true------------------------")
    else:
        print("falseeeeeeeeeeeeeeee-----------------")
    return render(req,'home.html')'''

def shop(req):
    if(req.user.is_authenticated):
        oulet_id=req.GET.get('id')
        products=Products.objects.filter(outlet_id=oulet_id)
        print("----------------------------------------------------------------")
        print(products)
        temp_json = serializers.serialize('json', products)
        products = json.dumps({"name":"dummy"})

        return render(req,'product_view.html',{'products':temp_json})
    return redirect('homepage')


def cart(req):
    if(req.user.is_authenticated):
        if(req.method=='POST'):
            print("************")
            body_unicode = req.body.decode('utf-8')
            body = json.loads(body_unicode)
            print(body)
            prod_id=[]
            quant=[]
            prods=[]
            for i in body:
                if('qty' in i.keys()):
                    i=dict(i)
                    print(i['id'])
                    print("************")
                    prod_id.append(i['id'])
                    quant.append(i['qty'])
            outletid=body[0]['outlet_id']
            print(prod_id,outletid,quant)
            print("~~~~~~~~~~~~~~~~~~~~~~")
            # print(body['content'])
            try:
                with transaction.atomic():
                    res=Products.objects.filter(product_id__in=prod_id)
                    for p in prod_id:
                        for temp in res:
                            if(str(temp.product_id)==p):
                                prods.append(temp)
                                break
                    print(prods)
                    amount=0
                    for q,pr in zip(quant,prods):
                            amount=amount+(float(q)*float(pr.price))
                            pr.stock_quatity=pr.stock_quatity-q
                            pr.save()
                    ord=Orders()
                    ord.amount=amount
                    ord.product_quantity=quant
                    ord.product_list=prod_id
                    ord.outlet_id=Outlets.objects.get(outlet_id=outletid)
                    ord.user_id=User.objects.get(id=req.user.id)
                    ord.status='P'
                    ord.address="random address"
                    ord.payment_type='O'
                    ord.save()
                    print(amount)
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            except DatabaseError as e:
                #return  redirect('notfound')            
                print("********************************")
                print(e)
            return redirect('myorders')
        if(req.method=='GET'):
            return render(req,'cart.html')
    return redirect('homepage')



def vhome(req):
    if(req.user.is_authenticated):
        if(req.user.is_staff):
            user_id=req.user.id
            outid=Outlets.objects.get(owner_id=user_id)
            print(outid)
            products=Products.objects.filter(outlet_id=outid)
            print(products)
            return render(req,'vhome.html',{"products":products})

    return redirect('homepage')


    #return render(req,'vhome.html')
def accept_order(req):
    if(req.user.is_authenticated and req.user.is_staff):
        orderid=req.GET.get('order_id')
        print("&&&&&&&&&&&&&&&&&&&&&&&&"+orderid)
        if(orderid):
            print("entered")
            outlet=Outlets.objects.get(owner_id=req.user.id)
            Orders.objects.filter(outlet_id=outlet.outlet_id,order_id=orderid).update(status='A')
        else:
            print("not entered")
        return render(req,'pending.html')
    else:
        redirect('homepage')

def pending(req):
    if(req.user.is_authenticated and req.user.is_staff):
        outlet=Outlets.objects.get(owner_id=req.user.id)
        pending_orders=Orders.objects.filter(outlet_id=outlet.outlet_id,status='P')
        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        print(pending_orders)


        products_list=[]
        for i in pending_orders:
            print("-------------------------")
            print(i.product_list)
            print("+++++++++++++++++++++++++++")
            productlist=list(i.product_list)
            p=Products.objects.filter(product_id__in=productlist)
            pds=[]
            for pids in i.product_list:
                
                for temps in p:

                    if(str(temps.product_id)==str(pids)):
                        pds.append(temps)
                        break
            products_list.append(pds)

        print("==================")
        print(products_list)
        print("----------------")
        dictlist=[]
        for order,prod in zip(pending_orders,products_list):
            d=dict()
            d['order_id']=order.order_id
            d['status']=order.status
            array=[]
            for j,k in zip(prod,order.product_quantity):
                pdic=dict()
                pdic['product_name']=j.product_name
                pdic['product_id']=j.product_id
                pdic['product_quantity']=k
                array.append(pdic)
            d['products']=array
            dictlist.append(d)
        print(products_list)
        return render(req,'pending.html',{'orders':dictlist})
    return redirect('homepage')


def pastorders(req):
    if(req.user.is_authenticated and req.user.is_staff):
        outlet=Outlets.objects.get(owner_id=req.user.id)
        past_orders=Orders.objects.filter(outlet_id=outlet.outlet_id,status='A')
        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        print(past_orders)


        products_list=[]
        for i in past_orders:
            print("-------------------------")
            print(i.product_list)
            print("+++++++++++++++++++++++++++")
            productlist=list(i.product_list)
            p=Products.objects.filter(product_id__in=productlist)
            pds=[]
            for pids in i.product_list:
                
                for temps in p:

                    if(str(temps.product_id)==str(pids)):
                        pds.append(temps)
                        break
            products_list.append(pds)

        print("==================")
        print(products_list)
        print("----------------")
        dictlist=[]
        for order,prod in zip(past_orders,products_list):
            d=dict()
            d['order_id']=order.order_id
            d['status']=order.status
            d['amount']= order.amount
            array=[]
            for j,k in zip(prod,order.product_quantity):
                pdic=dict()
                pdic['product_name']=j.product_name
                pdic['product_id']=j.product_id
                pdic['product_quantity']=k
                array.append(pdic)
            d['products']=array
            dictlist.append(d)
        print(products_list)
        return render(req,'pastorders.html',{'orders':dictlist})
    return redirect('homepage')


def myorders(req):
    all_orders=Orders.objects.filter(user_id=req.user.id).order_by('timestamp')
    products_list=[]

    

    for i in all_orders:
        print("-------------------------")
        print(i.product_list)
        print("+++++++++++++++++++++++++++")
        productlist=list(i.product_list)
        p=Products.objects.filter(product_id__in=productlist)
        pds=[]
        for pids in i.product_list:
            
            for temps in p:

                if(str(temps.product_id)==str(pids)):
                    pds.append(temps)
                    break
        products_list.append(pds)

    print("==================")
    print(products_list)
    print("----------------")
    dictlist=[]
    for order,prod in zip(all_orders,products_list):
        d=dict()
        d['order_id']=order.order_id
        d['status']=order.status
        d['amount']=order.amount
        array=[]
        for j,k in zip(prod,order.product_quantity):
            pdic=dict()
            pdic['product_name']=j.product_name
            pdic['product_id']=j.product_id
            pdic['product_quantity']=k
            array.append(pdic)
        d['products']=array
        dictlist.append(d)
    print(products_list)
    return render(req,'myorders.html',{'orders':dictlist})

def notfound(req):
    return render(req,'pnf.html')

