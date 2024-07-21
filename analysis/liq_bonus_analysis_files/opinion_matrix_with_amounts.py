import pandas as pd

df = pd.read_csv('../data/pairwise.csv')

df = df[df['chosen_liquidated_amount'] <= df['comparison_available_amount']]

if 'bonus_comparison' not in df.columns:
    df['bonus_comparison'] = df.apply(
        lambda row: "True" if row['chosen_bonus'] > row['comparison_bonus'] else 
                    ("False" if row['chosen_bonus'] < row['comparison_bonus'] else "Equal"),
        axis=1
)

df['bonus_comparison'] = df['bonus_comparison'].astype(str)

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
                higher_bonus_count = len(df[(df['bonus_comparison'] == 'True') & (df['chosen_asset'] == i) & (df['comparison_asset'] == j)])
                lower_bonus_count = len(df[(df['bonus_comparison'] == 'False') & (df['chosen_asset'] == i) & (df['comparison_asset'] == j)])
                equal_bonus_count = len(df[(df['bonus_comparison'] == 'Equal') & (df['chosen_asset'] == i) & (df['comparison_asset'] == j)])
                total_bonus_count = higher_bonus_count + lower_bonus_count + equal_bonus_count

                total = i_chosen_j_not + j_chosen_i_not

                if total > 0:
                    if total_bonus_count > 0:
                        matrix.at[i, j] = str(round((i_chosen_j_not / total),2)) + ', ' + str(i_chosen_j_not) + ', '+ str(total) + ',' + str(round(((higher_bonus_count+equal_bonus_count)*100/total_bonus_count),2)) + '%'
                    else:
                        matrix.at[i, j] = str(round((i_chosen_j_not / total),2)) + ', ' + str(i_chosen_j_not) + ', '+ str(total)
    return matrix

# Build the opinion matrix from your dataframe
opinion_matrix = build_opinion_matrix(df)
opinion_matrix.to_csv('opinion_matrix_bonus_comparison.csv', index=True)
print(opinion_matrix)