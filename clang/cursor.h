#ifndef _CURSOR_H_
#define _CURSOR_H_

#include "transunit.h"
#include <string>
#include <iostream>
#include <clang-c/Index.h>


typedef enum CXChildVisitResult (*TFunc)(CXCursor cursor, CXCursor parent, CXClientData client_data);

class Cursor
{
public:
    ~Cursor();

    std::string get_display()const;
    std::string get_kind() const;
    std::string get_const() const;
    std::string get_typename() const;
    void printout() const;
    void traverse_tree() const;

private:
    CXCursor _cursor;
    TFunc _traverser;
    bool _manipulated;

    //private constructor
    Cursor(CXCursor c);
    Cursor(CXTranslationUnit tunit);

    friend class Transunit;
};




#endif // _CURSOR_H_
