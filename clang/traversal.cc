#include <iostream>
#include <map>
#include <clang-c/BuildSystem.h>
#include <clang-c/CXCompilationDatabase.h>
#include <clang-c/CXErrorCode.h>
#include <clang-c/CXString.h>
#include <clang-c/Documentation.h>
#include <clang-c/Index.h>
#include <clang-c/Platform.h>


//std::map <std::string, struct symbol> resolve_map;



int main(int argc, char ** argv)
{
    CXIndex index = NULL;
    CXTranslationUnit unit = NULL;
    CXCursor cursor;



    if ((unit = clang_parseTranslationUnit(index, SOURCE, NULL, 0, NULL, 0, 0)) == NULL)
    {
        std::cerr << "Translation unit parse error" << std::endl;
        exit(EXIT_FAILURE);
    }



    if(clang_visitChildren(cursor, traverse_func, NULL) != 0)
    {
        std::cerr << "Traversal failure!" << std::endl;
        exit(EXIT_FAILURE);
    }


    clang_disposeIndex(index);

    return 0;
}
