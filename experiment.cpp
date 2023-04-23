#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

struct ListNode
{
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(NULL) {} // constructor
};

ListNode *addTwoNumbers(ListNode *l1, ListNode *l2)
{
    ListNode *head = new ListNode(0); // dummy head
    ListNode *p = head;
    int carry = 0;
    while (l1 || l2 || carry)
    {
        int sum = 0;
        if (l1)
        {
            sum += l1->val;
            l1 = l1->next;
        }
        if (l2)
        {
            sum += l2->val;
            l2 = l2->next;
        }
        sum += carry;
        carry = sum / 10;
        p->next = new ListNode(sum % 10);
        p = p->next;
    }
    return head->next;
}

int main()
{
    ListNode *l1 = new ListNode(2);
    ListNode *l2 = new ListNode(4);
    ListNode *l3 = new ListNode(3);
    l1->next = l2;
    l2->next = l3;

    ListNode *l4 = new ListNode(5);
    ListNode *l5 = new ListNode(6);
    ListNode *l6 = new ListNode(4);
    l4->next = l5;
    l5->next = l6;

    ListNode *result = addTwoNumbers(l1, l4);
    while (result)
    {
        cout << result->val << " ";
        result = result->next;
    }

    return 0;
}
