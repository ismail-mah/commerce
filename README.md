# Commerce – Auction Site

An eBay-style auction web app built with Django and Bootstrap. This is the CS50W Project 2.

## Features

- Register, log in, and log out
- Create listings with a title, description, starting price, image URL, and category
- Browse active and closed listings, or filter by category
- Place bids and comment on listings
- Add listings to a personal watchlist
- Owners can close an auction, and the highest bidder wins
- Django admin for managing users, listings, bids, comments, and categories

## Getting Started

```bash
git clone https://github.com/ismail-mah/commerce
cd commerce

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Admin

Log in at http://127.0.0.1:8000/admin/ with the superuser account you created above.
