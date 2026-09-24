# Commerce – Auction Site

An eBay-style auction web app built with Django. Users can create listings, place bids, comment, and manage a personal watchlist. This is the CS50W "Commerce" project.

## Features

- **User accounts** – register, log in, and log out
- **Create listings** – title, description, starting price, optional image URL, and optional category
- **Active & closed listings** – browse open auctions or view closed ones
- **Listing page** – view details, current price, bids, and comments
- **Bidding** – place bids that must be valid against the current price
- **Auction closing** – owners can close an auction; the highest bidder becomes the winner
- **Watchlist** – add or remove listings to follow them
- **Comments** – logged-in users can comment on any listing
- **Categories** – browse listings by category and create new categories
- **Django admin** – manage users, listings, bids, comments, and categories

## Tech Stack

- Python 3
- Django 6.0
- SQLite
- Bootstrap 5 and Bootstrap Icons (front end)
- djLint (template linting/formatting)

## Project Structure

```
commerce/
├── auctions/            # Main app (models, views, forms, templates, static)
│   ├── models.py        # User, Category, Listing, Bid, Comment
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── templates/auctions/
│   └── static/auctions/
├── commerce/            # Project settings and root URL config
├── static/              # Shared static files (e.g. images)
├── manage.py
└── requirements.txt
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ismail-mah/commerce
cd commerce
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin account)

A superuser can log in to the Django admin site to manage users, listings, bids, comments, and categories.

```bash
python manage.py createsuperuser
```

You'll be prompted for:

- **Username** – e.g. `admin`
- **Email address** – optional, press Enter to skip
- **Password** – typed characters are hidden; you'll be asked to confirm it


### 6. Run the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Admin Management

1. Make sure the server is running (`python manage.py runserver`).
2. Go to http://127.0.0.1:8000/admin/
3. Log in with the superuser username and password you created in step 5.

From the admin panel you can add, edit, or delete users, categories, listings, bids, and comments.

To reset a forgotten admin password:

```bash
python manage.py changepassword <username>
```

## URL Overview

| Path                                  | Description                     |
|---------------------------------------|---------------------------------|
| `/`                                   | Active listings                 |
| `/closed_listings/`                   | Closed listings                 |
| `/listing/<id>/`                      | Listing detail page             |
| `/create_listing/`                    | Create a new listing            |
| `/bid/<id>/`                          | Place a bid                     |
| `/comment/<id>/`                      | Add a comment                   |
| `/close_listing_auction/<id>/`        | Close an auction (owner only)   |
| `/watchlist/`                         | View your watchlist             |
| `/watchlist/add/<id>/`                | Add listing to watchlist        |
| `/watchlist/remove/<id>/`             | Remove listing from watchlist   |
| `/categories/`                        | List categories                 |
| `/categories/<id>/`                   | Listings in a category          |
| `/create_category/`                   | Create a category               |
| `/login/`, `/logout/`, `/register/`   | Authentication                  |

## Data Models

- **User** – extends Django's `AbstractUser`
- **Category** – name (unique)
- **Listing** – title, description, price, image URL, category, active flag, owner, winner, watchers
- **Bid** – listing, bidder, amount, timestamp
- **Comment** – listing, commenter, text, timestamp

## Development Notes

- Template linting/formatting uses [djLint](https://djlint.com/). If you use VSCode, select the project's `venv` as your Python interpreter so the djLint extension can find it.
- `django-browser-reload` is included for auto-refresh during development.

