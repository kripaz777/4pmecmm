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


class SearchView(BaseView):
	def get(self,request):
		if request.method == 'GET':
			query = request.GET['query']
			# self.views['search_product'] = Product.objects.filter((name__icontains =query) | (description__icontains =query) )
			lookups= Q(title__icontains=query) | Q(description__icontains=query)
            self.views['search_product']= Product.objects.filter(lookups).distinct()
        return render(request,'shop-search-result.html',self.views)

