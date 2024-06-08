#!/bin/bash

if [ -f .env ] && [ -s .env ] && [ "$1" != "--override" ]; then
    echo -e "\e[1;91m.env exists and is non-empty, use --override to overwrite\e[0m"
    exit 1
fi

POSTGRES_PASSWORD=$(openssl rand -hex 22 | tr -d '\n')
MINIO_ROOT_PASSWORD=$(openssl rand -hex 22 | tr -d '\n')

echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >.env
echo "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" >>.env

echo -e "\e[1;92m.env generated successfully\e[0m"
