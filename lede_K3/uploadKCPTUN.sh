#!/bin/bash

cd /tmp/upload && chmod a+x client_linux_arm5 

mkdir /usr/share/kcptun
mv /tmp/upload/client_linux_arm5 /usr/share/kcptun/
mv /tmp/upload/client*.json /usr/share/kcptun/
cd /usr/share/kcptun/ && mv client_linux_arm5 kcptun_client

mv /tmp/upload/client_linux_arm5 /var/kcptun_client


opkg install /tmp/upload/luci-app-kcptun_*.ipk

/etc/adhosts
usr/share/kcptun/kcptun_client

/etc/adhosts
/var/kcptun_client


/etc/adhosts
/usr/share/kcptun/
