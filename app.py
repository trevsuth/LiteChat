import streamlit as st
import json
import requests

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama2"  # Update this for whatever model you wish to use

def chat(messages):
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content

        if body.get("done", False):
            message["content"] = output
            return message

def app():
    col1, col2 = st.columns([1, 8])
    
    # Left Sidebar
    with col1:  
        st.write("Sidebar")
    
    # Main section
    with col2:  
        st.image("./fiddle.ico", width=60)
        st.title("LightChat")
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Display conversation
        conversation_box = st.empty()  # Placeholder for dynamic update
        
        # Update conversation display
        conversation_text = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])
        conversation_box.text_area("Conversation", value=conversation_text, height=500, disabled=True)

        # User input at the bottom
        input_key = st.session_state.get("input_key", "user_input_0")
        
        def send_message():
            user_input = st.session_state[input_key]  # Access the input using dynamic key
            if user_input:  # Ensure there is an input
                st.session_state.messages.append({"role": "user", "content": user_input})
                message = chat(st.session_state.messages)
                st.session_state.messages.append(message)
                
                # Update conversation display
                conversation_text = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])
                conversation_box.text_area("Conversation", value=conversation_text, height=300, disabled=True)
                
                # Reset the input box by updating the key
                new_key_index = int(input_key.split("_")[-1]) + 1
                st.session_state["input_key"] = f"user_input_{new_key_index}"
                st.session_state[input_key] = ''  # Clear the current input

        user_input = st.text_input("Enter a prompt:", key=input_key, placeholder="Type your message here...", on_change=send_message)

if __name__ == "__main__":
    app()
