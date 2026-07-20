n=int(input("enter a number"))
try:
    a=5
    b=2
    c=a/b
    print(c)
except ZeroDivisionError:
    print("not divisible by zero")
else:
    print("enter valid input")
finally:
    print("done")