#include <iostream>
using namespace std;

class Node
{
public:
    int data;
    Node *next;
};

int main()
{
    Node *head = new Node();
    Node *second = new Node();
    head->data = 1;
    head->next = second;
    second->data = 2;
    second->next = NULL;

    // free memory allocated for nodes
    delete head;
    delete second;

    return 0;
}
