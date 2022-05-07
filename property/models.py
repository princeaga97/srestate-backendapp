from ast import Try
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import RegexValidator




class City(models.Model):
    #id =  models.IntegerField(primary_key=True)
    city_name = models.CharField(unique=True, max_length=128)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        #db_table = 'city'
    def __str__(self):
        return self.city_name



class Area(models.Model):
    #id =  models.IntegerField(primary_key=True)
    area_name = models.CharField(max_length=128)
    city = models.CharField(max_length=128, default= "surat")
    pincode = models.IntegerField(blank= True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        #db_table = 'area'
        unique_together = (('area_name', 'city'),)
    def __str__(self):
        return self.area_name + "," + self.city.city_name


class Apartment(models.Model):
    #id =  models.IntegerField(primary_key=True)
    apartment_name = models.CharField(max_length=128)
    area = models.CharField(max_length=128, default= "")
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = True
        #db_table = 'area'


class EnquiryQuerys(models.Model):
    broker_number = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=10)
    type = models.CharField(max_length=128)
    estate_type = models.CharField(max_length=128)
    budget = models.CharField(max_length=128)
    area = models.CharField(max_length=128)
    class Meta:
        managed = True
        #db_table = 'area'











class Client(models.Model):
    #id =  models.IntegerField(primary_key=True)
    client_name = models.CharField(max_length=255)
    client_address = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    mobile = models.CharField(max_length=64, blank=True)
    mail = models.CharField(max_length=64, blank=True)
    client_details = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        managed = True
        #db_table = 'client'


class Contact(models.Model):
    #id =  models.IntegerField(primary_key=True)
    client = models.CharField(max_length=128, default= "surat")
    employee = models.CharField(max_length=128, default= "surat")
    estate = models.CharField(max_length=128, default= "surat")
    contact_time = models.TextField()  # This field type is a guess.
    contact_details = models.TextField()  # This field type is a guess.

    class Meta:
        managed = True
        #db_table = 'contact'


class Estate(models.Model):
    #id =  models.AutoField(primary_key = True)
    estate_name = models.CharField(max_length=255)
    city = models.CharField(max_length=128, default= "")
    estate_type = models.CharField(max_length=128, default= "")
    floor_space = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    number_of_balconies = models.IntegerField(blank=True)
    balconies_space = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    number_of_bedrooms = models.IntegerField(blank=True)
    number_of_bathrooms = models.IntegerField(blank=True)
    number_of_garages = models.IntegerField(blank=True)
    number_of_parking_spaces = models.IntegerField(blank=True)
    pets_allowed = models.IntegerField(blank=True)
    estate_description = models.TextField()  # This field type is a guess.
    estate_status = models.CharField(max_length=128, default= "")
    is_deleted = models.BooleanField(default=False)
    society = models.CharField(max_length=128, default= "")
    area = models.CharField(max_length=128, default= "")
    broker_mobile = models.CharField(max_length=128, default= "")
    broker_name = models.CharField(max_length=128, default= "")
    budget = models.IntegerField(blank=True)

    class Meta:
        managed = True



class EstateStatus(models.Model):
    #id =  models.AutoField(primary_key = True)
    estate_status_name = models.CharField(unique=True, max_length=64)
    is_deleted  = models.BooleanField(default=0)
    class Meta:
        managed = True
    def __str__(self):
        return  self.estate_status_name
        #db_table = 'estate_status'


class EstateType(models.Model):
    #id =  models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=128)
    is_deleted = models.BooleanField(default=0)

    class Meta:
        managed = True
    def __str__(self):
        return  self.type_name

class InCharge(models.Model):
    #id =  models.IntegerField(primary_key=True)
    estate = models.CharField(max_length=128, default= "")
    broker = models.CharField(max_length=128, default= "")
    date_from = models.DateField()
    date_to = models.DateField(blank=True)

    class Meta:
        managed = True


class SubestateType(models.Model):
    #id =  models.IntegerField(primary_key=True)
    subtype_name = models.CharField(max_length=128)
    estate_type = models.CharField(max_length=128, default= "surat")

    class Meta:
        managed = True


class photos(models.Model):
    # title field
    estate_id = models.CharField(max_length=128, default= "")
    #image field
    image = CloudinaryField('image')

    class Meta:
        managed = True

    def __str__(self):
        return  self.estate_id




class Broker(models.Model):
    #id =  models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be entered in the format: '999999999'. 10 digit mobile number.")
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True , unique= True) # validators should be a list
    class Meta:
        managed = True

