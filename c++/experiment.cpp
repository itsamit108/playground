#include <bits/stdc++.h> // bits/stdc++.h should not be used in production.

using namespace std;

int main()
{
    int r = 3, c = 3;

    vector<vector<int>> mat(r, vector<int>(c));

    for (int i = 0; i < r; i++)
    {
        for (int j = 0; j < c; j++)
        {
            mat[r][c] = i * j;
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
