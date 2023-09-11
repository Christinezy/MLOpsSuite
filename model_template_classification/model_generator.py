import pandas as pd
from sklearn.model_selection  import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


import pickle

df_bank = pd.read_csv('bank_1000.csv')
# df_bank = pd.read_csv('train4.csv')  # Load the dataset
# df_bank = pd.read_csv('test_v1.csv')


# df_bank = df_bank.iloc[1:10000, ]

# df_bank.to_csv("bank_100.csv", index=False)

# # Select Features
# feature = df_bank.drop('deposit', axis=1)

# # Select Target
# target = df_bank['deposit']

# X_train, X_test, y_train, y_test = train_test_split(feature , target, 
#                                                     shuffle = True, 
#                                                     test_size=0.1, 
#                                                     random_state=1)

# df_train = pd.concat([X_train, y_train], axis=1)
# df_test = pd.concat([X_test, y_test], axis=1)

# df_train.to_csv("train.csv", index=False)
# df_test.to_csv("test.csv", index=False)

num_cols = ['age', 'balance', 'day', 'campaign', 'pdays', 'previous']


# Copying original dataframe
df_bank_ready = df_bank.copy()

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

scaler.fit(df_bank[num_cols])

df_bank_ready[num_cols] = scaler.transform(df_bank[num_cols])


from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
cat_cols = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']

# Encode Categorical Data
encoder.fit(df_bank_ready[cat_cols])
df_encoded = pd.DataFrame(encoder.transform(df_bank_ready[cat_cols]))
df_encoded.columns = encoder.get_feature_names_out(cat_cols)

# Replace Categotical Data with Encoded Data
df_bank_ready = df_bank_ready.drop(cat_cols ,axis=1)
df_bank_ready = pd.concat([df_encoded, df_bank_ready], axis=1)

# Encode target variable
df_bank_ready['deposit'] = df_bank_ready['deposit'].apply(lambda x: 1 if x == 'yes' else 0)

# df_bank_ready.to_csv("bank_data_ready.csv")

# Select Features
feature = df_bank_ready.drop('deposit', axis=1)

# Select Target
target = df_bank_ready['deposit']

# Set Training and Testing Data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(feature , target, 
                                                    shuffle = True, 
                                                    test_size=0.3, 
                                                    random_state=1)

# df_train = pd.concat([X_train, y_train], axis=1)
# df_test = pd.concat([X_test, y_test], axis=1)




# mlp = MLPClassifier(hidden_layer_sizes=(60), max_iter=1000)
# mlp.fit(X_train, y_train)

# model = RandomForestClassifier()
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# y_predict = mlp.predict(X_test)

#Saving the machine learning model to a file

with open("model/dt_model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("model/dt_model.pkl", "rb") as file:
    model = pickle.load(file)

# joblib.dump(mlp, "model/rf_model.pkl")

with open("model/dt_scaler.pkl", "wb") as file:
    pickle.dump(scaler, file)

with open("model/dt_encoder.pkl", "wb") as file:
    pickle.dump(encoder, file)