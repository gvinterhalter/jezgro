#include "index.h"

Index::Index()
{
    _index = clang_createIndex(0, 0);
}

Index::~Index()
{
    clang_disposeIndex(_index);
}


Transunit* Index::tunit_from_file(std::string & filename) const
{
    CXTranslationUnit unit;
    if((unit = clang_createTranslationUnitFromSourceFile(_index, filename.data(), 0, NULL, 0, NULL)) == NULL)
    {
        std::cerr << "Translation unit create error" << std::endl;
        return 0;
    }

    return new Transunit(unit, filename);
}
