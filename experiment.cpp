#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

class Node
{
public:
    int data;
    Node *next;
    Node()
    {
        data = 0;
        next = nullptr;
    }
};

class LinkedList
{
    public:
    Node *head;
    LinkedList()
    {
        head = nullptr;
    }
    void add(int data)
    {
        Node *newNode = new Node();
        newNode->data = data;
        newNode->next = head;
        head = newNode;
    }
};

int main()
{

    return 0;
}
