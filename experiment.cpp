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

Node *fn(Node *head, int n)
{
    Node *curr = head;
    Node *prev = nullptr;
    int c = 1;
    int l = 0;
    while (curr != nullptr)
    {
        curr = curr->next;
        l++;
    }

    while (curr != nullptr && c < l - n + 1)
    {
        curr = curr->next;
        prev = curr;
        c++;
    }
    prev->next = curr->next;
    delete curr;
    return head;
}

int main()
{

    return 0;
}
