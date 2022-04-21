from django.shortcuts import render
from .models import *
# Create your views here.
from django.views.generic import View

class BaseView(View):
	views = {}


class HomeView(BaseView):
	def get(self,request):
		self.views['categories'] = Category.objects.all()
		self.views['subcategories'] = SubCategory.objects.all()
		self.views['sliders'] = Slider.objects.all()
		self.views['ads'] = Ad.objects.all()
		self.views['products'] = Product.objects.filter(stock = 'In Stock')

		return render(request,'shop-index.html',self.views)


