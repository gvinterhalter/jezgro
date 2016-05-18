#ifndef _TRANSUNIT_H_
#define _TRANSUNIT_H_

#include "cursor.h"
#include "index.h"
#include <clang-c/Index.h>
#include <string>

#define SOURCE "test.cpp"

class Transunit
{
public:
  ~Transunit();
  Cursor* get_cursor()const;

private:
  Transunit(CXIndex index, std::string& str);
  CXTranslationUnit _unit;
  std::string _filepath;
  
  friend class Index;
};

#endif // _TRANSUNIT_H_
