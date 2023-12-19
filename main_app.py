import streamlit as st 
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import json
from Footer import footer

st.set_page_config(
    page_title="AdventureGPT",
    page_icon="🌠",

)

st.title("Welcome to AdventureGPT")
load_dotenv(find_dotenv())
client = OpenAI()
def generate_user_line(prompt):
    return [
        {
            "role": "user",
            "content": prompt,
        },
    ]

def generate_host_line(response):
    return [
        {
            "role": "host",
            "content": response,
        },
    ]

def generate_response(prompt, script):
  response = client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      response_format={ "type": "json_object" },
      messages=[
          {
              "role": "system",
              "content": "You are the host of a 10 part multiple choice adventure series"
              ,
          },
      ]
      + generate_user_line(prompt),
      max_tokens=500,
  )
  response_text = response.choices[0].message.content
  return response, response_text

def initial_prompt(char1, char2, keyword1, genre):
  text_ret = """ You are going the first part of a 10 part turn by turn multiple choice adventure story time that is {0}. 
  The two main characters are {1} and {2}.
  Involve {3} in the story somehow.
  Ensure that the story concludes within 10 parts
  Generate the introduction to the first part of the story.
  Generate a prompt for an image that portrays the scene accurately.
  Generate 4 following choices for the users to select to continue the story.
  Please give the response in a proper JSON format that is easily parsed for data.

  Here is the example JSON output:
  {{
  "Part": "1",
  “Storyline”: "Generated Story Line",
  “ImagePrompt”: "Generated Image Prompt",
  “MultipleChoice”: [
      "Choice A": "Generated Choice A",
      "Choice B": "Generated Choice B",
      "Choice C": "Generated Choice C",
      "Choice D": "Generated Choice D"
    ]
  }}""".format(genre, char1, char2, keyword1)
  return text_ret

def generate_next_prompt(selected_choice, partno):
  text_ret = """
  The user has selected the following choice: {0}. 
  Generate the next part of the story based on the user's selection. Generate a prompt for in image that portrays the scene accurately. 
  Generate 4 following choices for the users to select to continue the story.
  Please give the response in a proper JSON format that is easily parsed for data.

  Here is the example JSON output:
  {{
  "Part": {1},
  “Storyline”: "Generated Story Line",
  “ImagePrompt”: "Generated Image Prompt",
  “MultipleChoice”: [
      "Choice A": "Generated Choice A",
      "Choice B": "Generated Choice B",
      "Choice C": "Generated Choice C",
      "Choice D": "Generated Choice D"
    ]
  }}""".format(selected_choice, partno)
  return text_ret

def generate_ui (resp):
  data = json.loads(resp)
  return
  st.text_area("", data["Storyline"])
  selection = st.radio(
    "Make your next move:",
    [data["MultipleChoice"]["Choice A"], data["MultipleChoice"]["Choice B"], data["MultipleChoice"]["Choice C"], data["MultipleChoice"]["Choice D"]]
  )

def generate_img (img_prompt):
  response = client.images.generate(
    model="dall-e-3",
    prompt=img_prompt,
    size="1024x1024",
    quality="standard",
    n=1,
  )
  return response.data[0].url


def update_prompt():
  print("ZZinit promptupdated to "+st.session_state.number_inpt_choice)
  st.session_state.initial_prompt = st.session_state.number_inpt_choice

def clear_states():
  for key in st.session_state.keys():
    del st.session_state[key]

def click_button():
  #clear_states()
  print("button_clicked")
  # st.session_state.char1 = char1
  # st.session_state.char2 = char2
  # st.session_state.keyword1 = keyword1
  # st.session_state.genre = genre
  print("char1: "+st.session_state.char1)
  st.session_state.clicked = True

st.button('Restart', on_click=clear_states)


if 'clicked' not in st.session_state:
  with st.form("form_original"):
    st.markdown(
        """
        ### Enter some characters, a keyword, and a genre to begin your adventure!
    """
    )

    st.text_input("Enter a first character", key="char1")
    st.text_input("Enter a second character", key="char2")
    st.text_input("Enter a keyword", key='keyword1')
    st.text_input("Enter a genre", key="genre")

    #st.toggle('Show Logs', key="logs")

    submitted = st.form_submit_button('Begin', on_click=click_button)


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if 'part' not in st.session_state:
    st.session_state.part = 1

if 'script' not in st.session_state:
    st.session_state.script = []

if 'number_inpt_choice' not in st.session_state:
    st.session_state.number_inpt_choice = ""
print("session state clicked = "+str(st.session_state.clicked))
if st.session_state.clicked:
  resp_text = ""
  
  if 'initial_prompt' not in st.session_state:
    print("Generating initial prompt"+st.session_state.char1)
    #print("Showing Logs? "+str(st.session_state.logs))
    # char1 = st.session_state.char1
    # char2 = st.session_state.char2
    # keyword1 = st.session_state.keyword1
    # genre = st.session_state.genre

    initial_p = initial_prompt(st.session_state.char1, st.session_state.char2, st.session_state.keyword1, st.session_state.genre)
    st.session_state.script = generate_user_line(initial_p)
    resp, resp_text = generate_response(initial_p, [])
    st.session_state.script = st.session_state.script+generate_host_line(resp_text)
    
  else:
    print("Generating next prompt with: "+st.session_state.initial_prompt)
    next_p = generate_next_prompt(st.session_state.initial_prompt, st.session_state.part)
    st.session_state.script = st.session_state.script+generate_user_line(next_p)
    resp, resp_text = generate_response(next_p, st.session_state.script)
    st.session_state.script = st.session_state.script+generate_host_line(resp_text)
  #print(script+)
  #st.json(resp_text)
  #print(resp_text.Part)
  
  data = json.loads(resp_text)
  stry = data["Storyline"]
  imgurl = generate_img(data["ImagePrompt"])
  #st.text_area("", data["Storyline"])
  st.markdown(f"Part: {st.session_state.part}")

  #st.json(data)
  
  print(f"PART {st.session_state.part-1} DONE")
  st.session_state.part = st.session_state.part+1
  with st.form("form1"):
    st.image(imgurl)
    st.write(f"{stry}")
    radio_selection = st.radio(
      "Make your next move:",
      [data["MultipleChoice"]["Choice A"], data["MultipleChoice"]["Choice B"], data["MultipleChoice"]["Choice C"], data["MultipleChoice"]["Choice D"]],
      index=None,
      key="number_inpt_choice"
    )
    submitted = st.form_submit_button("Next", on_click=update_prompt)
    if submitted:
        print("init promptupdated to "+st.session_state.number_inpt_choice)
        st.session_state.initial_prompt = st.session_state.number_inpt_choice


 
  st.divider()
  st.json(st.session_state.script)


footer()
