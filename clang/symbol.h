#ifndef _SYMBOL_H_
#define _SYMBOL_H_

#include <iostream>
#include <map>
#include <sstream>
#include <string>

class Symbol{

  public:
    Symbol(std::string str, int vers);
    std::string getName(std::string& str) const;

    void increment_version();
    bool checkSameVersion (unsigned version) const;
    void change_type(std::string& type);
    bool is_equal(Symbol s2);

  private:
    std::string _type;
    unsigned _version;
};


#endif // _SYMBOL_H_
