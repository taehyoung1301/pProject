import re
def splitter(line:str):
    blacklist: list[str] = [' ', '\n', '\0']
    pattern = re.compile(r'''
        "[^"]*" # "로 시작, 가운데에 "가 아닌 문자 아무 양이나, "로 끝
        | # 또는
        [^" \t\n\r\f\v]+ # 시작은 신경 X, ",그리고 다른 공백 문자들이 아닌 문자 1개 이상의 양이나, 끝 신경 X
    ''',re.VERBOSE)
    return pattern.findall(line)
def readFile(file:str):
    out = []
    with open(file) as f:
       for line in f:
           line: str
           words:list[str]=splitter(line)#(str.removesuffix(line,'\n'))
           out.extend(words)
    return out

def interpret(code:list[str]):
    pc:int=0 #PROGRAM COUNTER
    funcpcs:list = [] #함수가 실행되었을때 실행위치(pc)를 스택에 넣음, 이하 @에서 설명
    stack:list = [] #모든 코드가 읽히면서 입력되는 스택
    vars:list = [{}] #변수를 저장하는 딕셔너리의 스택, 가장 아래 딕셔너리는 기본 변수이고, 나머지는 함수 실행 속 변수 스택이다.
    funcs:dict = {} #함수가 정의될때, 함수의 이름과 실행 시작위치를 딕셔너리로 저장한다.
    while (len(code) > pc):
        current = code[pc]
        match current:
            case 'if': # 1 if ~~~~~ endif -> ~~~~~ 실행
                if(not stack.pop()):
                    ifcnt: int = 0
                    while True:
                        if(code[pc]=='if'):ifcnt+=1
                        elif(code[pc]=='endif'):ifcnt-=1
                        pc+=1
                        if ifcnt==0:break
                    pc-=1
            case 'while' | 'endif':
                None #do nothing
            case 'repeat':
                if (not stack.pop()):
                    whilecnt: int = 1
                    while True:
                        if (code[pc] == 'while' ):
                            whilecnt += 1
                        elif (code[pc] == 'endwhile'):
                            whilecnt -= 1
                        pc += 1
                        if whilecnt == 0: break
                    pc-=1
            case 'endwhile':
                whilecnt: int = 0
                while True:
                    if (code[pc] == 'while'):
                        whilecnt += 1
                    elif (code[pc] == 'endwhile'):
                        whilecnt -= 1
                    pc -= 1
                    if whilecnt == 0: break
                pc+=1
            case 'eq':
                stack.append(stack.pop() == stack.pop()) # 1 1 eq -> 1 = 1 -> true
            case 'neq':
                stack.append(stack.pop() != stack.pop())
            case 'and':
                x = stack.pop()
                y = stack.pop()
                stack.append(x and y)
            case 'or':
                x = stack.pop()
                y = stack.pop()
                stack.append(x or y)
            case 'not':
                stack.append(not stack.pop())
            case 'gt':
                stack.append(stack.pop() < stack.pop()) # 1 2 gt -> 2 < 1 -> false
            case 'gte':
                stack.append(stack.pop() <= stack.pop())  # 1 2 gte -> 2 <= 1 -> false
            case 'lt':
                stack.append(stack.pop() > stack.pop())  # 1 2 lt -> 2 > 1 -> true
            case 'lte':
                stack.append(stack.pop() >= stack.pop())  # 1 2 lte -> 2 >= 1 -> true
            case 'mul':
                stack.append(stack.pop() * stack.pop())
            case 'div':
                x = stack.pop()
                y = stack.pop()
                stack.append(y / x)
            case 'add':
                x = stack.pop()
                y = stack.pop()
                stack.append(y+x)
            case 'sub':
                x = stack.pop()
                y = stack.pop()
                stack.append(y-x)
            case 'print':
                print(stack.pop())
            case 'input':
                stack.append(input())
            case 'int':
                stack.append(int(stack.pop()))
            case 'string':
                stack.append(str(stack.pop()))
            case 'float':
                stack.append(float(stack.pop()))
            case 'endfunc':
                if(len(funcpcs) > 0):
                    pc = funcpcs.pop()
                    vars.pop()
            case 'newlist':
                stack.append([])
            case 'getindex':
                index = stack.pop()
                l:list = stack.pop()
                stack.append(list[index])
            case 'setindex': # (x에 리스트가 있을때) <-x 0 a setindex ->x
                x = stack.pop()
                index:int = stack.pop()
                l:list = stack.pop()
                l[index] = x;
            case 'appendlist':
                appen = stack.pop()
                l:list = stack.pop()
                l.append(appen)
            case _ if current.startswith(':'): #:funcname 으로 정의
                funcs[current.removeprefix(":")] = pc+1,int(code[pc+1])
                while (code[pc] != 'endfunc'): pc+=1
            case _ if current.startswith('@'): #@funcname -> funcname 실행
                startpc,argcnt =funcs[current.removeprefix("@")]
                varflip:list = []
                for i in range(argcnt):
                    varflip.append(stack.pop())
                stack.extend(varflip)
                funcpcs.append(pc)
                pc = startpc
                vars.append({})
            case _ if current.startswith('->'): # 11 ->x
                name = current.removeprefix('->')
                var = stack.pop()
                vars[-1][name] = var
            case _ if current.startswith('<-'):  # <-x
                name = current.removeprefix('<-')
                stack.append(vars[-1][name])
            case _ if current[0].isnumeric():
                if "." in current:
                    stack.append(float(current))
                else:
                    stack.append(int(current))
            case _ if current[0] == '"':
                    stack.append(current.removeprefix('"').removesuffix('"'))
            case _:
                raise Exception("bad code")
        pc+=1

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    interpret(readFile(args[0]))