#ifndef _UTILS_H_
#define _UTILS_H_

#include <clang-c/Index.h>

#include <iostream>
#include <string>


std::string getCursorKindName( CXCursorKind cursorKind )
{
  CXString kindName  = clang_getCursorKindSpelling( cursorKind );
  std::string result = std::string(clang_getCString( kindName ));

  clang_disposeString( kindName );
  return result;
}

std::string getCursorSpelling( CXCursor cursor )
{
  CXString cursorSpelling = clang_getCursorSpelling( cursor );
  std::string result      = std::string(clang_getCString( cursorSpelling ));

  clang_disposeString( cursorSpelling );
  return result;
}

std::string getCursorTypeName ( CXCursor cursor )
{
  CXType cursorType = clang_getCursorType( cursor );
  CXString typeSpelling = clang_getTypeSpelling( cursorType );
  std::string result = std::string(clang_getCString( typeSpelling ));

  clang_disposeString( typeSpelling );
  return result;
}

std::string getCursorDisplayName (CXCursor cursor)
{
  CXString displayName = clang_getCursorDisplayName(cursor);
  std::string result = std::string (clang_getCString(displayName));
  clang_disposeString(displayName);

  return result;
}

void printCursorInfo(CXCursor cursor, bool global = false){

  CXCursorKind cursorKind = clang_getCursorKind( cursor );


  std::cout << (global ? "global -" : "local -")
            << " " << getCursorDisplayName(cursor)
            << " "  << getCursorKindName( cursorKind )
            << " (" << getCursorSpelling( cursor )
            << ") :: " << getCursorTypeName( cursor )
            << std::endl;
}

#endif // _UTILS_H_
