#!/bin/bash
source ../../.env

HOST=$SSH_ADDR
PASSWORD=$SSH_PASSWORD
LOCAL_PORT="3306"

nc -z -w5 $HOST
if [ $? -eq 0 ]; then
  echo "SSH connection to $HOST is up!"
else
  echo "SSH connection to $HOST is down. Opening SSH tunnel..."
  ssh -L $LOCAL_PORT:localhost:$LOCAL_PORT $HOST
  expect "password:"
  send "$PASSWORD\r"
fi