import pandas as pd
import openai
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("open_ai")
openai.api_key = api_key


def read_prepare_data():
    user_df = pd.read_csv("appetite_dummy_customers.csv")
    reservation_df = pd.read_csv("reservation_data.csv")
    rest_df = pd.read_csv("london_resturants_data.csv")
    friend_df = pd.read_csv("user_friend_data.csv")
    user_df['id'] = user_df.index

    reservation_df.uId = reservation_df[['uId']].replace(dict(zip(user_df.id, user_df.name)))
    reservation_df.restId = reservation_df[['restId']].replace(dict(zip(rest_df.id, rest_df.Name)))
    friend_df[['uid1', 'uId2']] = friend_df[['uid1', 'uId2']].replace(dict(zip(user_df.id, user_df.name)))
    return user_df, reservation_df, rest_df, friend_df


def sentence_data_prepare(user_df, reservation_df, rest_df):
    user_df['combined'] = user_df.apply(lambda row: f"{row['uid1']} and {row['uId2']} are friends.", axis=1)
    rest_df['combined'] = rest_df.apply(lambda row: f"{row['Name']} is restaurant located in {row['Location']} it serves", axis=1)
                                           # f" cuisines like {row['CUISINES']} " #, axis=1)
                                          # f"it provides the meals like {row['MEALS']}.", axis=1)
    #                                       f"The diet oriented customers it provides {row['SPECIAL DIETS']}."
    #                                        f"The rating of this restaurant is {str(row['Rating'])}", axis=1)
    reservation_df['combined'] = reservation_df.apply(lambda  row: f"{row['uId']} visited {row['restId']} restaurant.", axis=1)
    products_list = []

    for df in [user_df, rest_df, reservation_df]:
        for index, row in df.iterrows():
            brand_dict = {'role': "assistant", "content": f"{row['combined']}"}
            products_list.append(brand_dict)
    return products_list


def prepare_message(input_message, products_list):
    message_objects = []
    system_message = "You are a chatbot helping customers with the questions asked about the user friends and also recommend restaurants to her user. Do not answer anything other than restaurant and user." # + input_message[2]
    message_objects.append({"role": "system", 'content': system_message})
                            # "content": "You're a chatbot helping customers"
                            #            " with restaurants and helping them with asked number of restaurants recommendations"})
                            # "content":  "You're a chatbot helping customers"
                            #             " with restaurants and helping answering rating of the restaurant."})

    # customer_input = "Hi! Can you recommend atleast five  restaurants?"
    message_objects.append({"role": "user", "content": input_message[0]})

    # message_objects.append({"role": "user", "content": f"Here're my latest restaurant visit: {prev_purchases}"})
    #

    # message_objects.append(
    #     {"role": "user", "content": f"Dont give me details of restaurant."})
    message_objects.append({"role": "user",
                            "content": "Please be friendly"})
    # message_objects.append({"role": "assistant", "content": f"I found these restaurants I would recommend"})

    message_objects.extend(products_list)
    # if input_message[1] != "":
    #     print("Inside")
    message_objects.append({"role": "assistant", "content": input_message[0]})
    #                         # "content": "Here's the details of cuisines served in restaurant:"})

    return message_objects


def create_dataset():
    user_df, reservation_df, rest_df, friend_df  = read_prepare_data()
    friend_df = friend_df[(friend_df['uId2']=='Sarah')|(friend_df['uid1']=='Sarah')]
    reservation_df = reservation_df[reservation_df['uId'].isin(friend_df['uId2'].tolist()
                                                               +friend_df['uid1'].tolist())]
    best_df = rest_df[rest_df['Name'].isin(reservation_df['restId'])]
    print(best_df.Name.values)
    rest_df = rest_df.sample(n=50)

    products_list = sentence_data_prepare(friend_df, reservation_df, rest_df)
    # products_list = []
    # for index, row in sentence_df.iterrows():
    #     brand_dict = {'role': "assistant", "content": f"{row['combined']}"}
    #     products_list.append(brand_dict)
    return products_list

def feed_chatgpt_model(message_objects):
    completion = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo",
        messages=message_objects
    )
    return completion.choices[0].message['content']


def main():
    product_list = create_dataset()

    user_query = input("Your Message: ")
    # assistant_query = input("Assistant message: ")
    query = [user_query]
    message_object = prepare_message(query, product_list)
    response = feed_chatgpt_model(message_object)
    print(response)
    return
main()
