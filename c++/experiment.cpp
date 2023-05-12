#include <iostream>
#include <vector>

using namespace std;

int main()
{
    // int r = 3, c = 3;

    // vector<vector<int>> mat(r, vector<int>(c));
    vector<vector<int>> mat = {{1, 2, 3}, {4, 0, 4}, {6, 7, 8}};

    // for (int i = 0; i < r; i++)
    // {
    //     for (int j = 0; j < c; j++)
    //     {
    //         int t;
    //         cin >> t;
    //         mat[i][j] = t;
    //     }
    // }

    for (auto i : mat)
    {
        for (auto j : i)
        {
            cout << j << " ";
        }
        cout << endl;
    }

    return 0;
}
