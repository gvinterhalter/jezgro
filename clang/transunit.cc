#include "transunit.h"

Transunit:: Transunit(CXIndex index, std::string& str)
{

    if((_unit = clang_createTranslationUnitFromSourceFile(index, str.data(), 0, NULL, 0, NULL)) == NULL)
    {
        std::cerr << "Translation unit create error" << std::endl;
        //exit(EXIT_FAILURE);
    }
    _filepath = std::string(str);
}

Transunit::~Transunit()
{
    clang_disposeTranslationUnit(_unit);
}

Cursor* Transunit::get_cursor()const
{
    return new Cursor(_unit);
}
