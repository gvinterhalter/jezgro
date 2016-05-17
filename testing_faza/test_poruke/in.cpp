#include <iostream>
#include <vector>

using namespace std;

template <typename T>
std::ostream & operator<<(std::ostream & out, vector<T> a){
  out << "[";
  for(auto & x : a)
    out << x << " ";
  out << "]";
  return out;
}


extern "C" {

  int a = 25;
  string b = "Hello World";
  vector<int> lista= {1,2,3,4};

  void print(){
    cout << ", "  << b << ", " << lista << endl;
  }
}
