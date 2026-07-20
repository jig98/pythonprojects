
# increasing triangle number pattern
n=5
for i in range(1,n+1):
     for j in range(1,i+1):
          print(j,end="")
     print()          
     
     #same number pattern
print()
for i in range(1,n+1):
     for j in range(1,i+1):
          print(i,end="")
     print()          
          
print()
  # floyds triangle  

num=1
n=5
for i in range(1,n+1):
     for j in range(i):
          print(num,end=" ")
          num=num+1
     print()
