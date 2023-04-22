#include <iostream>
#include <forward_list>

using namespace std;

int main()
{
    forward_list<int> myList = {1, 2, 3, 4, 5};

    // Print the list
    for (auto i : myList)
    {
        cout << i << " ";
    }
    cout << endl;

    // Insert an element at the beginning of the list
    myList.push_front(0);

    // Insert an element after the first element of the list
    myList.insert_after(myList.begin(), 6);

    // Erase an element from the list
    myList.erase_after(++myList.begin());

    // Print the modified list
    for (auto i : myList)
    {
        cout << i << " ";
    }
    cout << endl;

    return 0;
}
