import curses

# curses 库 ( ncurses ) 提供了控制字符屏幕的独立于终端的方法
# curses 程序将在纯文本系统上、xterm 和其它窗口化控制台会话中运行，这使这些应用程序具有良好的可移植性。
from random import randrange, choice
from collections import defaultdict

# 用户动作表示
actions = ["Up", 'Left', 'Down', 'Right', 'Restart', 'Exit']

# 根据用户输入获取有效键zhi
# ord()返回字符的unicode编码
letter_codes = [ord(ch) for ch in 'WASDQRwasdrq']

# 将action与输入行为进行关联,zip()将对应元素打包成元组，然后映射成字典
actions_dict = dict(zip(letter_codes, actions*2))

# 状态机处理游戏状态，不同状态下有哪些情况
# 用户输入处理
def get_user_action(keyboard):
	char = 'N'
	while char not in actions_dict:
		char = keyboard.getch()
	return actions_dict[char]

# 矩阵转置
def transpose(field):
	return [list(row) for row in zip(*field)]

# 矩阵逆转

def invert(field):
	return [row[::-1] for row in field]


# 创建棋盘
class GameField(object):
	def __init__(self,height = 4,width = 4,win = 2048):
		self.height = height
		self.width = width
		self.win_value = 2048
		self.score = 0
		self.maxscore = 0
		self.reset() 

	# 棋盘操作

	def spawn(self):
		# 随机生成2或者4
		new_element = 4 if randrange(100) > 89 else 2
		# @ choice是干啥的
		(i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
		self.field[i][j] = new_element



	def reset(self):
		# 重置棋盘
		if self.score>self.maxscore:
			self.maxscore=self.score

		self.score = 0
		#  不理解
		self.field = [[0 for i in range(self.width)] for j in range(self.height)]
		self.spawn()
		self.spawn()



	def move(self,direction):
		def move_row_left(row):
			# 一行向左合并
			def tighten(row):# 把离散的单元积压在一起
				new_row = [i for i in row if i != 0]
				new_row += [0 for i in range(len(row)-len(new_row))]
				return new_row

			def merge(row):
				# 对临近元素进行合并
				# 好多不明白的
				is_pair = False
				new_row=[]
				for i in range(len(row)):
					if is_pair:
						new_row.append(2*row[i])
						self.score += 2*row[i]
						is_pair = False
					else:
						if i+1<len(row) and row[i] == row[i+1]:
							is_pair = True
							new_row.append(0)
						else:
							new_row.append(row[i])

				assert len(new_row) == len(row)

				return new_row

			return tighten(merge(tighten(row)))


		moves= {}

		moves['Left'] = lambda field:[move_row_left(row) for row in field]
		moves['Right'] = lambda field:invert(moves['Left'](invert(field)))
		moves['Up'] = lambda field:transpose(moves["Left"](transpose(field)))
		moves['Down'] = lambda field:transpose(moves['Right'](transpose(field)))

		if direction in moves:
			if self.move_is_possible(direction):
				self.field = moves[direction](self.field)
				self.spawn
				return True
			else:
				return False

	# 判断输赢
	def is_win(self):
		return any(any(i>=self.win_value for i in row ) for row in self.field)

	def is_gameover(self):
		return not any(self.move_is_possible(move) for move in actions)

	def move_is_possible(self,direction):
		def row_left_is_moveable(row):
			def change(i):
				if row[i] == 0 and row[i+1] != 0:
					return True

				if row[i] !=0 and row[i+1] == row[i]:
					return True

				return False
			return any(change(i) for i in range(len(row)-1))

		check = {}
		check['Left'] = lambda field:any(row_left_is_moveable(row) for row in field)
		check['Right'] = lambda field: check['Left'](invert(field))
		check['Up'] = lambda field:check['Left'](transpose(field))
		check["Down"] = lambda field: check['Right'](transpose(field))

		if direction in check:
			return check[direction](self.field)

		else:
			return False

	# 绘制游戏界面
	def draw(self,screen):
		help_string1 = '(W)Up (S)Down (A)Left (D)Right'
		help_string2 = '	(R)Restart (Q)Exit'
		gameover_string = '		Game Over'
		win_string = '			You Win'

		def cast(string):
			screen.addstr(string + "\n")

		# 绘制水平分割线
		def draw_hor_sepline():
			line = '+'+('+---'*self.width+"+")[1:]
			separator = defaultdict(lambda:line)
			if not hasattr(draw_hor_sepline,'counter'):
				draw_hor_sepline.counter = 0
			cast(separator[draw_hor_sepline.counter])
			draw_hor_sepline.counter += 1

		def draw_row(row):
			cast(''.join('|{:^3}'.format(num) if num >0 else '|   'for num in row) + "|")

		screen.clear()

		cast("Score:"+str(self.score))
		if 0!=self.maxscore:
			cast('maxscore:'+ str(self.maxscore))

		for row in self.field:
			draw_hor_sepline()
			draw_row(row)

		draw_hor_sepline()

		if self.is_win():
			cast(win_string)
		else:
			if self.is_gameover():
				cast(gameover_string)
			else:
				cast(help_string1)
		cast(help_string2)












def main(stdscr):



		def init():

			game_field.reset()
			return 'Game'

		def not_game(state):
			# 画出win或者gameover的界面
			game_field.draw(stdscr)
			# 读取用户输入的action,判断是重启还是退出
			action = get_user_action(stdscr)

			response = defaultdict(lambda: state)
			response['Restart'], response['Exit'] = 'Init', 'Exit'
			return response[action]

		def game():
			# 画出当前棋盘
			game_field.draw(stdscr)
			# 读取用户输入的action
			action = get_user_action(stdscr)
			if action == 'Restart':
				return 'Init'
			if action == 'Exit':
				return 'Exit'

			if game_field.move(action):
				if game_field.is_win():
					return 'Win'
				if game_field.is_gameover():
					return 'Gameover'

			return 'Game'

		static_actions = {

			'Init': init,
			'Win': lambda: not_game('Win'),
			'Gameover': lambda: not_game('Gameover'),
			'Game': game
		}

		curses.use_default_colors()
		game_field = GameField(win=2048)
		state = 'Init'
		# 状态机开始循环
		while state != 'Exit':
			# 返回值是一个函数的调用，所以要加一个（）
			state = static_actions[state]()


curses.wrapper(main)


    

    




