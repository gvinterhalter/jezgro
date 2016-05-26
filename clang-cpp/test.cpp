
#include <iostream>

#define MAX 320

using namespace std;

int a = 2;
auto b = a;
int * const c = & b;

int f(){
  int a = 2;
  return a;
}

int g( int b){
  int a = 2;
  return a + a + b;
}

int g (int a, int b)
{
 return 0;
}


int main(){
  return g(a, a);
}
