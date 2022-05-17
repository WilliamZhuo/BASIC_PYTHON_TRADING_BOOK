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
##  CH 2.5.2
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
