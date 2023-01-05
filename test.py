from nebula.nebula_dataclass import Borg
import test2

dict1 = Borg()

print("dict1", dict1.move_rnn)

dict2 = Borg()

print("dict3", dict2.move_rnn)

test2.dict3.move_rnn = 9

print("dict1", dict1.move_rnn)
print("dict3", test2.dict3.move_rnn)


