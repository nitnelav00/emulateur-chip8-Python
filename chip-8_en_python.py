###########
# Crée par Valentin en 2024
#
# Juste un émulateur de CHIP-8 crée en Python pour le fun
# S'il n'est pas parfait c'est totalement normal, je ne suis qu'un débutant, mais je m'améliore avec le temps !
###########

# pour l'aléatoire
from random import randint
# pour gérer le rafraichissement de l'écran
from time import time

# pygame est importé plus bas

# la RAM de l'émulateur
memoire = [0x00 for _ in range(0x1000)]
# le conteur du programme
pc = 0x200
# le registre i (renommé iu pour éviter les confusions)
iu = 0x00
# le stack
stack = []
# le premier timer
delay_timer = 0x00
# le second timer
sound_timer = 0x00
# 16 registres (de 0 à F) (le registre F pour Flags)
registres = [0x00 for _ in range(0x10)]
# pour si l'émulateur attend un appuie de touche
pause = False
key_reg = 0x0
# nombre d'instructions par images
vitesse = 10
# affichage en 64x32 pixels
affichage = [[False for _ in range(32)] for _ in range(64)]
# la touche actuellement appuyée
touche = -1

# pour gérer le rafraichissement de l'écran
prevtime = time()

# les numéros de base
numeros = [
0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
0x20, 0x60, 0x20, 0x20, 0x70, # 1
0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
0x90, 0x90, 0xF0, 0x10, 0x10, # 4
0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
0xF0, 0x10, 0x20, 0x40, 0x40, # 7
0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
0xF0, 0x90, 0xF0, 0x90, 0x90, # A
0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
0xF0, 0x80, 0x80, 0x80, 0xF0, # C
0xE0, 0x90, 0x90, 0x90, 0xE0, # D
0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
0xF0, 0x80, 0xF0, 0x80, 0x80, # F
]

# on met les numéros dans la RAM
for i in range(len(numeros)):
	memoire[i] = numeros[i]

# on ouvre le fichier rom.bin
try:
	rom = open("rom.bin", "rb").read()
except:
	print("\nAucune rom sous le nom de 'rom.bin' n'a été trouvé")
	import os
	os.system("pause")
	os._exit(-1)

# on charge le fichier dans la RAM
for i in range(len(rom)):
	memoire[i + 0x200] = rom[i]

# importer et initialiser pygame
import pygame
pygame.init()

# pour la taille de l'écran
taille_x = 64*10
taille_y = 32*10
# création de la fenètre
window = pygame.display.set_mode((taille_x,taille_y))
# changer le titre
pygame.display.set_caption('CHIP-8')

# affichage des instruction d'utilisation
font = pygame.font.SysFont(None, 28)
img = font.render('les touches sont : 1, 2, 3, 4,', True, (255, 255, 255))
window.blit(img, (20, 20))
img = font.render('a, z, e, r,', True, (255, 255, 255))
window.blit(img, (192, 36))
img = font.render('q, s, d, f,', True, (255, 255, 255))
window.blit(img, (192, 52))
img = font.render('w, x, c, v', True, (255, 255, 255))
window.blit(img, (192, 70))
img = font.render("! appuyer sur deux touches à la fois n'est pas possible !", True, (255, 255, 255))
window.blit(img, (20, 100))

# attendre 3 secondes
while (time() - prevtime) <= 3.:
	pygame.display.update()
prevtime = time()

# fonction pour afficher les pixels sur l'écran
def afficher(window, affichage):
	window.fill((0,0,0))
	for x in range(64):
		for y in range(32):
			if affichage[x][y] == True:
				pygame.draw.rect(window, (255, 255, 255), (x*10, y*10, 10, 10))
	pygame.display.update()

# fonction pour convertire les touches du clavier en nombre entre 0x0 et 0xF, renvoie -1 si elle ne fait pas partie des touches utiles pour l'émulateur
def convertir_touche(event):
	if event.key == pygame.K_1:
		return 0x1
	elif event.key == pygame.K_2:
		return 0x2
	elif event.key == pygame.K_3:
		return 0x3
	elif event.key == pygame.K_4:
		return 0xC
	elif event.key == pygame.K_a:
		return 0x4
	elif event.key == pygame.K_z:
		return 0x5
	elif event.key == pygame.K_e:
		return 0x6
	elif event.key == pygame.K_r:
		return 0xD
	elif event.key == pygame.K_q:
		return 0x7
	elif event.key == pygame.K_s:
		return 0x8
	elif event.key == pygame.K_d:
		return 0x9
	elif event.key == pygame.K_f:
		return 0xE
	elif event.key == pygame.K_w:
		return 0xA
	elif event.key == pygame.K_x:
		return 0x0
	elif event.key == pygame.K_c:
		return 0xB
	elif event.key == pygame.K_v:
		return 0xF
	else:
		return -1

