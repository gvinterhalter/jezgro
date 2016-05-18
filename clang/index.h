#ifndef _INDEX_H_
#define _INDEX_H_

#include "transunit.h"
#include <clang-c/Index.h>
#include <string>
#include <iostream>

class Index
{
public:
  Index();
  ~Index();

  Transunit* tunit_from_file(std::string&) const;
  Transunit* parse(Transunit* tunit);
private:
  CXIndex _index;

};

#endif //  _INDEX_H_
