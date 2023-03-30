#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

// Group anagrams
// https://leetcode.com/problems/group-anagrams/
vector<vector<string>> groupAnagrams(vector<string> &strs)
{
    unordered_map<string, vector<string>> mp;
    for (string s : strs)
    {
        string t = s;
        sort(t.begin(), t.end());
        mp[t].push_back(s);
    }
    vector<vector<string>> ans;
    for (auto p : mp)
    {
        ans.push_back(p.second);
    }
    return ans;
}

int main()
{
    vector<string> strs = {"eat", "tea", "tan", "ate", "nat", "bat"};
    vector<vector<string>> ans = groupAnagrams(strs);
    for (auto v : ans)
    {
        for (auto s : v)
        {
            cout << s << " ";
        }
        cout << endl;
    }

    return 0;
}
