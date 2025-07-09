import google.generativeai as genai

genai.configure(api_key="AIzaSyDKsokJFZUNmGiZxWBL_o89lVaz0WZ1NVY")

models = genai.list_models()

for model in models:
    print(model)  # 👈 Print the full model object to see what's available
