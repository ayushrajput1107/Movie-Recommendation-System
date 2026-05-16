#include<bits/stdc++.h>
using namespace std;


bool found(vector<vector<int>>&board,int i,int j){
    // front 
    if(i > 0){
        for(int row = i;row>=0;row--){
            if(board[row][j] == 1)return true;
        }

    }

    // doagional_right
    if(i > 0){
        int row = i,col = j;
        while(row >= 0 && col < board.size()){
            if(board[row][col] == 1)return true;
            row--;
            col++;
        }
    }

    // diagonal_left

    if(j > 0){
        int row = i,col = j;
        while(col >= 0 && row >= 0){
            if(board[row][col] == 1)return true;
            row--;
            col--;

        }
    }

    return false;


}

void output(vector<vector<int>>&board){
    for(int i=0;i<board.size();i++){
        for(int j=0;j<board[i].size();j++){
            if(board[i][j])cout<<"Q ";
            else cout<<". ";
        }
        cout<<endl;
    }
}

void solve(int n,vector<vector<int>>&board,int start){
    if(n <= 0)output(board);
    for(int i=start;i<board.size();i++){
        for(int j=0;j<board[i].size();j++){
            if(found(board,i,j)){
                board[i][j] = 1;
                solve(n-1,board,start+1);
                board[i][j] = 0;
            }
        }
    }
    
}


int main(){
    int n = 4;
    vector<vector<int>>board(n,vector<int>(n,0));
    solve(n,board,0);

    return 0;
}