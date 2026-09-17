from django.contrib.auth import authenticate, login, logout
from .models import User, Listing, Category, Bid
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ListingForm, CategoryForm, CommentForm
from django.urls import reverse
from decimal import Decimal, InvalidOperation



# Helper function to render an error page with a given message
def render_error(request, message):
    return render(request, "auctions/error.html", {
        "message": message
    })

# Helper function when a page does not exist, while on production with DEBUG=False
def page_not_found(request, exception):
    return render(request, "auctions/error.html", {
        "message": "The page does not exist."
    }, status=404,)

# Helper function to get the current price of a listing
def get_current_price(listing):
    highest_bid = listing.bids.order_by('-amount').first()
    return highest_bid.amount if highest_bid else listing.price

# View functions for all the auctions listings
def index(request):
    listings = Listing.objects.filter(active=True).order_by('-id')
    for listing in listings:
        listing.current_price = get_current_price(listing)
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def closed_listings(request):
    listings = Listing.objects.filter(active=False).order_by('-id')
    for listing in listings:
        listing.current_price = get_current_price(listing)
    return render(request, "auctions/index.html", {
        "listings": listings
    })




def categories(request):
    categories = Category.objects.all().order_by('name')
    for category in categories:
        category.active_listing_count = category.listings.filter(active=True).count()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return render_error(request, "Category not found.")
    listings = Listing.objects.filter(category=category, active=True).order_by('-id')
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings,
        "categories": Category.objects.all().order_by('name')
    })




@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("categories")
        messages.error(request, "Error creating category. Please check the form for errors.")
    else:
        form = CategoryForm()

    return render(request, "auctions/create_category.html", {
        "form": form,
        "title": "Create Category"
    })


def listing_context(request, single_listing, comment_form=None):
    highest_bid = single_listing.bids.order_by('-amount').first()
    current_price = get_current_price(single_listing)
    user_bid = None
    if request.user.is_authenticated:
        user_bid = single_listing.bids.filter(bidder_user=request.user).order_by('-amount').first()
        
    is_watching = False
    if request.user.is_authenticated:
        is_watching = single_listing.watcherlist.filter(pk=request.user.pk).exists()
    return {
        "listing": single_listing,
        "highest_bid": highest_bid,
        "current_price": current_price,
        "is_watching": is_watching,
        "comment_form": comment_form or CommentForm(),
        "comments": single_listing.comments.order_by('-id'),
        "user_bid": user_bid,
    }



def listing(request, listing_id):
    try:
        single_listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return render_error(request, "Listing not found.")
    return render(request, "auctions/listing.html", listing_context(request, single_listing))




@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, "Listing created successfully.")
            return redirect("listing", listing_id=listing.id)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        "form": form,
        "title": "Create a new Listing"
    })



@login_required
def watchlist(request):
    listings = request.user.watched_listings.all().order_by('-id')
    for listing in listings:
        listing.current_price = get_current_price(listing)
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings,
    })

@login_required
def add_to_watchlist(request, listing_id):
    if request.method != "POST":
        return redirect("listing", listing_id=listing_id)
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.watcherlist.filter(pk=request.user.pk).exists():
        messages.info(request, "Listing is already in your watchlist.")
    else:
        listing.watcherlist.add(request.user)
        messages.success(request, "Listing added to watchlist.")
    return redirect("listing", listing_id=listing_id)


@login_required
def remove_from_watchlist(request, listing_id):
    if request.method != "POST":
        return redirect("listing", listing_id=listing_id)
    listing = get_object_or_404(Listing, pk=listing_id)

    if listing.watcherlist.filter(pk=request.user.pk).exists():
        listing.watcherlist.remove(request.user)
        messages.success(request, "Listing removed from watchlist.")
    else:
        messages.info(request, "Listing is not in your watchlist.")
    return redirect("listing", listing_id=listing_id)


@login_required
def add_to_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method != "POST":
        return redirect("listing", listing_id=listing_id)

    if not listing.active:
        messages.error(request, "This auction is closed.")
        return redirect("listing", listing_id=listing_id)
    
    initial_amount = request.POST.get("bid_amount", "")
    context = listing_context(request, listing)
    context["bid_amount"] = initial_amount

    if request.user == listing.owner:
        context["bid_error"] = "You cannot bid on your own listing."
        return render(request, "auctions/listing.html", context)
    try:
        bid_amount = Decimal(initial_amount)
    except (ValueError, InvalidOperation, TypeError):
        context["bid_error"] = "Enter a valid number for the bid."
        return render(request, "auctions/listing.html", context)

    listing_has_bids = listing.bids.exists()
    current_price = context["current_price"]

    if listing_has_bids and bid_amount <= current_price:
        context["bid_error"] = (f"Bid must be higher than the current price of ${current_price}.")
        return render(request, "auctions/listing.html", context)

    if not listing_has_bids and bid_amount < listing.price:
        context["bid_error"] = (f"Your first bid must be at least the starting price of ${listing.price}.")
        return render(request, "auctions/listing.html", context)

    Bid.objects.create(
        listing=listing,
        
        bidder_user=request.user,
        amount=bid_amount
    )
    messages.success(request, "Bid placed successfully.")
    return redirect("listing", listing_id=listing_id)



@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.commenter_user = request.user
            comment.save()
            messages.success(request, "Comment added successfully.")
            return redirect("listing", listing_id=listing_id)
        else:
            messages.error(request, "Please correct the errors below.")
            context = listing_context(request, listing, comment_form=form)
            return render(request, "auctions/listing.html", context)
    return redirect("listing", listing_id=listing_id)


@login_required
def close_listing_auction(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        if request.user != listing.owner:
            messages.error(request, "The auction can only be closed by the owner.")
            return redirect("listing", listing_id=listing_id)

        highest_bid = listing.bids.order_by('-amount').first()
        if highest_bid:
            listing.winner = highest_bid.bidder_user
        listing.active = False
        listing.save()
        messages.success(request, "The auction has been closed successfully.")
        return redirect("listing", listing_id=listing_id)
    return redirect("listing", listing_id=listing_id)
        


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

