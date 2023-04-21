#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

struct Node
{
    int data;
    Node *next;
};

int main()
{
    // Creating a linked list
    Node *head = NULL;
    Node *second = NULL;
    Node *third = NULL;

    // Allocating memory for nodes in the linked list in the heap
    head = new Node();
    second = new Node();
    third = new Node();

    // Assigning data to the nodes
    head->data = 1;
    head->next = second;

    second->data = 2;
    second->next = third;

    third->data = 3;
    third->next = NULL;

    // Printing the linked list
    Node *temp = head;
    while (temp != NULL)
    {
        cout << temp->data << " ";
        temp = temp->next;
    }

    return 0;
}
