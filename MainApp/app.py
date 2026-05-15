from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

popular_df = pickle.load(open('..\Experimental_JupitorNotebook\popular.pkl', 'rb'))
pt = pickle.load(open('..\Experimental_JupitorNotebook\pt.pkl', 'rb'))
books = pickle.load(open('../Experimental_JupitorNotebook/books.pkl', 'rb'))
similarity_score = pickle.load(open('..\Experimental_JupitorNotebook\similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author = list(popular_df['Book-Author'].values),
                           image = list(popular_df['Image-URL-M'].values),
                           votes = list(popular_df['Number-Of-Rating'].values),
                           rating = list(popular_df['Avg-Rating'].values),
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods = ['post'])
def recommend():
    user_input = request.form.get('user_input')
    # Step 1: get index
    index = np.where(pt.index == book_name)[0][0]
    
    # Step 2: get similarity scores
    similarity_scores_list = list(enumerate(similarity_score[index]))
    
    # Step 3: convert to DataFrame
    similar_df = pd.DataFrame(similarity_scores_list, columns=['Index', 'Similarity'])
    
    # Step 4: map index → book title
    similar_df['Book-Title'] = similar_df['Index'].apply(lambda x: pt.index[x])
    
    # Step 5: remove the same book
    similar_df = similar_df[similar_df['Book-Title'] != book_name]
    
    # Step 6: apply similarity threshold
    # similar_df = similar_df[similar_df['Similarity'] > 0.2]
    
    # Step 6: taking top 50 books according to similarity score 
    similar_df = similar_df.sort_values('Similarity', ascending=False).head(50)
    
    # Step 7: merge rating data
    similar_df = similar_df.merge(avg_rating_df[['Book-Title', 'Avg-Rating']], on='Book-Title')
    similar_df = similar_df.merge(num_rating_df[['Book-Title', 'Number-Of-Rating']], on='Book-Title')
    
    # Step 8: compute weighted score
    similar_df['Final Score'] = (
        similar_df['Similarity'] *
        (similar_df['Avg-Rating'] / 5) *    # we can remove avg rating from the formula
        np.log(similar_df['Number-Of-Rating'])
    )
    
    # Step 9: sort and take top 5
    similar_df = similar_df.sort_values('Final Score', ascending=False).head(5)
    
    # Step 10: print result
    data = []
    for _, row in similar_df.iterrows():
        item = []
        temp_df = books[books['Book-Title'] == row['Book-Title']]
        temp_df = temp_df.drop_duplicates('Book-Title')

        item.extend(list(temp_df['Book-Title'].values))
        item.extend(list(temp_df['Book-Author'].values))
        item.extend(list(temp_df['Image-URL-M'].values))
        
        data.append(item)
    
    return data
    return str(user_input)

if __name__ == '__main__':
    app.run(debug=True)