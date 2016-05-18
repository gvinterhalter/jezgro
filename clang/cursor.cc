#include "cursor.h"

enum CXChildVisitResult traverse_func(CXCursor cursor, CXCursor parent, CXClientData client_data)
{
    CXType cursor_type;
    CXString typekind_spelling, type_spelling, kind_spelling;
    enum CXCursorKind cursor_kind;

    if(clang_Cursor_isNull(cursor))
        return CXChildVisit_Continue;

    cursor_kind = clang_getCursorKind(cursor);
    cursor_type = clang_getCursorType(cursor);
    kind_spelling = clang_getCursorKindSpelling(cursor_kind);
    type_spelling = clang_getTypeSpelling(cursor_type);
    typekind_spelling = clang_getTypeKindSpelling(cursor_type.kind);


    printf("%s\n",clang_getCString(kind_spelling));

    if(strcmp("", clang_getCString(type_spelling)))
    {
        printf("|| %s\n",clang_getCString(type_spelling));
        printf("|| %s\n",clang_getCString(typekind_spelling));
    }
    printf("\n");

    clang_disposeString(kind_spelling);
    clang_disposeString(type_spelling);
    clang_disposeString(typekind_spelling);

    return CXChildVisit_Recurse;
}
