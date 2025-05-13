import datetime
from datetime import date, datetime
from django.shortcuts import render,redirect
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Create your views here.

def checkuser(request):
    try:
        uid = request.session['login_id']
        userdata = login.objects.get(id=uid)

        try:
            profiledata = user_detail.objects.get(user=uid)

        except user_detail.DoesNotExist:
            profiledata = None

        manager = False
        if userdata.user_type == "manager":
            manager = True

        context = {
            'uid' : uid,
            'userdata': userdata,
            'profiledata': profiledata,
            'manager': manager
        }

        return context

    except:
        pass


def determine_time_slot(start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()

    if start_time < datetime.strptime("12:00", "%H:%M").time() <= end_time:
        return "morning"
    elif start_time < datetime.strptime("17:00", "%H:%M").time() <= end_time:
        return "afternoon"
    elif start_time < datetime.strptime("20:00", "%H:%M").time() <= end_time:
        return "evening"
    else:
        return "night"


def fetchturfs(request):
    uid = request.session['login_id']
    userdata = login.objects.get(id=uid)

    try:
        profiledata = user_detail.objects.get(user=uid)

    except user_detail.DoesNotExist:
        profiledata = None

    manager = False
    if userdata.user_type == "manager":
        manager = True

    if request.method == 'POST':
        areaname = request.POST.get('areaname')
        turfs = turf.objects.filter(Q(name__icontains=areaname) | Q(category__cate_name__icontains=areaname) |Q(location__area_name__icontains=areaname))

        combineddata = []

        for turfdata in turfs:
            # Fetch images for the current property
            turf_images = turf_images_table.objects.filter(turf=turfdata.id)

            # Check if there are any images for the property
            if turf_images.exists():
                # Include only the first image in the combined data
                first_image = turf_images.first()
                combineddata.append((turfdata, first_image))
            else:
                # If no images are found, include the property data with None for the image
                combineddata.append((turfdata, None))

        context = {
                    'uid': uid,
                    'userdata': userdata,
                    'profiledata': profiledata,
                    'manager': manager,
                    'combineddata': combineddata
                }

        return render(request, 'index.html',context)


def register(request):
    return render(request, "register.html")


def forgotpasswordpage(request):
    context = checkuser(request)
    return render(request,"forgotpassword.html", context)


def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST.get('email')

        try:
            user = login.objects.get(email=username)

        except login.DoesNotExist:
            user = None

        if user is not None:
            #################### Password Generation ##########################
            import random
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                       't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

            nr_letters = 6
            nr_symbols = 1
            nr_numbers = 3
            password_list = []

            for char in range(1, nr_letters + 1):
                password_list.append(random.choice(letters))

            for char in range(1, nr_symbols + 1):
                password_list += random.choice(symbols)

            for char in range(1, nr_numbers + 1):
                password_list += random.choice(numbers)

            print(password_list)
            random.shuffle(password_list)
            print(password_list)

            password = ""  #we will get final password in this var.
            for char in password_list:
                password += char

            ##############################################################


            msg = "hello here it is your new password  "+password   #this variable will be passed as message in mail

            ############ code for sending mail ########################

            from django.core.mail import send_mail

            send_mail(
                'Your New Password',
                msg,
                'rahulinfolabz@gmail.com',
                [username],
                fail_silently=False,
            )

            #now update the password in model
            cuser = login.objects.get(email=username)
            cuser.password = password
            cuser.save(update_fields=['password'])

            print('Mail sent')
            messages.info(request, 'mail is sent')
            return redirect(index)
        else:
            messages.info(request, 'This account does not exist')
    return redirect(index)

def createuser(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            role = request.POST.get("role")
            password1 = request.POST.get("password")
            password2 = request.POST.get("confirmpassword")

            if password1 == password2:
                registerdata = login(name=name, email=email, phone_number=phone, password=password1, user_type=role)
                registerdata.save()
                return redirect(loginuser)
    except:
        pass

    return render(request, "index.html")



def userprofile(request):
    context = checkuser(request)
    return render(request, "userprofile.html",context)


def edituserprofile(request):
    context = checkuser(request)
    return render(request, "edituserprofile.html",context)


def updateprofile(request):
    context = checkuser(request)
    try:
        if request.method == "POST":
            if 'update' in request.POST:
                uid = request.session['login_id']
                userdata = login.objects.get(id=uid)
                profiledata = user_detail.objects.get(user=uid)
                
                name = request.POST.get("name")
                phone = request.POST.get("phone")
                email = request.POST.get("email")
                address = request.POST.get("address")

                userdata.name = name
                userdata.phone_number = phone
                userdata.email = email
                profiledata.address = address

                if 'profile' in request.FILES:
                    profile = request.FILES["profile"]
                    print(profile)
                    profiledata.profile_pic = profile
                        
                userdata.save()
                profiledata.save()
                
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect(userprofile)
            else:
                messages.success(request, 'Some error occurs.')
                return redirect(userprofile)

    except:
        pass
        
    return render(request,"userprofile.html", context)


def completeprofilepage(request):
    context = checkuser(request)
    return render(request, "completeprofile.html", context)

def completeprofile(request):
    try:
        uid = request.session['login_id']
        if request.method == "POST":
            dob = request.POST.get("dob")
            address = request.POST.get("address")
            profilepic = request.FILES["profile"]

            insertdata = user_detail(user=login(id=uid), address=address, profile_pic=profilepic, dob=dob)
            insertdata.save()

            messages.success(request, "profile completed successfully")
            return redirect(userprofile)

    except:
        pass

    return render(request, "index.html")


def index(request):
    context = checkuser(request)
    return render(request, "index.html", context)



def loginpage(request):
    return render(request, 'login.html')



def loginuser(request):
    if request.method == "POST":
        uemail = request.POST.get("email")
        upwd = request.POST.get("password")

        try:
            logindata = login.objects.get(email=uemail, password=upwd)
            request.session['login_id'] = logindata.id
            request.session.save()

        except login.DoesNotExist:
            logindata = None


        if logindata is not None:
            messages.success(request, "Login Successfull !!")
            return redirect(index)

        else:
            messages.error(request, "Invalid Details")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'login.html')



def logout(request):
    try:
        del request.session['login_id']
        del request.session['login_pwd']
    except:
        pass

    return render(request, "index.html")


def changepwdpage(request):
    context = checkuser(request)
    return render(request, "changepwdpage.html", context)


def changepwd(request):
    context = checkuser(request)
    userdata = context.get("userdata")
    try:
        pwd = userdata.password

        if request.method == "POST":
            oldpwd = request.POST.get("oldpwd")
            newpwd = request.POST.get("newpwd")
            confirmpwd = request.POST.get("confirmpwd")

            if oldpwd == pwd:
                if newpwd == confirmpwd:
                    userdata.password = newpwd
                    userdata.save()
                    messages.success(request, 'Password Updated Successfully.')
                    del request.session['login_id']
                    return redirect(loginuser)
                else:
                    messages.error(request, "New Password and confirm not same")
                    return redirect(changepwdpage)
            else:
                messages.error(request, "Invalid Old Password")
                return redirect(changepwdpage)

    except userdata.DoesNotExist:
        messages.error(request, 'This account does not exist.')
        return redirect(index)


    return render(request, "index.html", context)




def services(request):
    context = checkuser(request)
    print(context)
    return render(request, "services.html", context)



def about(request):
    context = checkuser(request)
    return render(request, "about.html",context)



def contact(request):
    context = checkuser(request)
    return render(request, "contact.html", context)


def contactus(request):
    context = checkuser(request)
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        insert = inquiry(name=name, contact_number=phone, contact_email=email, subject=subject, description=message)
        insert.save()

    return render(request, 'index.html',context)



def userturflist(request):
    context = checkuser(request)
    try:
        allturfdata = turf.objects.all()
        combineddata = []
        # Iterate through each property data
        for turfdata in allturfdata:
            # Fetch images for the current property
            turf_images = turf_images_table.objects.filter(turf=turfdata.id)
            print(turf_images)
            # Check if there are any images for the property
            if turf_images.exists():
                # Include only the first image in the combined data
                first_image = turf_images.first()
                print(first_image)
                combineddata.append((turfdata, first_image))
            else:
                # If no images are found, include the property data with None for the image
                combineddata.append((turfdata, None))

        context.update({"combineddata": combineddata})
        return render(request, 'userturflist.html', context)

    except:
        pass

    return render(request,'userturflist.html')


def turfdetails(request, id):
    context = checkuser(request)
    try:
        turfdata = turf.objects.get(id=id)
        turfimages = turf_images_table.objects.filter(turf=id)
        context.update({"turfdata": turfdata,"turfimages":  turfimages})
    except:
        messages.error(request, "details does not exist")
    return render(request, 'turfdetails.html', context)


def blog(request):
    return render(request, 'blog.html')


def blogsingle(request):
    return render(request, 'blog-single.html')


def userbooking(request):
    return render(request, 'booking.html')

def selectdate(request, id):
    uid = request.session["login_id"]
    context = checkuser(request)
    try:
        profiledata = user_detail.objects.get(user=uid)

    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request,"please complete your profile")
        return redirect("/completeprofilepage")

    context.update({"turfid": id})
    return render(request, 'selectdate.html', context)


