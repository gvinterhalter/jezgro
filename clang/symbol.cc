#include "symbol.h"


    Symbol::Symbol(std::string str, int vers)
    : _type(str), _version(vers)
    {}

    std::string Symbol::getName(std::string& str) const
    {
      return str + "____" + std::to_string(_version + 1);
    }

    void Symbol::increment_version() { _version++; }
    bool Symbol::checkSameVersion (unsigned version) const
    {
      return version == _version;
    }
    void Symbol::change_type(std::string& type)
    {
        _type = type;
        increment_version();
    }

    bool Symbol::is_equal(Symbol s2)
    {
      return (s2._version == s2._version && s2._type == _type);
    }