# boncle principale
running = True
while running:

	# attente pour avoir 60 images par seconde
	while (time() - prevtime) <= 1./60.:
		pygame.display.update()
	prevtime = time()

	# récupérer les appuis de touches
	for event in pygame.event.get():
	    if event.type == pygame.QUIT:
	    	# quitter l'émulateur
	        running = False
	        break
	    elif event.type == pygame.KEYDOWN:
	    	# appuyer sur une touche
	    	touche = convertir_touche(event)
	    elif event.type == pygame.KEYUP:
	    	# relacher les touches
	    	touche = -1

	# boucle des instruction de l'émulateur : 10 instructions par image
	for ytr in range(vitesse):
		# arréter la boucle si l'émulateur attend une touche
		if pause == True:
			break
		# convertir deux octets en un mot
		opcode = memoire[pc] << 8 | memoire[pc+1]
		# incrémenter le compteur du programme
		pc += 2
		# le limiter à la taille de la mémoire
		pc = pc % 0x1000
		o = opcode & 0x000F
		# les deux derniers chiffres (16 bits)
		kk = opcode & 0x00FF
		# les trois derniers chiffres (24 bits)
		nnn = opcode & 0x0FFF
		# le séparer par demis octets
		opcode = ((opcode & 0xF000) >> 12, (opcode & 0x0F00) >> 8, (opcode & 0x00F0) >> 4, opcode & 0x000F)
		# x pour le premier registre et y pour le teuxième registre
		x = opcode[1]
		y = opcode[2]

		if opcode[0] == 0x0 and opcode[1] == 0x0 :
			# intruction pour remètre l'affichage à zéro
			if opcode[2] == 0xE and opcode[3] == 0x0:
				affichage = [[False for _ in range(32)] for _ in range(64)]
			# intruction pour retourner d'une fonction (à la dernière adresse du stack)
			elif opcode[2] == 0xE and opcode[3] == 0xE:
				pc = stack.pop()
		# intruction pour sauter à l'adresse nnn
		elif opcode[0] == 0x1:
			pc = nnn
		# intruction pour appeler une fonction (et stocker l'adresse dans le stack)
		elif opcode[0] == 0x2:
			stack.append(pc)
			pc = nnn
		# intruction pour sauter l'instruction suivante si le registre x est égale à kk
		elif opcode[0] == 0x3:
			if registres[x] == kk:
				pc += 2
		# intruction pour sauter l'instruction suivante si le registre x n'est pas égale à kk
		elif opcode[0] == 0x4:
			if registres[x] != kk:
				pc += 2
		# intruction pour sauter l'instruction suivante si le registre x est égale au registre y
		elif opcode[0] == 0x5:
			if registres[x] == registres[y]:
				pc += 2
		# intruction pour stocker la valeur kk danse le registre x
		elif opcode[0] == 0x6:
			registres[x] = kk
		# intruction pour additionner kk au registre x (et le stocker au même endroit)
		elif opcode[0] == 0x7:
			registres[x] = (registres[x] + kk) % 0x100

		elif opcode[0] == 0x8:
			# intruction pour stocker la valeur du registre y dans le registre x
			if opcode[3] == 0x0:
				registres[x] = registres[y]
			# intruction pour faire une opération ou binaire entre le registre x et le registre y et le stocker dans le registre x
			elif opcode[3] == 0x1:
				registres[x] = registres[y] | registres [x]
			# intruction pour faire une opération et binaire entre le registre x et le registre y et le stocker dans le registre x
			elif opcode[3] == 0x2:
				registres[x] = registres[y] & registres [x]
			# intruction pour faire une opération ou exclusif binaire entre le registre x et le registre y et le stocker dans le registre x
			elif opcode[3] == 0x3:
				registres[x] = registres[y] ^ registres [x]
			# intruction pour additionner les valeurs des registres x avec y et les stocker dans le registre x et mettre le registre F à 1 si débordement
			elif opcode[3] == 0x4:
				somme = registres[x] + registres[y]
				registres[x] = somme % 0x100
				registres[0xF] = 0
				if somme > 0xFF:
					registres[0xF] = 1
			# intruction pour soustraire les valeurs des registres x avec y et les stocker dans le registre x et mettre le registre F à 1 si débordement
			elif opcode[3] == 0x5:
				sous = registres[x] > registres[y]
				registres[x] = (registres[x] - registres[y]) % 0x100
				registres[0xF] = 0
				if sous == True:
					registres[0xF] = 1
			# intruction pour stocker la valeur du registre y dans le registre x et décaler les bits de 1 vers la droite et mettre le registre F à 1 si débordement
			elif opcode[3] == 0x6:
				registres[x] = registres[y]
				tmp = registres[x] & 0x1
				registres[x] >>= 1
				registres[0xF] = tmp
			# intruction pour soustraire les valeurs des registres y avec x et les stocker dans le registre x et mettre le registre F à 1 si débordement
			elif opcode[3] == 0x7:
				sous = registres[y] > registres[x]
				registres[x] = (registres[y] - registres[x]) % 0x100
				registres[0xF] = 0
				if sous == True:
					registres[0xF] = 1
			# intruction pour stocker la valeur du registre y dans le registre x et décaler les bits de 1 vers la gauche et mettre le registre F à 1 si débordement
			elif opcode[3] == 0xE:
				registres[x] = registres[y]
				tmp = registres[x] >> 7
				registres[x] = (registres[x] << 1) % 0x100
				registres[0xf] = tmp
		# intruction pour sauter l'instruction suivante si le registre x n'est pas égale au registre y
		elif opcode[0] == 0x9:
			if registres[x] != registres[y]:
				pc += 2
		# intruction pour mettre la valeur de i à nnn
		elif opcode[0] == 0xA:
			iu = nnn
		# intruction pour mettre le compteur du programme à la valeur du premier registre + nnn
		elif opcode[0] == 0xB:
			pc = (registres[0] + nnn) % 0x1000
		# intruction pour stocker dans le registre x une valeur aléatoire avec les bits correspondant à kk
		elif opcode[0] == 0xC:
			registres[x] = randint(0x0, 0x100) & kk
		# intruction pour changer la couleur des pixel d'un sprite de hauteur o et de largeur 8 à l'emplacement de mémoire i et à la position des valeurs des registres x et y
		# change la valeur du registre F si des pixels sont passés de 1 à 0
		elif opcode[0] == 0xD:
			largeur = 8
			hauteur = o
			registres[0xF] = 0x0
			for ligne in range(hauteur):
				sprite = memoire[iu + ligne]
				for colone in range(largeur):
					if (sprite & 0x80) > 0:
						xpos = registres[x] + colone
						ypos = registres[y] + ligne
						ax = xpos % 64
						ay = ypos % 32
						pixel_res = affichage[ax][ay]
						if affichage[ax][ay] == True:
							affichage[ax][ay] = False
						else:
							affichage[ax][ay] = True
						if pixel_res == True:
							registres[0xF] = 0x1
					sprite = sprite << 0x1
		elif opcode[0] == 0xE:
			# intruction pour sauter l'instruction suivante si la touche du registre x est pressée
			if kk == 0x9E:
				if touche == registres[x]:
					pc += 2
			# intruction pour sauter l'instruction suivante si la touche du registre x n'est pas pressée
			if kk == 0xA1:
				if touche != registres[x]:
					pc += 2
		elif opcode[0] == 0xF:
			# intruction pour stocker la valeur du premier timer dans le registre x
			if kk == 0x07:
				registres[x] = delay_timer
			# intruction pour attendre l'appuie d'une touche pour la stocker dans le registre x
			elif kk == 0x0A:
				pause = True
				touche = -1
				key_reg = x
			# intruction pour mettre la valeur du premier timer à la valeur du registre x
			elif kk == 0x15:
				delay_timer = registres[x]
			# intruction pour mettre la valeur du second timer à la valeur du registre x 
			elif kk == 0x18:
				sound_timer = registres[x]
			# intruction pour additionner la valeur du registre x à la valeur de i puis le stocker dans i
			elif kk == 0x1E:
				iu += registres[x]
			# intruction pour mettre la valeur de i à la valeur du registre x multiplié par 5
			elif kk == 0x29:
				iu = registres[x] * 5
			# intruction pour convertir un nombre héxadécimal en nombre décimal du registre x dans les emplacements de mémoire i, i+1 et i+2
			elif kk == 0x33:
				memoire[iu] = registres[x] // 100
				memoire[iu + 1] = (registres[x] % 100) // 10
				memoire[iu + 2] = registres[x] % 10
			# intruction pour stocker les valeurs des registre de 0 à x (inclus) dans les emplacements de mémoires i à i+x
			elif kk == 0x55:
				for index in range(x+1):
					memoire[iu + index] = registres[index]
			# intruction pour stocker les valeurs des emplacements de mémoires i à i+x dans les registre de 0 à x (inclus)
			elif kk == 0x65:
				for index in range(x+1):
					registres[index] = memoire[iu + index]

	# décrémenter les timers chaques images si l'émulateur n'est pas en pause
	if pause == False:
		if delay_timer > 0:
			delay_timer -= 1
		if sound_timer > 0:
			sound_timer -= 1
	# si l'émulateur est en pause, attendre un appuie de touche et enlever la pause
	if pause == True and touche != -1:
		registres[key_reg] = touche
		pause = False
	# afficher les pixels de l'écran
	afficher(window, affichage)

# fermer la fenètre et quitter
pygame.quit()