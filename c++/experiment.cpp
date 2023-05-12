#include <iostream>
#include <vector>

using namespace std;

int main()
{
    int r = 3, c = 3;

    vector<vector<int>> mat(r, vector<int>(c));

    for (int i = 0; i < r; i++)
    {
        for (int j = 0; j < c; j++)
        {
            int t;
            cin >> t;
            mat[i][j] = t;
        }
    }

    for (int i = 0; i < r; i++)
    {
        for (int j = 0; j < c; j++)
        {
            cout << mat[i][j] << " ";
        }
        cout << endl;
    }

    return 0;
}
