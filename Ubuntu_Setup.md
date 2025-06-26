````markdown
# CarWatch Backend API - Deployment Guide

This guide provides step-by-step instructions for deploying the CarWatch Backend API on an Ubuntu server. The setup uses Nginx as a reverse proxy, Gunicorn as the application server, and `systemd` to manage the service. It also includes securing the domain with SSL using Cloudflare and Certbot.

## Prerequisites

1.  An Ubuntu Server (22.04 LTS or newer, 24.04 LTS Recommended).
2.  A domain name pointed to your server's IP address.
3.  Your domain is added to a Cloudflare account with the **DNS record set to "Proxied"** (orange cloud).

---

## Part 1: Initial Server Setup

First, connect to your server via SSH and ensure the system is up-to-date.

# Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install Git
sudo apt install git -y
````

-----

## Part 2: Clone the Repository

Clone the project source code from GitHub into the `ubuntu` user's home directory.

```bash
# Navigate to the ubuntu user's home directory
cd /home/ubuntu

# Clone the repository
git clone [https://github.com/dumartist/carwatch-backend.git](https://github.com/dumartist/carwatch-backend.git)

# Navigate into the project directory
cd carwatch-backend
```

-----

## Part 3: Install System Dependencies

Install Nginx, Python, Pip, and other necessary libraries required by the application's dependencies (like PyTorch and OpenCV).

```bash
# Install Nginx
sudo apt install nginx -y

# Install Python, Pip, and the venv module
sudo apt install python3 python3-pip python3.12-venv -y

# Install libraries required by OpenCV and other ML packages
sudo apt install libgl1-mesa-glx libglib2.0-0 libgomp1 -y
```

-----

## Part 4: Setup Python Environment

We will create a Python virtual environment to isolate the project's dependencies.

```bash
# Make sure you are in the project directory
# /home/ubuntu/carwatch-backend

# Create a virtual environment named "venv"
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install all required Python packages from the requirements file
# This command must be run WITHOUT sudo
pip install -r requirements.txt
```

*After this step, you can run `deactivate` to exit the virtual environment. We will not need it active for the rest of the server setup.*

-----

## Part 5: Set File & Folder Permissions

Set the correct ownership for the project directory to avoid permission errors.

```bash
# Give the ubuntu user ownership of the entire project directory
sudo chown -R ubuntu:ubuntu /home/ubuntu/carwatch-backend
```

-----

## Part 6: Configure Gunicorn and `systemd` Service

We will create a `systemd` service file to manage the Gunicorn application server, allowing it to run as a background service and restart automatically.

#### 1\. Create the `systemd` Service File

Use a text editor like `nano` to create the service file.

```bash
sudo nano /etc/systemd/system/carwatch.service
```

Paste the following content into the file. This configuration is optimized for this project.

```ini
[Unit]
Description=CarWatch Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/carwatch-backend
RuntimeDirectory=gunicorn

# Add the venv to the system PATH
Environment="PATH=/home/ubuntu/carwatch-backend/venv/bin:$PATH"

# Gunicorn execution command using a UNIX socket
ExecStart=/home/ubuntu/carwatch-backend/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app

Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=carwatch

[Install]
WantedBy=multi-user.target
```

Save the file and exit the editor (`Ctrl+X`, `Y`, `Enter`).

#### 2\. Start and Enable the Service

Now, reload `systemd`, start the `carwatch` service, and enable it to start on boot.

```bash
# Reload the systemd daemon to recognize the new file
sudo systemctl daemon-reload

# Start the carwatch service
sudo systemctl start carwatch.service

# Enable the service to start automatically on server boot
sudo systemctl enable carwatch.service
```

-----

## Part 7: Configure Nginx as a Reverse Proxy

Nginx will sit in front of Gunicorn and handle incoming web requests, passing them to the application via the socket we configured.

#### 1\. Create the Nginx Configuration File

```bash
sudo nano /etc/nginx/sites-available/carwatch
```

Paste the following configuration into the file. This initially sets up the server to listen on port 80 (HTTP). **Replace `flask.dumartist.my.id` with your actual domain name.**

```nginx
server {
    listen 80;
    server_name flask.dumartist.my.id;

    location / {
        proxy_pass http://unix:/run/gunicorn/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2\. Enable the Nginx Configuration

Activate the new configuration by creating a symbolic link and removing the default site.

```bash
# Create the link
sudo ln -s /etc/nginx/sites-available/carwatch /etc/nginx/sites-enabled/

# Remove the default configuration
sudo rm /etc/nginx/sites-enabled/default
```

#### 3\. Test and Restart Nginx

```bash
# Test for syntax errors
sudo nginx -t

# If the test is successful, restart Nginx
sudo systemctl restart nginx
```

At this point, your site should be accessible via HTTP.

-----

## Part 8: Enable HTTPS with Cloudflare and Certbot

This final part secures your site with an SSL certificate.

#### 1\. Configure Cloudflare

In your Cloudflare Dashboard for your domain:

1.  Go to **SSL/TLS** -\> **Overview**.
2.  Set the encryption mode to **Full (Strict)**.
3.  Go to **SSL/TLS** -\> **Edge Certificates**.
4.  Turn on **"Always Use HTTPS"**.

#### 2\. Install and Run Certbot

On your server, Certbot will get a certificate and automatically update your Nginx configuration for HTTPS.

```bash
# Install Certbot and its Nginx plugin
sudo apt install certbot python3-certbot-nginx -y

# Run Certbot and follow the on-screen instructions
# Replace with your domain name
sudo certbot --nginx -d flask.dumartist.my.id
```

When prompted, choose the option to **redirect** HTTP traffic to HTTPS. Certbot will handle the rest.

-----

## Post-Installation

Your application is now fully deployed and running securely.

  * **To check the status of your application:**
    ```bash
    systemctl status carwatch.service
    ```
  * **To see your application's logs:**
    ```bash
    journalctl -u carwatch.service -f
    ```
  * **To check the status of Nginx:**
    ```bash
    systemctl status nginx
    ```

Congratulations\!

```
```