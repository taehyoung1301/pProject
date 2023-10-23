import main
import time
sTime = time.time()
main.interpret(main.readFile('foo.txt'))
print("Execution time:" + str(time.time()-sTime))