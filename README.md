# reDuh
reDuh Mejorado 2020

Mejoras Realizadas Por Gabriel Weise

Paso 1 =  Descargue el reDuh.php y reDuh.py y ubiquelos en la carpeta /var/www/html de su Kali Linux 2020

Paso 2 =  Establezca todos los permisos a la carpeta html con el comando: chmod 777 /var/www/html

Paso 3 =  Cree un archivo llamado reDuh.log con el siguiente comando:  touch /var/www/html/reDuh.log

Paso 4 =  Establezca permisos el archivo reDuh.log con el comando:  chmod 444 /var/www/html/reDuh.log

Paso 5 =  Instale el paquete php-curl, con el comando:  apt-get install php-curl

Paso 6 = Inicie el Servicio de Apache, con el comando: service apache2 start

Paso 7 = Descargue el archivo reDuhClient.jar en la maquina Windows/Linux desde donde desea hacer el Puente, se ejecutar con el comnado:
         java -jar reDuhClient.jar http://IP_Kali/reDuh.php
         
         
