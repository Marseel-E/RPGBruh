class _Color:
	def __init__(self):
		self.blurple = int("5261f8", 16)
		self.default = self.blurple

	def custom(HEX : str) -> hex:
		""" Converts str to hex """
		return int(HEX, 16)

Color = _Color()


class _Default:
	def __init__(self):
		self.test_server = 879153063036858428

Default = _Default()


class _Icon:
	def __init__(self):
		self.increase = "<:increase:945438059644731442>"
		self.decrease = "<:decrease:945438157929852948>"

Icon = _Icon()


from random import randint, choice

def generate_equation() -> (int, str):
	""" Generates a random math equation """
	number_of_operations = randint(1,5)

	equation = f"{randint(1,9)} "
	for i in range(number_of_operations):
		equation += f"{choice(['*', '/', '+', '-'])} {randint(1,9)} "

	result = eval(equation)

	return (round(result), equation)