def selectslotpage(request):
    context = checkuser(request)
    if request.method == "POST":
        turfid = request.POST.get("turfid")
        userdate = request.POST.get("date")
        slotsdata = slot.objects.filter(turf=turfid, date=userdate)

        user_selected_date = datetime.strptime(userdate, "%Y-%m-%d").date()
        current_date = date.today()

        if user_selected_date < current_date:
            messages.error(request, "Selected date cannot be less than the current date")
            return redirect(userturflist)

        context.update({"slotsdata": slotsdata, "turfid": turfid})
    return render(request,'selectslot.html', context)


def selectslot(request):
    context = checkuser(request)
    try:
        if request.method == 'POST':
            selected_slot_id = request.POST.get('selectedSlot')
            turfid = request.POST.get('turfid')
            if selected_slot_id is not None:
                context.update({"slotid": selected_slot_id, "turfid": turfid})
                messages.success(request, "Slot is selected Now you can pay")
                return render(request, "paymentmethod.html", context)
            else:
                messages.error(request, "select slot")

    except:
        messages.error(request, "Some error occured")
    return render(request, "index.html", context)

def paymentmethod(request):
    context = checkuser(request)
    if request.method == "POST":
        turfid = request.POST.get("turfid")
        slotid = request.POST.get("slotid")
        if slotid is not None and turfid is not None:
            context.update({"turfid": turfid, "slotid": slotid})
    return render(request, "paymentmethod.html", context)

