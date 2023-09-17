import pygame 
from settings import *
from tile import Tile
from player import Player
from enemies import Enemy
from debug import debug
from debug import check_enemy_searh_time
from debug import check_point
from debug import check_mode
from support import *
from enemies import find_shortest_path

class Level:
	end = False
	def __init__(self):
		#create menu
		# get the display surface 
		self.display_surface = pygame.display.get_surface()
		self.layouts = None
		# sprite group setup
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()
		#item
		self.point = 0
		self.sprites_index = 0
		self.sprites_object_list = []
		self.count_time_speed_restore = 0
		
		# sprite setup
		self.create_map()
		#sound effect game
		self.main_sound = pygame.mixer.Sound('audio/nhac_nhu_db.mp3')
		self.main_sound.play(loops=-1)
		self.main_sound.set_volume(BG_VOLUME)
		self.lose_sound = pygame.mixer.Sound('audio/lose.mp3')
		self.win_sound = pygame.mixer.Sound('audio/victory.mp3')
		self.sound_point = pygame.mixer.Sound('audio/loot_coin.mp3')
		self.food = pygame.mixer.Sound('audio/food.mp3')
		self.boom = pygame.mixer.Sound('audio/boom.mp3')
		self.die = pygame.mixer.Sound('audio/die.wav')
		self.sound_point.set_volume(EFFECT_VOLUME)
		self.food.set_volume(EFFECT_VOLUME)
		self.boom.set_volume(DEBUFF_VOLUME)
		self.die.set_volume(EFFECT_VOLUME)
		self.lose_sound.set_volume(BG_VOLUME)
		self.win_sound.set_volume(BG_VOLUME)

	def create_map(self):

		layouts = {
			'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
			'item': import_csv_layout('map/map_Grass.csv'),
			'object': import_csv_layout('map/map_Objects.csv'),
		}
		graphics = {
			'item': import_folder('graphics/Grass'),
			'objects': import_folder('graphics/objects')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'item':
							surf = graphics['item'][int(col)]
							Tile((x,y),[self.visible_sprites],'item',surf)
							self.sprites_object_list.append(MyObject(x,y,self.sprites_index))
							self.sprites_index+=1
						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites],'object',surf)
		#spawn player // bot
		self.player = Player((1664,3328),[self.visible_sprites],self.obstacle_sprites)
		self.sasuke = Enemy((768,1920),[self.visible_sprites],self.obstacle_sprites,SASUKE)
		self.minato = Enemy((2656, 1742),[self.visible_sprites],self.obstacle_sprites,MINATO)
		self.naruto = Enemy((2112 - 64,3530),[self.visible_sprites],self.obstacle_sprites,NARUTO)

	#finding the sprites index on group sprites (YSortCameraGroup)
	def find_sprites_index(self,x,y):
			for i in range(0,len(self.sprites_object_list)):
				if(self.sprites_object_list[i].x == x and self.sprites_object_list[i].y == y) :
					return self.sprites_object_list[i].id
			return -1
	#restore player_speed
	def restore_speed(self):
		if(self.player.speed != PLAYERSPEED) :
			self.count_time_speed_restore += 1
			if(self.player.speed < PLAYERSPEED) :
				if self.count_time_speed_restore == 100 :
					self.count_time_speed_restore = 0
					self.player.speed += 1
			if(self.player.speed > PLAYERSPEED) :
				
				if self.count_time_speed_restore == 100 :
					self.count_time_speed_restore = 0
					self.player.speed -= 2
				if(self.player.speed <PLAYERSPEED) :
					self.player.speed += (PLAYERSPEED -self.player.speed)
	

	#checking and doing ending
	def when_game_ending(self):
		if self.player.win == False :
			if (self.sasuke.catched or self.naruto.catched) and (self.player.player_mode == "PLAYING MODE"):
				self.ending("lose")
			if (self.minato.catched and self.player.player_mode == "PLAYING MODE"):
				self.ending("lose")
		if (self.point >= 160 and self.player.player_mode == "PLAYING MODE" and  (2048 <= self.player.hitbox.x <= 2176) and (3584 <= self.player.hitbox.y <= 3712)) or self.player.win == True :
			self.ending("win")
		
	#type of ending
	def ending(self,type_ending) :
		ending_font = pygame.font.Font("graphics/font/turok.ttf",100)
		ending_sub_font = pygame.font.Font("graphics/font/turok.ttf",50)
		point_font = pygame.font.Font("graphics/font/turok.ttf",30)
		if type_ending == "lose" :
			if self.player.lose == False :
				self.die.play()
				self.main_sound.stop()
				self.lose_sound.play()
			self.player.lose = True
			self.display_surface.fill((0,0,0))
			ending_surf = ending_font.render(str("YOU LOSE"),True,'RED')
			self.display_surface.blit(LOSE_BG,(-200,-100))
			self.display_surface.blit(ending_surf,(530,290))
		if type_ending == "win" :
			if self.player.win == False :
				self.main_sound.stop()
				self.win_sound.play()
			self.player.win = True
			self.display_surface.fill((0,0,0))
			ending_surf = ending_font.render(str("YOU WIN"),True,'GOLD')
			sub_surf = ending_sub_font.render(str("Congratulations"),True,'LIGHT CORAL')
			point_surf = point_font.render("Your FINAL Point : " + str(self.point),True,'tomato')
			self.display_surface.blit(WIN_BG,(0,-400))
			self.display_surface.blit(ending_surf,(300,250))
			self.display_surface.blit(sub_surf,(300,200))
			self.display_surface.blit(point_surf,(320,375))
			self.display_surface.blit(VICTORY,(920,0))
	#checking and remove kunai from group sprites
	def check_took_kunai(self):
		if self.layouts is None :
			self.layouts = import_csv_layout('map/map_Grass.csv')
		for row_index,row in enumerate(self.layouts):
			for col_index, col in enumerate(row):
				x = col_index * TILESIZE
				y = row_index * TILESIZE
				if((x-64) <= self.player.hitbox.x <= (x+64) and (y-64) <= self.player.hitbox.y <= (y+64)) :
					if self.layouts[row_index][col_index] != '-1':
						if(self.layouts[row_index][col_index]) == '0' :
							# increase point for character
							self.sound_point.play()
							self.point += 1000
						if(self.layouts[row_index][col_index]) == '1' :
							if(self.player.speed)>= PLAYERSPEED//2:
								
								# hitting by boom <-1 uy tin>
								# if(self.player.status == "left") :
								# 	self.player.hitbox.x += 1.5*self.player.speed
								# if(self.player.status == "right") :
								# 	self.player.hitbox.x -= 1.5*self.player.speed
								# if(self.player.status == "up") :
								# 	self.player.hitbox.y += 1.5*self.player.speed
								# if(self.player.status == "down") :
								# 	self.player.hitbox.y -= 1.5*self.player.speed

								self.boom.play()
								self.player.speed -= 1
								self.count_time_speed_restore = 0
						if(self.layouts[row_index][col_index]) == '2' :
							if(self.player.speed) <= PLAYERSPEED*2:
								self.food.play()
								self.player.speed += (int)(PLAYERSPEED*0.3)
								self.count_time_speed_restore = 0
						self.layouts[row_index][col_index] = '-1'
						id = self.find_sprites_index(x,y)
						if(id > -1):
							length = len(self.visible_sprites)
							self.visible_sprites.remove(self.visible_sprites.sprites()[self.find_sprites_index(x,y)])
							if(len(self.visible_sprites) < length) :
								if((id) > -1) :
									self.sprites_object_list.remove(self.sprites_object_list[id])
									for i in range((id),len(self.sprites_object_list)):
										self.sprites_object_list[i].id -= 1
    
	def run(self):
		# -1 POINT every milisecond while POINT > 0
		if self.player.win != True :
			if self.point > 0 :
				self.point -=1
		#AI find path
		find_shortest_path(self.sasuke,(int (self.sasuke.hitbox.x / 64), int (self.sasuke.hitbox.y / 64)), (int (self.player.hitbox.x / 64), int (self.player.hitbox.y / 64)), BFS)	
		find_shortest_path(self.minato,(int (self.minato.hitbox.x / 64), int (self.minato.hitbox.y / 64)), (int (self.player.hitbox.x / 64), int (self.player.hitbox.y / 64)), DFS)	
		find_shortest_path(self.naruto,(int (self.naruto.hitbox.x / 64), int (self.naruto.hitbox.y / 64)), (int (self.player.hitbox.x / 64), int (self.player.hitbox.y / 64)), IDS)	
  		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		#check my point
		check_point(self.point,230,1220)
		check_enemy_searh_time(self.sasuke.execution_time,330,1220)
		check_enemy_searh_time(self.minato.execution_time,430,1220)
		check_enemy_searh_time(self.naruto.execution_time,530,1220)
		#player_mode
		check_mode(self.player.player_mode,690,1230)
		#ending
		self.when_game_ending()
		#check and loot item
		self.check_took_kunai()
		#restore speed for player
		self.restore_speed()
