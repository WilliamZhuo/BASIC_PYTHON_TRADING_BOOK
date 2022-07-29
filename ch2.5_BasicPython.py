##################################################
## CH 2.5.1. Arithmetic operations 
#################################################
#add
print('7+5=?')
print(7+5)  

#subtract
print('1.0-1.3=?')
print(1.0-1.3)

#multiply
pi=3.14
r=2
print('pi=3.14')
print('r=2')
print('pi*r*r=?')
print(pi*r*r)

#divide
print('4.6/8.7=?')
print(4.6/8.7)

#max,min
print('max(1,5,11,4,9,6)=?')
print(max(1,5,11,4,9,6))
print('min(1,5,11,4,9,6)=?')
print(min(1,5,11,4,9,6))

###################################################
##  CH 2.5.2 Python裡面的迴圈用法
######################################################
# for loop example 1
print('print i in 0,1,2,... till i>=10:')
for i in range(0,10,1):
    print(i)
# for loop example 2
print('print i in 0,0.3,0.6,....,... till i>=4.0:')
import numpy as np
for i in np.arange(0.0,4.0,0.3):
    print(i)
# for loop example 3
print('print all numbers in the list:')
l=[1,1,2,3,5,8,13]
for i in l:
    print(i)
    
# while loop example
print('print fibonacci numbers:')
a_n2=0
a_n1=1
a_n=1
while a_n <= 100:
    a_n2=a_n1
    a_n1=a_n
    a_n=a_n1+a_n2
    print(a_n)


###################################################
##  CH 2.5.3 Functions
######################################################
#add function example
print('add(3,6):')
def add(a,b):
    output=a+b
    return output
print(add(3,6))

#circle area example
print('circlearea(r):')
def circlearea(r):
    pi=3.14
    return pi*r*r
print(circlearea(2))



#local variable example
print('local variable example:')
thetarget=0
def modify_local():
    thetarget=1
    return
modify_local() 
print(thetarget)

#global variable example 
print('global variable example:')
def modify_global():
    global thetarget
    thetarget=1
    return
modify_global() 
print(thetarget)

#global variable example 2
thesource=2
print('global variable example2:')
def modify_global2():
    global thetarget
    thetarget=thesource
    return
modify_global2() 
print(thetarget)

#fibonacci example 1
print('the 10th fiboonacci number:')
def calculate_fibonacci(n):
    if(n==0):
        return 0
    elif(n==1):
        return 1
    else:
        return calculate_fibonacci(n-1)\
              +calculate_fibonacci(n-2)
print(calculate_fibonacci(10))

###################################################
##  CH 2.5.4 Data Types
######################################################
##########################################
#string example 1
##########################################
print('string example:')
str_0='Hello world'
print(str_0)
print('type:')
print(type(str_0))

##########################################
#string example 2
##########################################
#string concatenation
print('string concatenation example:')
str_1='Hello'
str_2=' world'
print(str_1+str_2)

##########################################
#string example 3
##########################################
#string concatenation and convert to string
print('integer to string example:')
str_1='book writen year:'
str_2=str(2022)
print(str_1+str_2)

##########################################
#list example 1
##########################################
print('list example:')
l=[1,1,2,3,5,8,13]
print('l[0]:')
print(l[0])
print('l[3]:')
print(l[3])
print('last element:')
print(l[-1])

##########################################
#list example 2
##########################################
print('list of strings example')
l=['stringA','stringB','stringC','stringD']
print(l[2])

##########################################
#list example 3
##########################################
print('list of lists example')
l1=[1,1,2,3,5,8,13]
l2=['stringA','stringB','stringC','stringD']
l3=[l1,l2]
print(l3[0][5])
print(l3[1][1])

#dict example 1
print('dict example')
d={'Jan':31,'Feb':28,'Mar':31}
print('Number of days in January')
print(d['Jan'])
print('Number of days in February')
print(d['Feb'])
print('Number of days in March')
print(d['Mar'])

#class example 1
import math
class point:
    x=0
    y=0
    def __init__(self, x=None, y=None):
        if(x==None or y==None):
            self.x=0
            self.y=0
        else:
            self.x = x
            self.y = y
a=point() 
b=point(3,3) 
print('a.x:')
print(a.x)
print('a.y:')
print(a.y)
print('b.x:')
print(b.x)
print('b.y:')
print(b.y)

def distance(a,b):
    val=(a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y)
    return math.sqrt(val)
dis=distance(a,b)
print('distance of a,b:')        
print(dis)

#class example 2
class point:
    x=0
    y=0
    def __init__(self, x=None, y=None):
        if(x==None or y==None):
            self.x=0
            self.y=0
        else:
            self.x = x
            self.y = y
        
    def distance(self,b):
        val=(self.x-b.x)*(self.x-b.x)+(self.y-b.y)*(self.y-b.y)
        return math.sqrt(val)
a=point()
b=point(3,3)
dis=a.distance(b)
print('distance of a,b:')
print(dis)

#class example 3
class circle:
    def __init__(self, r=None):
        if(r==None):
            self.r=0
        else:
            self.r = r
    def area(self):
        return math.pi*self.r*self.r
class square:
    def __init__(self, edge=None):
        if(edge==None):
            self.edge=0
        else:
            self.edge = edge
    def area(self):
        return self.edge*self.edge
c=circle(3)
s=square(5)
print('circle area:')
print(c.area())
print('square area:')
print(s.area())
 
