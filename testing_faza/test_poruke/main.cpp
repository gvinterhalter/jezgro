#include <iostream>
#include <string>
#include <dlfcn.h>
#include <vector>


using namespace std;

typedef void (*function_t) () ;

void load(string input){
  cout << "opening " << input << endl;
  const char * error;

  void * p = dlopen(input.c_str(), RTLD_NOW | RTLD_GLOBAL);
  if (p == NULL){
    cerr << dlerror() << endl;
    return;
  } else
    cout << "OK :)" << endl;


  void * p1 = dlopen("./in1.so", RTLD_NOW | RTLD_GLOBAL);
  if (p1 == NULL){
    cerr << dlerror() << endl;
    return;
  } else
    cout << "OK :)" << endl;


  function_t fn = (function_t) dlsym(p1, "f");
  if ((error = dlerror()) ){
    cerr << error << endl;
    return;
  }

  int * a = (int*) dlsym(p, "a");
  cout << *a << endl;


  (*fn)();

}

int main() {

  // cout << "start" << endl;
  load("./in.so");
  // cout << "end" << endl;
  



  return 0;
}
