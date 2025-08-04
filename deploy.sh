#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python, pip, Git and other dependencies
echo "Installing Python, pip, Git and other dependencies..."
sudo apt install -y python3 python3-pip python3-dev git nginx python3-venv

# Clone the GitHub repository
echo "Cloning the repository..."
cd ~
git clone https://github.com/wajahatalitariq/Sale.git
cd Sale

# Set up a virtual environment and install dependencies
echo "Setting up virtual environment and installing dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure application for production
echo "Configuring the application for production..."
sudo mkdir -p /var/www/Sale
sudo cp -r ~/Sale/* /var/www/Sale/
sudo chown -R ubuntu:ubuntu /var/www/Sale/

# Create a virtual environment in the production directory
cd /var/www/Sale
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create systemd service file for Gunicorn
echo "Setting up Gunicorn service..."
sudo bash -c 'cat > /etc/systemd/system/sale.service << EOL
[Unit]
Description=Gunicorn instance to serve Sale application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/Sale
Environment="PATH=/var/www/Sale/venv/bin"
ExecStart=/var/www/Sale/venv/bin/gunicorn --workers 3 --bind unix:/var/www/Sale/sale.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOL'

# Configure Nginx
echo "Configuring Nginx..."
sudo bash -c 'cat > /etc/nginx/sites-available/sale << EOL
server {
    listen 80;
    server_name 13.239.85.169;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/Sale/sale.sock;
    }
}
EOL'

# Create symbolic link and test Nginx configuration
sudo ln -s /etc/nginx/sites-available/sale /etc/nginx/sites-enabled
sudo nginx -t

# Remove default Nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Restart Nginx
sudo systemctl restart nginx

# Start and enable the Gunicorn service
echo "Starting Gunicorn service..."
sudo systemctl start sale
sudo systemctl enable sale

# Ensure data directory exists
echo "Ensuring data directory exists..."
mkdir -p /var/www/Sale/data
touch /var/www/Sale/data/.keep

echo "Deployment completed! Your application should be running at http://13.239.85.169" 