
#write to program to enter name and percentage marks in a dictionary and display information on screen
d={}
name=input("enter name:")
marks=int(input("enter percentage marks:"))
d["name"]=name
d["marks"]=marks
print(d.items())

# write a program to find the no of occurence of each letter present in the string
s=input("enter a string:")
for i in s:
  print(i ,s.count(i))

# write a program to find no of occurence of each vowel present in the string
s=input("enter a string:")
vowels="aeiou"
for i in vowels:
  print(i,s.count(i))

# write a program to accept student names and marks from keyboard and creates as dict .Alsp display student marks by taking name as input
students={}
n=int(input("enter no of students:"))
for i in range(n):
    name=input("enter name of student:")
    marks=input("enter number of marks:")
    students[name]=marks
print(students.items())
search=input("enter name of student to search:")
if search in students:
       print(search ,students[search])
else:
       print("student not found")   

  #write a python program which should print tabular column with header/columnas:list,tuple,set,frozenset
  #dict rows as syntax,ordered,mutable,allow duplicates,indexed,hetrogenous,hasable.can be dictornary key,can be nested,supports slicing,lookup speed,stores,typical use headers = ["Property", "List", "Tuple", "Set", "Frozenset", "Dictionary"]


headers = ["Property", "List", "Tuple", "Set", "Frozenset", "Dictionary"]
data = [
    ["Syntax", "[]", "()", "{ }/set[()] ", "frozenset()", "{K : V}"],
    ["Ordered", "Yes", "Yes", "No", "No", "Yes"],
    ["Mutable", "Yes", "No", "Yes", "No", "Yes"],
    ["Allow Duplicates", "Yes", "Yes", "No", "No", "Keys: No, Values: Yes"],
    ["Indexed", "Yes", "Yes", "No", "No", "By Key"],
    ["Heterogeneous", "Yes", "Yes", "Yes", "Yes", "Yes"],
    ["Hashable", "No", "Yes", "No", "Yes", "No"],
    ["Can be Nested", "Yes", "Yes", "Yes", "Yes", "Yes"],
    ["Supports Slicing", "Yes", "Yes", "No", "No", "No"],
    ["Lookup Speed", "O(n)", "O(n)", "O(1)", "O(1)", "O(1)"],
    ["Stores", "Values", "Values", "Unique Values", "Unique Values", "Key-Value Pairs"],
    ["Typical Use", "General Purpose", "Fixed Data", "Unique Items", "Immutable Set", "Fast Lookup"]
]

# Print the table
print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(*headers))
print("-" * 90)

for row in data:
    print("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(*row))

