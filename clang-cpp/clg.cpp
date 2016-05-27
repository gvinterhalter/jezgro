#include <clang-c/Index.h>

#include <algorithm>
#include <map>
#include <utility>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>

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

struct Insertion
{
    std::string name;
    std::string version;
    unsigned offset;
};

std::map<std::string, Symbol> symbolMap;
std::vector<Insertion> insertionList;
CXCursor rootCursor;
CXTranslationUnit tu = 0;
CXFile file = 0;

bool compare (Insertion first, Insertion second)
{
    return first.offset < second.offset;
}

void makeChangesToFile(const char * filename)
{
  std::ifstream infile (filename, std::ifstream::binary);
  std::string output;
  std::stringstream outfile(output);
  //std::ofstream outfile ((filename +"_new.cpp"), std::ofstream::out);
  std::vector<Insertion>::iterator it = insertionList.begin();
  unsigned offset = 0;

  infile.seekg (0,infile.end);
  long size = infile.tellg();
  infile.seekg (0);

  char* buffer = new char[size];

  while (it != insertionList.end())
  {
    Insertion next = *it;

    infile.read(buffer, (next.offset - offset + next.name.length()));
    outfile.write(buffer, (next.offset - offset + next.name.length()));
    outfile.write(next.version.data(), next.version.length());
    offset = next.offset + next.name.length();

    it++;
  }

  infile.read(buffer, (size - offset));
  outfile.write(buffer, (size - offset));
  outfile.flush();
  delete[] buffer;

  std::cout<< "\n\n\n==========================================================================================" << std::endl;
  std::cout<< "==========================================================================================" << std::endl;
  std::cout<< " Changed file : "<< filename << std::endl;
  std::cout<< "==========================================================================================" << std::endl;
  std::cout<<  (outfile.str()) << std::endl;
  std::cout<< "==========================================================================================" << std::endl;
  std::cout<< "==========================================================================================" << std::endl;


  //outfile.close();
  infile.close();

}

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
    Insertion ins;

    ins.name = name;
    ins.version = "__" + std::to_string(version);
    ins.offset = offset;

    insertionList.push_back(ins);
    std::cout << "\tApplying change to: " << name << "__" << version
              << " at line " << line << " : " << column << std::endl;
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

unsigned int varDecl(CXCursor cursor)
{
  Context context;
  std::string spelling= getCursorSpelling(cursor);
  std::string typeName = getCursorTypeName(cursor);
  std::map<std::string, Symbol>::iterator it = symbolMap.find(spelling);

  if (it == symbolMap.end())
  {
    symbolMap.insert(std::pair<std::string, Symbol> (spelling, {spelling, typeName, 0}));
    context.callerCursor = cursor;
    context.name = spelling;
    context.version = 0;
    clang_findReferencesInFile(cursor, file, {(void*) &context, visitReference});
  }
  else
  {
    std::pair <std::string, Symbol> resultPair = *it;
    Symbol result = resultPair.second;

    if (!typeName.compare(result.type)){
      result.version ++;

      context.callerCursor = cursor;
      context.name = spelling;
      context.version = result.version;

      symbolMap.insert(std::pair<std::string, Symbol>(spelling, {spelling, typeName, result.version}));
      symbolMap.erase(it);

      clang_findReferencesInFile(cursor, file, {(void*) &context, visitReference});
    }
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
  if (clang_equalCursors( parent, rootCursor ) )
  {
    printCursorInfo(cursor, true);
    CXCursorKind kind = clang_getCursorKind ( cursor );
    // obradjujemo deklaracije variabli i funkcija
    if (kind == CXCursor_VarDecl)
      varDecl (cursor);
    //else if (kind == CXCursor_FunctionDecl)
      //fnDecl (cursor);
  }
  else
    printCursorInfo(cursor, false);

  return CXChildVisit_Recurse;
}

int main( int argc, char** argv )
{
  insertionList= std::vector<Insertion>();
  if( argc < 2 )
    return -1;

  CXIndex index = clang_createIndex( 0, 0 );
  tu = clang_parseTranslationUnit( index, argv[1], NULL, 0, NULL, 0, 0);

  if( !tu )
  {
    std::cerr << "Translation Unit not created" << std::endl;
    return -1;
  }

  file = clang_getFile(tu, argv[1]);
  rootCursor = clang_getTranslationUnitCursor( tu );

  clang_visitChildren(rootCursor, mainVisitor, 0);

  std::sort(insertionList.begin(), insertionList.end(), compare);

  makeChangesToFile(argv[1]);

  insertionList.clear();

  clang_disposeTranslationUnit( tu );
  clang_disposeIndex( index );

  return 0;
}
