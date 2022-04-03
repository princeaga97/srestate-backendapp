from django.contrib import admin
from property.models import Area,Broker,Contact, City, Client, Estate, EstateStatus,EstateType,InCharge, SubestateType ,photos



# class PropertyImageInline(admin.TabularInline):
#     model = photos
#     extra = 3


# class EstateAdmin(admin.ModelAdmin):
#     search_fields = ['estate_name']
#     inlines = [ PropertyImageInline ]

# Register your models here.
admin.site.register(Area)
admin.site.register(Broker)
admin.site.register(Contact)
admin.site.register(City)
admin.site.register(Client)
admin.site.register(Estate)
admin.site.register(EstateStatus)
admin.site.register(EstateType)
admin.site.register(InCharge)
admin.site.register(SubestateType)