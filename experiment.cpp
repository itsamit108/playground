#include <iostream>

struct ListNode
{
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(NULL) {}
};

ListNode *removeNthFromEnd(ListNode *head, int n)
{
    // Count the number of nodes in the linked list
    int len = 0;
    ListNode *curr = head;
    while (curr != NULL)
    {
        len++;
        curr = curr->next;
    }

    // Calculate the position of the node to be removed
    int pos = len - n;

    // Special case: remove the head node
    if (pos == 0)
    {
        ListNode *temp = head;
        head = head->next;
        delete temp;
        return head;
    }

    // Traverse the linked list to find the node to be removed
    ListNode *prev = NULL;
    curr = head;
    for (int i = 0; i < pos; i++)
    {
        prev = curr;
        curr = curr->next;
    }

    // Remove the node
    prev->next = curr->next;
    delete curr;

    return head;
}

int main()
{
    // Example usage
    ListNode *head = new ListNode(1);
    head->next = new ListNode(2);
    head->next->next = new ListNode(3);
    head->next->next->next = new ListNode(4);
    head->next->next->next->next = new ListNode(5);

    head = removeNthFromEnd(head, 2);

    ListNode *curr = head;
    while (curr != NULL)
    {
        std::cout << curr->val << " ";
        curr = curr->next;
    }

    return 0;
}
