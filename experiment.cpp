#include<bits/stdc++.h> // bits/stdc++.h should not be used in production.

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

Node* fn(Node* l1, Node* l2)
{
        Node *newList, *t1, *t2;
        t1 = l1;
        t2 = l2;
        while (t1 != nullptr && t2 != nullptr)
        {
            if(t1->data<t2->data)
            {
                newList->data = t1->data;
                newList = newList->next;
                t1 = t1->next;
            }
            else{
                newList->data = t2->data;
                newList = newList->next;
                t2 = t2->next;
            }
        }
        while (t1!=nullptr)
        {
            newList->data = t1->data;
            newList = newList->next;
            t1 = t1->next;
        }
        while (t2!=nullptr)
        {
            newList->data = t2->data;
            newList = newList->next;
            t2 = t2->next;
        }
        return newList;
};

int main()
{
    Node *l1, *l2, *newList;
    l1 = new Node();
    l2 = new Node();
    newList = new Node();
    l1->data = 1;
    l1->next = new Node();
    l1->next->data = 2;
    l1->next->next = new Node();
    l1->next->next->data = 4;
    l1->next->next->next = nullptr;
    l2->data = 1;
    l2->next = new Node();
    l2->next->data = 3;
    l2->next->next = new Node();
    l2->next->next->data = 4;
    l2->next->next->next = nullptr;
    newList = fn(l1, l2);
    while (newList!=nullptr)
    {
        cout<<newList->data<<" ";
        newList = newList->next;
    }

    return 0;
}