def paymentpage(request):
    context = checkuser(request)
    slotid = request.POST.get("slotid")
    turfid = request.POST.get("turfid")
    if slotid is not None and turfid is not None:
        context.update({"turfid": turfid, "slotid": slotid})
    return render(request, "payment.html", context)


def processpayment(request):
    context = checkuser(request)
    uid = request.session['login_id']
    if request.method == "POST":
        turfid = request.POST.get("turfid")
        slotid = request.POST.get("slotid")
        method = request.POST.get("paymentMethod")

        turfdata = turf.objects.get(id=turfid)
        amount = turfdata.price_per_slot

        if method is not None:
            if method == "cash":

                slotsdata = slot.objects.get(id=slotid)
                slotsdata.is_booked = True
                slotsdata.save()

                insertbooking = booking(user=login(id=uid), turf=turf(id=turfid), slot=slot(id=slotid), booking_status="booked")
                insertbooking.save()

                insertpayemnt = payment(user=login(id=uid), booking=insertbooking, amount=amount, payment_method=method, transaction_id="None",payment_date_time="",payment_status="complete")
                insertpayemnt.save()

                context.update({"turfid": turfid, "slotid": slotid, 'amount': amount, 'method': method})
                return redirect("/userbookings", context)


            elif method == "creditCard" or method == "debitCard":
                if slotid is not None and turfid is not None:

                    context.update({"turfid": turfid, "slotid": slotid, 'amount': amount, 'method': method})

                return render(request, "payment.html", context)

            else:
                messages.info(request,"please select the payment method")
                return redirect(paymentmethod)
        else:
            messages.info(request,"please select the payment method")
            return redirect(paymentmethod)

    return render(request, "index.html", context)


import uuid
def generate_transaction_id():
    return str(uuid.uuid4())

def savepayment(request):
    context = checkuser(request)
    uid = request.session['login_id']
    if request.method == "POST":
        turfid = request.POST.get("turfid")
        slotid = request.POST.get("slotid")
        method = request.POST.get("method")
        amount = request.POST.get("amount")
        cardNumber = request.POST.get("cardNumber")
        expiryDate = request.POST.get("expiryDate")
        cvv = request.POST.get("cvv")

        carddata = card.objects.get(user=uid)
        number = carddata.card_number
        balance = carddata.card_balance
        expdate = carddata.expiration_date
        ccvv = carddata.cvv

        if cardNumber == number and int(amount) < balance and expiryDate == expdate and cvv == ccvv:

            insertbooking = booking(user=login(id=uid), turf=turf(id=turfid), slot=slot(id=slotid),
                                    booking_status="booked")
            insertbooking.save()

            bookingid = insertbooking.id

            transid = generate_transaction_id()
            insertpayemnt = payment(user=login(id=uid), booking=booking(id=bookingid), amount=amount, payment_method=method,
                                    transaction_id=transid, payment_date_time="", payment_status="complete")
            insertpayemnt.save()

            slotsdata = slot.objects.get(id=slotid)
            slotsdata.is_booked = True
            slotsdata.save()

            messages.success(request, "slot is booked payment is done")

        else:
            messages.error(request, "Invalid Details")
            return redirect(userturflist)


    return redirect("/userbookings", context)


