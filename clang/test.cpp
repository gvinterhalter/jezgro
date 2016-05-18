#include <iostream>

using namespace std;

class Foo
{
    Foo();
    void func();
};

class B
{
public:
    void reallyInline()
    {
        Foo f();
    }

    static void sortaInline();
};

Foo::Foo()
{
    func();
}

void Foo::func()
{
    std::cout<< "hello" << std::endl;
}

void B::sortaInline()
{
    std::cout<< "sorta" << std::endl;
}

std::string str = "hello";
string str2 = "hello";

int main()
{
    int a = 4, b = 3,c;
    Foo f();
    B boo;
    c = a - b;
    c++;
    boo.sortaInline();
    return 0;
}