def circle_area(c):    
    return math.pi*c.r*c.r

def square_area(s):    
    return s.edge*s.edge

print('circle area:')
print(circle_area(c))
print('square area:')
print(square_area(s))
 
def circle_area(c:circle):    
    return math.pi*c.r*c.r
def square_area(s:square):    
    return s.edge*s.edge

#class example 4
print('class example 4:')
l=list()
def modify_list(l):
    l.append(1)
modify_list(l)
print('l:')
print(l)

def modify_circle(c):
    c.r=99
    return
modify_circle(c)
print('c.r:')
print(c.r)

i=0
def modify_i(i):
    i=5
    return
modify_i(i)
print('i:')
print(i)

#fibonacci example 2
import time
start = time.time()
calculate_fibonacci(30)
end = time.time()
print('original fibonacci time:')
print(end - start)

def calculate_fibonacci_2(n):
    print('fib:'+str(n))
    if(n==0):
        return 0
    elif(n==1):
        return 1
    else:
        return calculate_fibonacci_2(n-1)\
              +calculate_fibonacci_2(n-2)
calculate_fibonacci_2(5)


def calculate_fibonacci_modified(n):
    l=[-1]*(n+1)
    def fibonacci(n,l):
        if(l[n]>0):
            return l[n]
        else:
            val=0
            if(n==0):
                val=0
            elif(n==1):
                val=1
            else:
                val=fibonacci(n-1,l)\
                      +fibonacci(n-2,l)
            l[n]=val
            return val
    return fibonacci(n,l)

import time
start = time.time()
calculate_fibonacci_modified(30)
end = time.time()
print('modified fibonacci time:')
print(end - start)

#numpy example 1
print('numpy example:')
print('[1 2 3] X [4 5 6]  ')
print('[4 5 6] X [1 2 3] =')

import numpy as np
a=np.array([[1,2,3],[4,5,6]])
b=np.array([[4,5,6],[1,2,3]])
print(a*b)

#numpy example 2
import numpy as np
print('numpy example 2')
a=np.array([[1,2,3],[4,5,6]])
print('second row, third column')
print(a[1,2])
print('first column')
print(a[:,0])
print('first row')
print(a[0,:])

#numpy example 3
import numpy as np
print('numpy example 3')
a=np.array([[1,2,3],[4,5,6]])
print('set second row, third column to 9')
a[1,2]=9
print(a)
print('set second column to second column +1')
a[:,1]=a[:,1]+1
print(a)
print('set first row to second row +3')
a[0,:]=a[0,:]+3
print(a)


#dataframe example 1
print('dataframe example 1 initial:')

import pandas as pd
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
print(df)

#dataframe example 2
print('dataframe example 2 get column:')
import pandas as pd
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
print(df['col1'])

#dataframe example 3
import yfinance as yf
tw0050 = yf.Ticker("0050.tw")
df0050 = tw0050.history(period="max")

#dataframe head 
print('df0050 head:')
print(df0050.head())

print('df0050 head(10):')
print(df0050.head(10))

#dataframe tail
print('df0050 tail:')
print(df0050.tail())

print('df0050 tail(10):')
print(df0050.tail(10))

#dataframe index
print('df0050 index:')
print(df0050.index)

#dataframe column
print('df0050 columns:')
print(df0050.columns)


#dataframe loc vs iloc
print('df0050 loc:')
print(df0050.loc['2022-07-14'])

print('df0050 iloc:')
print(df0050.iloc[0])

#dataframe loc range
print('df0050 loc range:')
print(df0050.loc['2022-07-01':'2022-07-14'])

#dataframe iloc range
print('df0050 iloc range:')
print(df0050.iloc[5:10])

#dataframe contional access
print('df0050 contional access:')
print('get all index of close>100:')
print(df0050['Close']>100)
print('get all date with close>100:')
theindex=df0050['Close']>100
print(df0050[theindex])
print('get all date with close>100:')
print(df0050[df0050['Close']>100])


#dataframe fillna vs dropna
temp=df0050.loc['2022-07-01':'2022-07-14']
temp.iat[1,0]=float('Nan')#2nd Open=Nan
temp.iat[1,1]=float('Nan')#2nd Hight=Nan
temp.iat[1,2]=float('Nan')#2nd Low=Nan
temp.iat[1,3]=float('Nan')#2nd Close=
print('Set Nan:')
print(temp)

print('Dropna:')
print(temp.dropna())

print('Fillna ffill:')
print(temp.fillna(method='ffill'))

print('Fillna bfill:')
print(temp.fillna(method='bfill'))


#drawing
import matplotlib.pyplot as plt
plt.plot(df0050['Close'])
plt.show()


plt.plot(df0050['High'],color='green')
plt.plot(df0050['Low'],color='red')
plt.show()

plt.plot(df0050['Close'][-100:-1],marker='.')
plt.title('draw dots')
plt.show()

plt.plot(df0050['Close'][-100:-1]\
         ,marker='.'\
         ,linestyle = 'None')
plt.title('draw dots no lines')
plt.show()

f, axarr = plt.subplots(2,2)
axarr[0,0].set_title('Open')
axarr[0,0].plot(df0050['Open'])
axarr[0,1].set_title('High')
axarr[0,1].plot(df0050['High'])
axarr[1,0].set_title('Low')
axarr[1,0].plot(df0050['Low'])
axarr[1,1].set_title('Close')
axarr[1,1].plot(df0050['Close'])
plt.show()
          