def userpayemnts(request):
    context = checkuser(request)
    try:
        uid = request.session['login_id']
        paymentdata = payment.objects.filter(user=uid)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(paymentdata, 2)  # Set the number of items per page

        try:
            paymentdata = paginator.page(page)
        except PageNotAnInteger:
            paymentdata = paginator.page(1)
        except EmptyPage:
            paymentdata = paginator.page(paginator.num_pages)

        context.update({'paginator': paginator, 'page': int(page), 'paymentdata': paymentdata})

        return render(request, "userpayments.html", context)
    except:
        pass

    return render(request, "index.html")


def userbookings(request):
    context = checkuser(request)
    uid = request.session['login_id']
    bookingdata = booking.objects.filter(user=login(id=uid))

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(bookingdata, 2)  # Set the number of items per page

    try:
        bookingdata = paginator.page(page)
    except PageNotAnInteger:
        bookingdata = paginator.page(1)
    except EmptyPage:
        bookingdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'bookingdata': bookingdata})
    return render(request, "userbookings.html", context)

def addturfpage(request):
    context = checkuser(request)
    uid = request.session["login_id"]
    context = checkuser(request)
    try:
        profiledata = user_detail.objects.get(user=uid)

    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "please complete your profile")
        return redirect("/completeprofilepage")

    categories = turf_categories.objects.all()
    locations = location.objects.all()
    context.update({'categories': categories, 'locations': locations})
    print(context)
    return render(request, "addturf.html", context)


def addturf(request):
    try:
        if request.method == "POST":
            manager = request.POST.get("manager")
            category = request.POST.get("category")
            loc = request.POST.get("location")
            turfname = request.POST.get("name")
            desc = request.POST.get("description")
            phone = request.POST.get("contact_number")
            email = request.POST.get("contact_email")
            price = request.POST.get("price_per_slot")
            capacity = request.POST.get("maximum_capacity")
            rules = request.POST.get("rules")

            insertturf = turf(manager=login(id=manager), category=turf_categories(id=category),
                              location=location(id=loc), name=turfname, description=desc, contact_number=phone,
                              contact_email=email, price_per_slot=price, maximum_capacity=capacity,
                              rules_and_regulations=rules)
            insertturf.save()
            messages.success(request, "turf inserted successfull")
            return redirect(index)

    except:
        messages.error("Data not inserted")

    return render(request,"index.html")

def turflist(request):
    uid = request.session["login_id"]
    context = checkuser(request)
    turfdata = turf.objects.filter(manager=login(id=uid))
    # Paginate
    page = request.GET.get('page', 1)
    paginator = Paginator(turfdata, 6)  # Show 10 items per page
    try:
        turfdata = paginator.page(page)
    except PageNotAnInteger:
        turfdata = paginator.page(1)
    except EmptyPage:
        turfdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'turfdata': turfdata})

    return render(request, "turflist.html", context)


def addimages(request):
    uid = request.session["login_id"]
    context = checkuser(request)
    try:
        profiledata = user_detail.objects.get(user=uid)

    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "please complete your profile")
        return redirect("/completeprofilepage")


    turfdata = turf.objects.all()
    context.update({'turfdata': turfdata})
    return render(request, "addimages.html",context)


def addphotossubmit(request):
    if request.method == 'POST':
        turfid = request.POST.get("turfid")
        images = request.FILES.getlist('photos')
        for image in images:
            userdata = turf_images_table(turf=turf(id=turfid), photo=image)
            userdata.save()
        messages.success(request, 'Turf Images added successfully.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Some error occured')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def timeslots(request):
    context = checkuser(request)
    uid = request.session["login_id"]
    context = checkuser(request)
    try:
        profiledata = user_detail.objects.get(user=uid)

    except user_detail.DoesNotExist:
        profiledata = None
        messages.error(request, "please complete your profile")
        return redirect("/completeprofilepage")

    turfdata = turf.objects.filter(manager=login(id=uid))
    context.update({'turfdata': turfdata})
    return render(request, "timeslots.html", context)


