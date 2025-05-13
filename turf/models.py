from django.db import models
from django.utils.safestring import mark_safe
# Create your models here


class login(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, default="admin@123")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(max_length=30, choices=[('user', 'user'), ('manager', 'manager')], default="user")

    def __str__(self):
        return self.name


class user_detail(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    address = models.TextField()
    profile_pic = models.ImageField(upload_to="profiles")
    dob = models.DateField()

    def profile_photo(self):
        return mark_safe('<img src="{}" width="100px"/>'.format(self.profile_pic.url))



class state(models.Model):
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return self.state_name


class city(models.Model):
    state_name = models.ForeignKey(state,on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name



class location(models.Model):
    city_name = models.ForeignKey(city, on_delete=models.CASCADE)
    area_name = models.CharField(max_length=200)
    postal_code = models.IntegerField()

    def __str__(self):
        return self.area_name


class turf_categories(models.Model):
    cate_name = models.CharField(max_length=200)

    def __str__(self):
        return self.cate_name


class turf(models.Model):
    manager = models.ForeignKey(login, on_delete=models.CASCADE)
    category = models.ForeignKey(turf_categories, on_delete=models.CASCADE)
    location = models.ForeignKey(location, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    contact_number = models.CharField(max_length=20)
    contact_email = models.EmailField()
    price_per_slot = models.IntegerField()
    duration_per_slot = models.IntegerField()
    maximum_capacity = models.IntegerField(default=100)
    is_available = models.CharField(max_length=50, choices=[("available", "available"), ("unavailable", "unavailable")], default="available")
    rules_and_regulations = models.TextField()
    is_featured = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class turf_images_table(models.Model):
    turf = models.ForeignKey(turf, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos")

    def photos(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.photo.url))




class slot(models.Model):
    turf = models.ForeignKey(turf, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=30, choices=[('morning', 'morning'), ('evening', 'evening'), ('afternoon', 'afternoon'), ('night', 'night') ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        time = f"{self.time_slot} - {self.start_time} - {self.end_time}"
        return time




class booking(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    turf = models.ForeignKey(turf, on_delete=models.CASCADE)
    slot = models.ForeignKey(slot, on_delete=models.CASCADE)
    booking_status = models.CharField(max_length=60, choices=[("booked", "booked"), ("not_booked", "not_booked")], default="not_booked")
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.turf.name}  -  {self.user.name}  -  {self.slot}"



class payment(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    booking = models.ForeignKey(booking, on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=20, choices=[('Credit Card', 'Credit Card'), ('Debit Card', 'Debit Card'), ('Cash', 'Cash')])
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date_time = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=60,choices=[("pending", "pending"), ("complete", "complete")], default="pending")

    def __str__(self):
        return self.payment_status


class card(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    cardholder_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=16)
    card_balance = models.IntegerField(default=1000000)
    expiration_date = models.CharField(max_length=20)
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.cardholder_name}'s Card ending in {self.card_number[-4:]}"


class feedback(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    turf = models.ForeignKey(turf, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name


class complaint(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)
    description = models.TextField()
    complaint_status = models.CharField(max_length=60,choices=[("pending", "pending"), ("resolved", "resolved")], default="resolved")
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.name


class inquiry(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    contact_email = models.EmailField()
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[("pending", "pending"), ("resolved", "resolved")], default="resolved")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
