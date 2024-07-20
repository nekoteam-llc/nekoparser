#!/bin/bash
# wget -qO- https://get-nekoparser.dan.tatar | sudo bash -

if [ "$EUID" -ne 0 ]; then
    echo -e "\e[1;91mPlease run as root\e[0m"
    exit 1
fi

if [ "$PWD" != "/opt" ]; then
    echo -e "\e[1;92mYou are not in /opt. Do you want to switch to /opt? (Y/n)\e[0m"
    read switch </dev/tty
    if [ "$switch" == "Y" ] || [ "$switch" == "y" ]; then
        cd /opt
    fi
fi

if [ -d "nekoparser" ]; then
    echo -e "\e[1;91mNekoparser directory already exists\e[0m"
    exit 1
fi

if ! [ -x "$(command -v git)" ]; then
    echo -e "\e[1;91mGit is not installed. Installing Git...\e[0m"
    apt update
    apt install -y git
    echo -e "\e[1;92mGit installed successfully\e[0m"
else
    echo -e "\e[1;92mGit is already installed\e[0m"
fi

echo -e "\e[1;92mEnter the GitHub token provided by developer\e[0m"
read token </dev/tty
if [ -z "$token" ]; then
    echo -e "\e[1;91mGitHub token cannot be empty\e[0m"
    exit 1
fi

echo -e "\e[1;92mCloning repository...\e[0m"
git clone https://hikariatama:$token@github.com/nekoteam-llc/nekoparser.git

cd nekoparser

if [ -z "$1" ]; then
    echo -e "\e[1;92mEnter the domain name for the site (e.g. dan.tatar)\e[0m"
    read domain </dev/tty
    if [ -z "$domain" ]; then
        echo -e "\e[1;91mDomain name cannot be empty\e[0m"
        exit 1
    fi
else
    domain=$1
fi

if ! [ -x "$(command -v docker)" ]; then
    echo -e "\e[1;91mDocker is not installed. Installing Docker...\e[0m"
    wget -qO- https://get.docker.com | bash -
    echo -e "\e[1;92mDocker installed successfully\e[0m"
else
    echo -e "\e[1;92mDocker is already installed\e[0m"
fi

if [ -f default.conf ]; then
    rm -f default.conf
fi

echo -e "\e[1;92mGenerating Nginx configuration...\e[0m"
cp default.conf.sample default.conf
sed -i "s/DOMAIN/$domain/g" default.conf

echo -e "\e[1;92mReplacing domain name in source files...\e[0m"
find apps -type f -exec sed -i "s/dan.tatar/$domain/g" {} \;

if [ -f .env ] && [ -s .env ]; then
    echo -e "\e[1;91m.env exists and is non-empty\e[0m"
    exit 1
fi

POSTGRES_PASSWORD=$(openssl rand -hex 22 | tr -d '\n')
MINIO_ROOT_PASSWORD=$(openssl rand -hex 22 | tr -d '\n')

touch .env
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >>.env
echo "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" >>.env

echo -e "\e[1;92m.env generated successfully\e[0m"

echo -e "\e[1;92mEnter the port for Nginx (empty for 80)\e[0m"
read port </dev/tty
if [ -z "$port" ]; then
    port=80
fi

if [ "$port" -ne 80 ]; then
    echo "NGINX_PORT=$port" >>.env
fi

echo -e "\e[1;92mBuilding Docker images...\e[0m"
docker compose build

echo -e "\e[1;92mStarting Docker containers...\e[0m"
docker compose up -d

echo -e "\e[1;92mNekoparser installed successfully\e[0m"
echo -e "\e[1;92mYou can access the site at https://nekoparser.$domain\e[0m"
echo -e "\e[1;92mDon't forget to configure Cloudflare DNS with SSL mode set to 'Flexible' and ZeroTrust\e[0m"
echo -e "\e[1;92mDomains to include in ZeroTrust scope: nekoparser.$domain, nekoparser-s3.$domain, nekoparser-prefect.$domain\e[0m"
echo -e "\e[1;92mCloudflare DNS Dashboard: https://dash.cloudflare.com/\e[0m"
echo -e "\e[1;92mCloudflare Zero Trust Dashboard: https://one.dash.cloudflare.com/\e[0m"
