import area

'''test_area file'''

class Test_Area:

	def test_circle(self):
		assert area.circle(14) == 615.44

	def test_square(self):
		assert area.square(4) == 16

	def test_rectangle(self):
		assert area.rectangle(6, 9) == 54

	def test_parallelogram(self):
		assert area.parallelogram(7, 5) == 35

	def test_triangle(self):
		assert area.triangle(12, 10) == 60
