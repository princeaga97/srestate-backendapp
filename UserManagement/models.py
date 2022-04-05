from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.validators import RegexValidator

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, fullname=None, password=None
                    ):
        if not email:
            raise ValueError('Users must have an Mobile Number')

        user = self.model(
            Mobile=self.normalize_email(email),
            name=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, Mobile, password):
        user = self.create_user(
            Mobile=Mobile,
            password=password,
        )
        user.is_admin = True
        user.is_active=True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

class Users(AbstractUser):
    id = models.IntegerField(default=0,primary_key=True)
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be entered in the format: '999999999'. 10 digit mobile number.")
    Mobile = models.CharField(validators=[phone_regex], max_length=10, blank=True , unique= True) # validators should be a list
    name = models.CharField(max_length=30, blank=True, null=True)
    otp = models.CharField(max_length=30, blank=True, null=True)

    USERNAME_FIELD = 'Mobile'

    objects = MyAccountManager()

    class Meta:
        db_table = "tbl_users"

    def __str__(self):
        return str(self.Mobile)+str(self.id)


    def has_perm(self, perm, obj=None): return self.is_superuser

    def has_module_perms(self, app_label): return self.is_superuser