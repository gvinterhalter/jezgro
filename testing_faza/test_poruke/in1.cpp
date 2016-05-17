#include <iostream>
#include <vector>

using namespace std;


extern "C" {


  extern in a;

  void print();

  void f(){
    a = 100;
    print();
  }
}
