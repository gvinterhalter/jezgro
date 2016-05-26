#include <clang-c/Index.h>

#include <map>
#include <utility>
#include <iostream>
#include <string>

#include "utils.hpp"


struct Symbol
{
  std::string name;
  std::string type;
  unsigned version;

} ;

struct Context
{
  std::string name;
  unsigned version;
  CXCursor callerCursor;
};

std::map<std::string, Symbol> symbolMap;
CXCursor rootCursor;
CXTranslationUnit tu = 0;
CXFile file = 0;

void changeRefName(CXCursor cursor, std::string name, unsigned version)
{
  CXFile file;
  CXSourceLocation location = clang_getCursorLocation(cursor);
  unsigned line, column, offset;

  clang_getSpellingLocation(location, &file, &line, &column, &offset);

  if(!line || !column)
  {
    std::cerr << "\tUnable to apply changes "<< std::endl;
  }
  else
  {
    std::cout << "\tApplying change to: " << name << "__" << version
              << " at line " << line << " : " << column << std::endl
              << "\tOffset: "<< offset << " in buffer" << std::endl;
  }
}

enum CXVisitorResult   visitReference (void *context, CXCursor cursor, CXSourceRange range)
{
  Context passedContext = *((Context *)context);
  CXCursor refCursor = clang_getCursorReferenced(passedContext.callerCursor);

  if (clang_equalCursors(passedContext.callerCursor, refCursor))
  {
      changeRefName(cursor, passedContext.name, passedContext.version);
  }
  else
  {
    std::cerr << "Traversing error -- Unmatching cursors."<< std::endl;
  }

  return CXVisit_Continue;
};

unsigned int varDecl(CXCursor cursor){
  std::string spelling= getCursorSpelling(cursor);
  std::string typeName = getCursorTypeName(cursor);
  std::map<std::string, Symbol>::iterator it = symbolMap.find(spelling);

  if (it == symbolMap.end())
  {
    symbolMap.insert(std::pair<std::string, Symbol> (spelling, {spelling, typeName, 0}));
  }
  else
  {
    //Uziamo podatke iz pronadjenog elementa, uklanjamo ga i ubacujemo azuriranu verziju
    Context context;
    std::pair <std::string, Symbol> resultPair = *it;
    Symbol result = resultPair.second;

    result.version ++;
    symbolMap.erase(it);
    context.callerCursor = cursor;
    context.name = spelling;
    context.version = result.version;


    symbolMap.insert(std::pair<std::string, Symbol>(spelling, {spelling, typeName, result.version}));
    symbolMap.erase(it);

    clang_findReferencesInFile(cursor, file, {(void*) &context, visitReference});
  }

  return 0;
}

unsigned int fnDecl(CXCursor cursor)
{
  std::string spelling= getCursorSpelling(cursor);
  std::string typeName = getCursorTypeName(cursor);
  std::map<std::string, Symbol>::iterator it = symbolMap.find(spelling);

  if (!spelling.compare("main"))
    return 0;

  if (it == symbolMap.end())
  {
    symbolMap.insert(std::pair<std::string, Symbol> (spelling, {spelling, typeName, 0}));
  }
  else
  {
    //Uziamo podatke iz pronadjenog elementa, uklanjamo ga i ubacujemo azuriranu verziju
    Context context;
    std::pair <std::string, Symbol> resultPair = *it;
    Symbol result = resultPair.second;

    result.version ++;
    symbolMap.erase(it);
    context.callerCursor = cursor;
    context.name = spelling;
    context.version = result.version;

    symbolMap.insert(std::pair<std::string, Symbol>(spelling, {spelling, typeName, result.version}));
    symbolMap.erase(it);

    clang_findReferencesInFile(cursor, file, {(void*) &context, visitReference});
  }

  return 0;}

enum CXChildVisitResult mainVisitor( CXCursor cursor, CXCursor parent, CXClientData clientData )
{
  // Ako nismo u main fajlu (neki include recimo), preskoci obradu  cursora
  if ( ! clang_Location_isFromMainFile( clang_getCursorLocation(cursor) ) )
    return CXChildVisit_Continue;


  // Ako je root CXCursor parent, to znaci da je u pitanju globalna stvar
  if ( !clang_equalCursors( parent, rootCursor ) )
    printCursorInfo(cursor, false);
  else
    printCursorInfo(cursor, true);

  CXCursorKind kind = clang_getCursorKind ( cursor );
  // obradjujemo deklaracije variabli i funkcija
  if (kind == CXCursor_VarDecl || kind == CXCursor_ParmDecl)
    varDecl (cursor);
  else if (kind == CXCursor_FunctionDecl)
    fnDecl (cursor);

  return CXChildVisit_Recurse;
}

int main( int argc, char** argv )
{
  if( argc < 2 )
    return -1;

  CXIndex index = clang_createIndex( 1, 0 );
  tu = clang_parseTranslationUnit( index, argv[1], NULL, 0, NULL, 0, 0);

  if( !tu )
  {
    std::cerr << "Translation Unit not created" << std::endl;
    return -1;
  }

  file = clang_getFile(tu, argv[1]);
  rootCursor = clang_getTranslationUnitCursor( tu );

  clang_visitChildren(rootCursor, mainVisitor, 0);

  clang_disposeTranslationUnit( tu );
  clang_disposeIndex( index );

  return 0;
}