class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):
		#font 
		self.menu_font = pygame.font.Font("graphics/font/turok.ttf",40)
		self.label_font = pygame.font.Font("graphics/font/njnaruto.ttf",15)
		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		#menu surface
		self.menu_surface = pygame.Surface((350, HEIGHT))
		self.menu_surface.blit(MENU_BACKGROUND,(0,0))
		self.draw_text("properties",self.menu_font,(255,255,255),80,20)
		self.draw_text("???   < In Developing >",self.label_font,(255,255,255),50,90)
		self.draw_text("Your POINT",self.label_font,(255,255,255),50,190)
		self.draw_text("Time search ENEMY USING BFS",self.label_font,(255,255,255),50,290)
		self.draw_text("Time search ENEMY USING DFS",self.label_font,(255,255,255),50,390)
		self.draw_text("Time search ENEMY USING IDS",self.label_font,(255,255,255),50,490)
		self.draw_text("Time search ENEMY USING A*",self.label_font,(255,255,255),50,590)
		#get size
		self.half_width = (self.display_surface.get_size()[0] - 350) // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()
		#zoom
		self.zoom_scale = 1
		self.internal_surface_size = (3008,3840)
		self.internal_surf = pygame.Surface(self.internal_surface_size,pygame.SRCALPHA)
		self.internal_rect = self.internal_surf.get_rect(center = (self.half_width,self.half_height))
		self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)
		self.internal_offset = pygame.math.Vector2()
		self.internal_offset.x = self.internal_surface_size[0]//2 - self.half_width
		self.internal_offset.y = self.internal_surface_size[1]//2 - self.half_height
		# creating the floor
		self.floor_surf = pygame.image.load('graphics/tilemap/konoha.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def zoom_keyboard_control(self):
		keys = pygame.key.get_pressed()
		if(keys[pygame.K_q]):
				self.zoom_scale +=0.01
		if(keys[pygame.K_e]):
				self.zoom_scale -=0.01
 
	def custom_draw(self,player):
		
		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset + self.internal_offset
		self.internal_surf.blit(self.floor_surf,floor_offset_pos)
		#drawing the menu

		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
			self.internal_surf.blit(sprite.image,offset_pos)
		
		#scale
		scaled_surf = pygame.transform.scale(self.internal_surf,self.internal_surface_size_vector*self.zoom_scale)
		scaled_rect = scaled_surf.get_rect(center = (self.half_width,self.half_height))
		
		self.display_surface.blit(scaled_surf,scaled_rect)
		#display menu
		# self.menu_surface.fill((255,255,255))
		self.display_surface.blit(self.menu_surface,(1170,0))

		self.zoom_keyboard_control()
		if(self.zoom_scale <=0.44):
			self.zoom_scale += 0.01
	#draw text for menu
	def draw_text(self,text, font, text_col, x, y):
		img = font.render(text, True, text_col)
		self.menu_surface.blit(img, (x, y))

class MyObject:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
