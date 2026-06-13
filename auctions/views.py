from django.contrib.auth import authenticate, login, logout
from .models import User, Listing, Category
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, CategoryForm
from django.urls import reverse



def index(request):
    activate_listings = Listing.objects.filter(active=True).order_by('-id')
    return render(request, "auctions/index.html", {
        "listings": activate_listings
    })



def categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })

@login_required
def create_category(request):
    form = CategoryForm(request.POST or None)
    if request.POST.get("name") and form.is_valid():
        form.save()
        return redirect("categories")
    return render(request, "auctions/create_category.html", {
        "form": form,
        "title": "Create Category"
    })


def listing(request, listing_id):
    single_listing = Listing.objects.get(id=listing_id)
    return render(request, "auctions/listing.html", {
        "listing": single_listing
    })




@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
             listing = form.save(commit=False)
             listing.owner = request.user
             listing.save()
             return redirect("listing", listing_id=listing.id)
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        "form": form,
        "title": "Create Listing"
    })
        

@login_required
def watchlist(request):
    listings = request.user.watched_listings.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings
    })

@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.watcherlist.add(request.user)
    return redirect("watchlist")

    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

