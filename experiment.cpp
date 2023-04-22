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
        Node *node = new Node();
        node->data = data;
        node->next = nullptr;

        if (head == nullptr)
        {
            head = node;
        }
        else
        {
            Node *current = head;
            while (current->next != nullptr)
            {
                current = current->next;
            }
            current->next = node;
        }
    }

    void remove(int data)
    {
        if (head == nullptr)
        {
            return;
        }
        else
        {
            Node *current = head;
            Node *previous = nullptr;
            while (current->next != nullptr)
            {
                if (current->data == data)
                {
                    if (previous == nullptr)
                    {
                        head = current->next;
                        delete current;
                        return;
                    }
                    else
                    {
                        previous->next = current->next;
                        delete current;
                        return;
                    }
                }
                previous = current;
                current = current->next;
            }
        }
    }
};

int main()
{

    return 0;
}
