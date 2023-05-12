#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

int main()
{
    int r = 3, c = 3;

    vector<vector<int>> mat;

    for (int i = 0; i < r; i++)
    {
        for (int j = 0; j < c; j++)
        {
            int t;
            cin >> t;
            mat[r][c] = t;
        }
    }

    for (int i = 0; i < r; i++)
    {
        for (int j = 0; j < c; j++)
        {
            cout << mat[r][c] << " ";
        }
        cout << endl;
    }

    return 0;
}
