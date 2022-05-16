from django.shortcuts import render,redirect
from .models import *
# Create your views here.
from django.views.generic import View
from django.core.mail import EmailMessage


class BaseView(View):
	views = {}


class HomeView(BaseView):
	def get(self,request):
		self.views['categories'] = Category.objects.all()
		self.views['subcategories'] = SubCategory.objects.all()
		self.views['sliders'] = Slider.objects.all()
		self.views['ads'] = Ad.objects.all()
		self.views['products'] = Product.objects.filter(stock = 'In Stock')
		self.views['sale_products'] = Product.objects.filter(labels = 'sale', stock = 'In Stock')
		self.views['hot_products'] = Product.objects.filter(labels = 'hot',stock = 'In Stock')
		self.views['new_products'] = Product.objects.filter(labels = 'new')

		return render(request,'shop-index.html',self.views)


class DetailView(BaseView):
	def get(self,request,slug):
		self.views['product_detail'] = Product.objects.filter(slug = slug)

		return render(request,'shop-item.html',self.views)


class CategoryView(BaseView):
	def get(self,request,slug):
		cat_id = Category.objects.get(slug = slug).id
		cat_name = Category.objects.get(slug = slug).name
		self.views['cat_name'] = cat_name
		self.views['subcategories'] = SubCategory.objects.filter(category_id = cat_id)
		self.views['category_products'] = Product.objects.filter(category_id = cat_id)

		return render(request,'category.html',self.views)

class SubCategoryView(BaseView):
	def get(self,request,slug):
		subcat_id = SubCategory.objects.get(slug = slug).id
		self.views['subcategory_products'] = Product.objects.filter(subcategory_id = subcat_id)

		return render(request,'subcategory.html',self.views)

from django.db.models import Q
class SearchView(BaseView):
	def get(self,request):
		if request.method == 'GET':
			query = request.GET['query']
			# self.views['search_product'] = Product.objects.filter((name__icontains =query) | (description__icontains =query) )
			lookups= Q(name__icontains=query) | Q(description__icontains=query)
			self.views['search_product']= Product.objects.filter(lookups).distinct()
			self.views['search_for'] = query
		return render(request,'shop-search-result.html',self.views)

from django.contrib import messages
from django.contrib.auth.models import User
import random
def signup(request):
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		cpassword = request.POST['cpassword']

		if password == cpassword:
			randomlist = random.sample(range(1000, 9999), 1)

			if User.objects.filter(username = username).exists():
				messages.error(request,'The username is already taken')
				return redirect('/signup')

			elif User.objects.filter(email = email).exists():
				messages.error(request,'The email is already taken')
				return redirect('/signup')
			else:
				user = User.objects.create_user(
					username = username,
					email = email,
					password = password
					)
				user.save()
				User.objects.filter(username = username).update(is_active = False)

				code = OTP.objects.create(
					user = username,
					token = randomlist[0]
					)
				code.save()

				email = EmailMessage(
				    'Email verification code',
				    f'Please enter email verification code {randomlist[0]}',
				    '<your email add>',
				    [email]
				    )
				email.send()
				messages.error(request,'The otp is sent to your email.')
				return redirect('verify')
		else:
			messages.error(request,'The password does not match')
			return render(request,'shop-standart-forms.html')
	return render(request,'shop-standart-forms.html')

def Verification_code(request):
	
	if request.method == 'POST':
		code = request.POST['code']
		username = request.POST['username']
		if OTP.objects.filter(token = code,user=username).exists():
			User.objects.filter(username = username).update(is_active = True)
			return redirect('verify')
	return render(request,'code.html')


from django.contrib.auth.decorators import login_required
@login_required
def cart(request,slug):
	if Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).exists():
		quantity = Cart.objects.get(slug = slug,user=request.user.username,checkout = False).quantity
		price = Product.objects.get(slug = slug).price
		discounted_price = Product.objects.get(slug = slug).discounted_price
		quantity = quantity +1
		if discounted_price >0:
			original_price = discounted_price
			total = original_price*quantity
		else:
			total = price*quantity

		
		Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).update(quantity = quantity,total = total)

	else:
		username = request.user.username
		price = Product.objects.get(slug = slug).price
		discounted_price = Product.objects.get(slug = slug).discounted_price
		if discounted_price >0:
			original_price = discounted_price
		else:
			original_price = price
		data = Cart.objects.create(
			user = username,
			slug = slug,
			items = Product.objects.filter(slug = slug)[0],
			total = original_price
			)
		data.save()

	return redirect('/mycart')


def deletecart(request,slug):
	if Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).exists():
		Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).delete()

	return redirect('/mycart')

def decreasecart(request,slug):
	if Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).exists():
		quantity = Cart.objects.get(slug = slug,user=request.user.username,checkout = False).quantity
		if quantity >1:
			quantity = quantity -1
			Cart.objects.filter(slug = slug,user=request.user.username,checkout = False).update(quantity = quantity)
	return redirect('/mycart')


class CartView(BaseView):
	def get(self,request):
		self.views['cart_product'] = Cart.objects.filter(user=request.user.username,checkout = False)
		return render(request,'shop-shopping-cart.html',self.views)



# ------------------------------------------------API-----------------------------------------------------------------------
from rest_framework import serializers, viewsets
from .serializers import *
from rest_framework import generics

from django_filters.rest_framework import  DjangoFilterBackend
from rest_framework.filters import OrderingFilter,SearchFilter

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductFilterViewSet(generics.ListAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	filter_backends = [DjangoFilterBackend,OrderingFilter,SearchFilter]
	filter_fields = ['id','name','price','labels','category','subcategory']
	ordering_fields = ['price','id','name']
	search_fields = ['name','description']


from rest_framework import status
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from rest_framework.views import APIView
# from snippets.serializers import SnippetSerializer
class ProductCRUDViewSet(APIView):
	def get_object(self,pk):
		try:
			return Product.objects.get(pk = pk)
		except:
			print("The id is not in db")

	def get(self,request,pk,format = None):
		product = self.get_object(pk)
		serializer = ProductSerializer(product)
		return Response(serializer.data)

	def post(self,request,pk):
		serializer = ProductSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self,request,pk):
		serializer = ProductSerializer(product, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self,request,pk):
		product.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)