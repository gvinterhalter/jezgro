#include <iostream>
int a;
int b = a;
int const c = b;

int f(){
  int a = 2;
  return a;
}

int main(){
   std::cout << a ;
   std::cout << b ;
  return 0;
}
