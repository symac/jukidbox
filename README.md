# jukidbox
Jukebox for kid based on Raspberry Pi.

# Hardware

- écran de radar de recul de voiture : [Rear view 4,3"](https://www.ebay.fr/sch/i.html?_from=R40&_sacat=0&_nkw=rear+view+4%2C3&LH_PrefLoc=2&_sop=15) 
![display](/home/nous/dev/jukidbox/img/screen.jpg) 
- boutons d'arcade : [arcade button](https://www.ebay.fr/sch/i.html?_from=R40&_sacat=0&_nkw=arcade+button&LH_PrefLoc=2&_sop=15) 
![](/home/nous/dev/jukidbox/img/arcade_button.jpg) 
- un slider pour la gestion du volume : [sliding potentiometer 10k](https://www.ebay.fr/sch/i.html?_odkw=arcade+button&LH_PrefLoc=2&_sop=15&_osacat=0&_from=R40&_trksid=p2045573.m570.l1313.TR3.TRC2.A0.H0.Xpotentiometer+10k+sliding.TRS0&_nkw=potentiometer+10k+sliding&_sacat=0) 
 ![](/home/nous/dev/jukidbox/img/sliding.jpg) 
 - un convertisseur pour récupérer une valeur numérique à partir du potentiomètre : [MCP 3008](https://www.ebay.fr/itm/MCP3008-I-P-Convertisseur-analogique-vers-num%C3%A9rique-Octal-16DIP/152465009958?ssPageName=STRK%3AMEBIDX%3AIT&_trksid=p2057872.m2749.l2649)
 ![](/home/nous/dev/jukidbox/img/mcp3008.jpg) 
 - une carte son audio. On en trouve tout un tas sous la dénomation 3D sound qui permettent d'avoir un son correct. On peut aussi utiliser la sortie jack du RPi en direct, mais la qualité reste limitée sur les premières générations de Rpi.
 ![](/home/nous/dev/jukidbox/img/usb_audio.jpeg)
 - un amplificateur audio en mono ([de ce type](https://www.adafruit.com/product/2130)) qui permet de prendre le son de la carte USB pour l'envoyer sur les enceintes en l'amplifiant
  ![](/home/nous/dev/jukidbox/img/pam8302.jpg) 
 - une alimentation pour alimenter le tout. Possibilité que l'écran soit en 5V selon les configurations, mais pas toujours le cas. Dans le doute, utilisation d'une alimentation mixte 12V (écran) / 5V (Raspberry). Dans mon cas [une meanwell](https://fr.rs-online.com/web/p/alimentations-a-decoupage/6447073/). Un peut chère mais semble secure. Parmi les autres options celle de reprendre une alimentation de disque dur externe qui, il y a quelques années, demandait du 12/5v ([notes sur le blog](http://www.geobib.fr/blog/2016-09-25-alimentation)).
 ![](/home/nous/dev/jukidbox/img/alim.jpeg).
 - Petites choses variées : 
 	- un cable d'alimentation générale;
 	- un interrupteur pour la mise en route générale;
 	- des cables pour connexion des différentes pins & cartes;
 	- une breadboard pour fixer le MCP3008 & l'ampli audio;
 	- des haut-parleurs, à récupérer facilement depuis une vieille enceinte;
 	- une clé USB pour stocker la musique;
 	
# Software
## Préparation du système
```
sudo apt-get install mpg321
```

## Connexion automatique
Pour que le RPi démarre sans avoir besoin de saisir le login et le mot de passe, on va configurer raspi-config au niveau du menu suivant :
```
3 > B1 > B2 (Console autologin)
```

## Sortie sur carte USB
Pour sortie sur la carte audio USB plutôt que le son interne, on va créer une fichier /etc/modprobe.d/alsa-base.conf qui va contenir : 

```
# This sets the index value of the cards but doesn't reorder.
options snd_usb_audio index=0
options snd_bcm2835 index=1

# Does the reordering.
options snd slots=snd_usb_audio,snd_bcm2835
```

##.bashrc
Pour configurer le démarrage automatique, on va ajouter en fin du fichier .bashrc (de tête, à vérifier) :

```
# Run only when starting, don't replicate when connecting over SSH
if [ ! "$SSH_TTY" ]
then
	sudo mount -t vfat -ouser,umask=0000 /dev/sda1 /media/usb/
	cd jukidbox
	nohup python soundControl.py > /dev/null 2>/dev/null &
	python jukidbox.py
fi
```

## Orientation de l'écran
L'orientation de l'écran du RPi se gère dans le fichier ```/boot/config.txt```, ajouter à la fin :
```
display_rotate=1
```

L'orientation de l'écran est gérée aussi au niveau du fichier ```screencontrol.py``` via une variable ```orientation``` à faire varier entre 0 & 1 selon l'orientation souhaitée.

## Système en lecture seule
en raison de la manière de gérer l'extinction un peu brutale du RPi via l'interruption de l'alimentation, il est préférable de passer le système en lecture seule; Pour cela, on se base sur les instructions https://hallard.me/raspberry-pi-read-only/ ([copie Internet Archive](https://web.archive.org/web/20191008200136/https://hallard.me/raspberry-pi-read-only/)) : 

```
Sudo apt-get remove --purge wolfram-engine triggerhappy anacron logrotate dphys-swapfile xserver-common lightdm
sudo apt-get install busybox-syslogd; sudo dpkg --purge rsyslog
```

ajout de "fastboot noswap ro" à la fin de la ligne de ```/boot/cmdline.txt```

Déplacement de fichiers divers : 
```
sudo rm -rf /var/lib/dhcp/ /var/lib/dhcpcd5 /var/run /var/spool /var/lock /etc/resolv.conf
sudo ln -s /tmp /var/lib/dhcp
sudo ln -s /tmp /var/lib/dhcpcd5
sudo ln -s /tmp /var/run
sudo ln -s /tmp /var/spool
sudo ln -s /tmp /var/lock
touch /tmp/dhcpcd.resolv.conf
sudo ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf
```

édition de /etc/systemd/system/dhcpcd5.servicer pour remplacer le PIDFILE de /run/dhcpcd.id vers /var/run/dhcpcd.id

```
sudo rm /var/lib/systemd/random-seed
sudo ln -s /tmp/random-seed /var/lib/systemd/random-seed
```

/lib/systemd/system/systemd-random-seed.service

Ajouter la ligne  ```ExecStartPre=/bin/echo "" >/tmp/random-seed``` sous la section  service qui devrait maintenant ressembler à : 

```
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/bin/echo "" >/tmp/random-seed
ExecStart=/lib/systemd/systemd-random-seed load
ExecStop=/lib/systemd/systemd-random-seed save
```

Gérer /etc/fstab pour que le système démarre en lecture seule.