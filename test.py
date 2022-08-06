

output = []
n = int(input())
si = input().split(" ")
for i in si:
    i = int(i)
    if 100 >= i >= 0:
        for jn,j in enumerate(output):
            if j > i:
                output.insert(jn,i)

         
    if not output:
        print("no data")
    else:
        n = len(output)
        nn=n//2
        if n % 2 == 1:
            print(float(output[nn]))
        elif n % 2 == 0:

            print(((output[nn]+output[nn-1])/2))
