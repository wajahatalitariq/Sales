# Street Food Sales Tracker

A web application for tracking sales of street food items with an initial investment of 21,000 Pakistani Rupees. Built with Python Flask for the backend, SQLite for the database, and React for the frontend.

## Features

- User authentication with authorized user IDs (01-135231-091, 01-135231-041)
- Categorized menu with items from the street food menu (Golgappay, Chat, Corn, etc.)
- Record sales for different items with quantity tracking
- Options customization for Chat in a Bag
- Calculate total sales and remaining investment
- Display progress toward recouping initial investment
- View sales history by item

## Menu Items

The application includes the following menu items:
- **Golgappay**: 8 in plate (Rs200), 12 in plate (Rs250)
- **Mint Margarita**: Rs130
- **Chat in Bag**: Rs250 with customizable options
- **Boiled Flavoured Corns**: Classic Butter (Rs100), Masaa Masti (Rs150), Super Corn Chaat (Rs200)
- **Extra Toppings**: Garlic Powder (Rs10), Cheese Powder (Rs30)

## Setup Instructions

### Requirements

- Python 3.7+
- Flask
- SQLite

### Installation

1. Clone the repository:
```
git clone <repository-url>
cd street-food-sales-tracker
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python app.py
```

4. Access the application at:
```
http://localhost:5000
```

### Authorized Users

The following user IDs are authorized to access the system:
- 01-135231-091
- 01-135231-041

### Application Structure

- `app.py`: Main application file
- `app/static/css/style.css`: CSS styles
- `app/static/js/app.js`: React application code
- `app/templates/`: HTML templates
- `app/database/sales.db`: SQLite database

## Usage

1. Login with an authorized user ID.
2. Browse menu items by category (All, Golgappay, Drinks, Chat, Corn).
3. Add items to your sales by adjusting quantities.
4. For "Chat in Bag", select the desired options when adding to your order.
5. Submit your sales to record them in the database.
6. View sales history and summary statistics.
7. Logout when finished.

## Notes

- The application automatically calculates the total amount based on quantity and item price.
- The progress bar shows how much of the initial investment has been recouped through sales.
- The summary view shows sales broken down by item.
- All prices are in Pakistani Rupees (Rs). 