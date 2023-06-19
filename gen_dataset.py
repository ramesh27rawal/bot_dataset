import pandas as pd
import openai
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("open_ai")
openai.api_key = api_key
import requests
import json
filename = "chat_dataset.csv"
if not os.path.isfile(filename):
    df_data= pd.DataFrame()


def data_prepare():
    df = pd.read_csv("london_resturants_data.csv")
    # df=df.dropna()
    # df=df[df['City'] == 'Amsterdam']
    print(df.shape)
    string_to_replace = ['\[', '\]', '\'']
    # for replace_value in string_to_replace:
        # df['Cuisine Style'] = df['Cuisine Style'].str.replace(replace_value, '', regex=True)
        # df['combined'] = df.apply(lambda row: f"Restaurant Details , Name : {row['Name']}, cuisines: {row['CUISINES']},"
        #                                       f"price range: {row['PRICE RANGE']}, meals: {row['MEALS']}", axis=1)
    df['combined'] = df.apply(lambda row: f"{row['Name']} is restaurant located in {row['Location']}, it serves"
                                           f" cuisines like {row['CUISINES']}. " #, axis=1)
                                          f"The price range is from {row['PRICE RANGE']} pound and it provides the meals like {row['MEALS']}."#, axis=1)
    #                                       f"The diet oriented customers it provides {row['SPECIAL DIETS']}."
                                           f"The rating of this restaurant is {str(row['Rating'])} ", axis=1)
    filt_df = df  # [df['Cuisine Style']=='Chinese']
    return filt_df


def prepare_message(input_message, products_list, trigger):
    message_objects = []
    system_message = "You are a chatbot helping customers with restaurants, answering their query and give the details if needed." # + input_message[2]
    message_objects.append({"role": "system", 'content': system_message})
                            # "content": "You're a chatbot helping customers"
                            #            " with restaurants and helping them with asked number of restaurants recommendations"})
                            # "content":  "You're a chatbot helping customers"
                            #             " with restaurants and helping answering rating of the restaurant."})

    # customer_input = "Hi! Can you recommend atleast five  restaurants?"
    message_objects.append({"role": "user", "content": input_message[0]})

    # message_objects.append({"role": "user", "content": f"Here're my latest restaurant visit: {prev_purchases}"})
    #
    if trigger == '1':
        message_objects.append(
            {"role": "user", "content": f"Please  give "
                                        f" details of restaurants with  explanation."})
    else:
        message_objects.append(
            {"role": "user", "content": f"Dont give me details of restaurant."})
    message_objects.append({"role": "user",
                            "content": "Please be friendly and talk to"
                                       " me like a person, Don't just give me details of restaurant"})
    # message_objects.append({"role": "assistant", "content": f"I found these restaurants I would recommend"})

    message_objects.extend(products_list)
    if input_message[1] != "":
        print("Inside")
        message_objects.append({"role": "assistant", "content": input_message[1]})
    #                         # "content": "Here's the details of cuisines served in restaurant:"})

    return message_objects


def feed_chatgpt_model(message_objects):
    completion = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo",
        messages=message_objects
    )
    return completion.choices[0].message['content']


API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def generate_chat_completion(messages, model="gpt-4", temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def main():
    data_df = data_prepare()
    # print(data_df.dtypes.index)
    prev_purchases = data_df['combined'].values[0]
    products_list = []

    data_df = data_df.sample(n=50)
    # print(data_df.City.unique())
    for index, row in data_df.iterrows():
        brand_dict = {'role': "assistant", "content": f"{row['combined']}"}
        products_list.append(brand_dict)
    # print(products_list)
    chatbot = True
    datasets_lst = []
    while(chatbot):
        chat_dataset = {}
        print(data_df.Name.values)
        user_input = input("Your Message:")
        text = "Enter\n1   for  Please just give details of restaurants with  explanation.\n" \
               "2   for Dont give me the details for restaurant.\n"
        trigger = input(text)
        final_input = input("Bot Message: ")
        input_message = [user_input, final_input]#, system_input]
        message = prepare_message(input_message, products_list, trigger)
        responses = feed_chatgpt_model(message)
        print(responses)
        # chat_dataset["system"] = system_input
        chat_dataset["user"] = user_input
        # chat_dataset['assistant'] = final_input
        chat_dataset["response"] = responses
        try:
            df_data =  pd.read_csv("chat_dataset.csv")
        except Exception as e:
            df_data = pd.DataFrame()
        df_data = pd.concat([df_data, pd.DataFrame([chat_dataset])])
        df_data.to_csv("chat_dataset.csv",index=False)
        chatbot = False if input("Enter E for exit and press any key for continue:") in ['e','E'] else True
    # datasets_df = pd.DataFrame(datasets_lst)
    # datasets_df.to_csv("chat_dataset.csv", index=False)


main()
