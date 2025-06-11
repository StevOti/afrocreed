from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q
import json
from cart.cart import Cart


# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)

            # Get their saved cart from database
            saved_cart = current_user.old_cart

            # Convert database string to python dictionary

            if saved_cart:
                # convert to dictionary using json
                converted_cart = json.loads(saved_cart)

                # add the loaded cart dictionary to our sessions
                # get the cart
                cart = Cart(request)

                # Loop through the cart and items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You have been logged in successfully!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, please try again!"))
            return redirect('login') 

    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out!"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have been registered successfully! Please update your information."))
            return redirect('update_info')
        else:
            messages.success(request, ("Something went wrong! Please try again"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
    

def product(request, pk):
    product = Product.objects.get(id=pk)
    products = Product.objects.all()
    return render(request, 'product.html', {'product': product, 'products': products})

def category(request, foo):
    # Replace hyphens with spaces in the category name
    foo = foo.replace("-", " ")
    categories = Category.objects.all()

    # Get the category from the url
    try:
        # Get the category from the database
        category = Category.objects.get(name=foo)
        # Get the products in that category
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'category': category, 'products': products, 'categories': categories})
    except:
        messages.success(request, ("This category does not exist!"))
        return redirect('home')
    

# def category_summary(request):
#     categories = Category.objects.all()
#     return render(request, 'category_summary.html', {'categories': categories})

def update_user(request):
    if request.user.is_authenticated:
        user = request.user  #  This is the correct User instance
        user_form = UpdateUserForm(request.POST or None, instance=user)
        if user_form.is_valid():
            user_form.save()
            login(request, user)  #  Still the User instance
            messages.success(request, "Your account has been updated successfully!")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(request, "You need to be logged in to update your account!")
        return redirect('home')

    

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated successfully!")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                # Add this return statement to handle invalid form submission
                return render(request, 'update_password.html', {'form': form})
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, "You need to be logged in to update your password!")
        return redirect('home')
    

def update_info(request):
    if request.user.is_authenticated:
        profile_instance = request.user.profile  # Get the associated profile
        Shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        # get original form
        form = UserInfoForm(request.POST or None, instance=profile_instance)

        # get shipping form
        shipping_form = ShippingForm(request.POST or None, instance=Shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            # Save original form
            form.save()
            # Save shipping form
            shipping_form.save()
            messages.success(request, "Your Information has been updated successfully!")
            return redirect('home')
        return render(request, 'update_info.html', {'form': form, 'shipping_form':shipping_form})
    else:
        messages.success(request, "You need to be logged in to update your account!")
        return redirect('home')
    

def search(request):
    # Determine if they filled out the form
    if request.method == 'POST':
        searched = request.POST['searched']
        # Query the products DB model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test  for null
        if not searched:
            messages.success(request, ("No results found!"))
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
        
    else:
        return render(request, 'search.html', {})
    
def cargo(request):
    return render(request, 'cargo.html', {})

def events(request):
    return render(request, 'events.html', {})

def tours(request):
    return render(request, 'tours.html', {})

def contact(request):
    return render(request, 'contact.html', {})


