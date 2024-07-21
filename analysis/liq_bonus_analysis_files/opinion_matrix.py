import pandas as pd

df = pd.read_csv('../data/pairwise.csv')

# Create a function to build the matrix
def build_opinion_matrix(df):
    # Initialize the matrix as a DataFrame
    assets = pd.concat([df['chosen_asset'], df['comparison_asset']]).unique()
    matrix = pd.DataFrame(0, index=assets, columns=assets, dtype=float)
    
    # Count occurrences
    for i in assets:
        for j in assets:
            if i != j:
                i_chosen_j_not = len(df[(df['chosen_asset'] == i) & (df['comparison_asset'] == j)])
                j_chosen_i_not = len(df[(df['chosen_asset'] == j) & (df['comparison_asset'] == i)])
                total = i_chosen_j_not + j_chosen_i_not
                
                if total > 0:
                    matrix.at[i, j] = str(round((i_chosen_j_not / total),2)) + ', ' + str(i_chosen_j_not) + ', '+ str(total)
    
    return matrix

# Build the opinion matrix from your dataframe
opinion_matrix = build_opinion_matrix(df)
opinion_matrix.to_csv('../data/opinion_matrix_more_info.csv', index=True)
print(opinion_matrix)