def saveslot(request):
    context = checkuser(request)
    try:
        if request.method == "POST":
            turfid = request.POST.get("turfid")
            userdate = request.POST.get("date")
            startTime = request.POST.get("startTime")
            endTime = request.POST.get("endTime")
            timeSlot= determine_time_slot(startTime, endTime)

            user_selected_date = datetime.strptime(userdate, "%Y-%m-%d").date()
            current_date = date.today()

            if user_selected_date < current_date:
                messages.error(request, "Selected date cannot be less than the current date")
                return redirect(timeslots)

            else:
                insertslot = slot(turf=turf(id=turfid), date=user_selected_date, time_slot=timeSlot, start_time=startTime, end_time=endTime)
                insertslot.save()
                messages.success(request, "Slot inserted successfull")
                return redirect(index)

    except Exception as e:

        messages.error(request,f"Error: {e}")

    return render(request, "index.html", context)



def viewslots(request):
    context = checkuser(request)
    uid = request.session["login_id"]
    turfdata = turf.objects.filter(manager=login(id=uid))
    turf_ids = turfdata.values_list('id', flat=True)
    slotsdata = slot.objects.filter(turf__in=turf_ids)

    page = request.GET.get('page', 1)
    paginator = Paginator(slotsdata, 6)
    try:
        slotsdata = paginator.page(page)
    except PageNotAnInteger:
        slotsdata = paginator.page(1)
    except EmptyPage:
        slotsdata = paginator.page(paginator.num_pages)

    context.update({'paginator': paginator, 'page': int(page), 'slotsdata': slotsdata})

    return render(request, "viewslots.html", context)



def editturfpage(request,id):
    context = checkuser(request)
    turfdata = turf.objects.get(id=id)
    categories = turf_categories.objects.all()
    locations = location.objects.all()
    context.update({'turfdata': turfdata, 'categories': categories, 'locations': locations})
    return render(request, "editturfs.html", context)


def updateturf(request,id):
    try:
        if request.method == "POST":
            uid = request.session['login_id']
            turfdata = turf.objects.get(id=id, manager=login(id=uid))
            name = request.POST.get("name")
            description = request.POST.get("description")
            category = request.POST.get("category")
            loc = request.POST.get("location")
            phone = request.POST.get("contact_number")
            email = request.POST.get("contact_email")
            price = request.POST.get("price_per_slot")
            capacity = request.POST.get("maximum_capacity")
            rules = request.POST.get("rules")

            turfdata.name = name
            turfdata.contact_number = phone
            turfdata.contact_email = email
            turfdata.price_per_slot = price
            turfdata.maximum_capacity = capacity
            turfdata.rules_and_regulations = rules
            turfdata.description = description
            turfdata.location = location(id=loc)
            turfdata.category = turf_categories(id=category)

            turfdata.save()

            messages.success(request, ' Turf data updated successfully.')
            return redirect(turflist)

        else:
            messages.success(request, 'Some error occurs.')
            return redirect(index)

    except:
        pass

    return render(request, "index.html")

def removeturf(request,id):
    context =checkuser(request)

    try:
        turdata = turf.objects.get(id=id)
        turdata.delete()
        messages.success(request,"Turf removed successfully !!")
        return redirect(turflist)

    except:
        pass

    return render(request, "index.html",context)
def removeslot(request, id):
    context = checkuser(request)
    try:
        slotdata = slot.objects.get(id=id)
        slotdata.delete()
        messages.success(request,"slot removed successfully !!")
        return redirect(viewslots)
    except:
        messages.error(request,"slot data does not exist")

    return render(request, "viewslots.html", context)


def turfbookings(request):
    context = checkuser(request)
    try:
        bookingdata = booking.objects.all()
        print(bookingdata)
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(bookingdata, 2)  # Set the number of items per page

        try:
            bookingdata = paginator.page(page)
        except PageNotAnInteger:
            bookingdata = paginator.page(1)
        except EmptyPage:
            bookingdata = paginator.page(paginator.num_pages)

        context.update({'paginator': paginator, 'page': int(page), 'bookingdata': bookingdata})


        return render(request, "turfbookings.html", context)

    except:
        messages.error("Booking data does not exist")

    return render(request, "index.html", context)


def turfpayments(request):
    context = checkuser(request)
    try:
        paymentsdata = payment.objects.all()

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(paymentsdata, 2)  # Set the number of items per page

        try:
            paymentsdata = paginator.page(page)
        except PageNotAnInteger:
            paymentsdata = paginator.page(1)
        except EmptyPage:
            paymentsdata = paginator.page(paginator.num_pages)
        context.update({'paginator': paginator, 'page': int(page), 'paymentsdata': paymentsdata})

        return render(request, "turfpayments.html", context)

    except:
        messages.error(request,"Payment data does not exist")

    return render(request, "index.html", context)
