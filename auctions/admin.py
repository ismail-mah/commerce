from django.contrib import admin
from .models import User, Listing, Category, Bid, Comment

admin.site.register(User)

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "price",
        "active",
        "owner",
        "winner",
        "created_at",
    )
    list_filter = ("active", "category", "owner", "winner")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", )


    actions = ("reopen_auction",)

    @admin.action(description="Reopen selected auctions")
    def reopen_auction(self, request, queryset):
      
        for listing in queryset:
            listing.bids.all().delete()    
            listing.winner = None           
            listing.active = True           
            listing.save()

        self.message_user(request, "Selected listings have been reopened.")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name",)
    search_fields = ("name",)
    ordering = ("id",)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "bidder_user", "amount", "created_at")
    list_filter = ("listing", "bidder_user")
    search_fields = ("listing__title", "bidder_user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("listing", "commenter_user", "created_at")
    list_filter = ("listing", "commenter_user")
    search_fields = ("comment_text", "listing__title", "commenter_user_username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)