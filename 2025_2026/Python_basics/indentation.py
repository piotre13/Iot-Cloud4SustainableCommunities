


for i in range(3):
    print(i)
print("Loop finished")  # runs once, after the loop


x=10
if x > 0:
print("Positive") #IndentationError


x=10
if x > 0:
    print("Positive") 


for i in range(3):
    msg = "Hello"
print(msg)  # ❌ NameError, msg not visible outside the function



for i in range(3):
    msg = "Hello"
    print(msg)  # ✅ No error, msg is visible within the function







