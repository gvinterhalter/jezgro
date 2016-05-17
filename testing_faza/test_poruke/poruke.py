include = """
#include <stdio>
#include <vector>
using namespace std;

"""

p1 = """
int a = 25;
string b = "Hello World";
vector<int> = [1,2,3]
"""

p2 = """
#include  <vector>
#include  <stdio>
using namespace std;
"""





print(include, p1)

name = "in.cpp"
with open(name, "w") as f:
    f.writelines(include + p1)


compileCmd =  "g++ --std=c++11 in.cpp -o out.o"
