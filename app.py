import streamlit as st
import json
import requests

st.set_page_config(layout="wide")


def chat(model, messages):
    r = requests.post(
        f"http://0.0.0.0:11434/api/chat",
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
    col1, col2 = st.columns([1, 5])

    with col1:
        model = st.selectbox(
            "Choose a model:",
            options=["llama2", "codellama", "orca-mini", "mistral"],
            index=3,  # Default value is mistral
        )

    with col2:
        st.title("LightChat")

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.message_counter = 0  # Initialize a message counter

        conversation_box = st.empty()

        conversation_text = "\n".join(
            [
                f"{msg['role'].title()}: {msg['content']}"
                for msg in st.session_state.messages
            ]
        )
        conversation_box.text_area(
            "Conversation", value=conversation_text, height=250, disabled=True, key="convo"
        )

        # Generate a unique key for each input using a counter
        input_key = f"user_input_{st.session_state.message_counter}"

        def send_message():
            user_input = st.session_state.get(input_key, "")
            if user_input.strip():
                st.session_state.messages.append(
                    {"role": "user", "content": user_input}
                )
                message = chat(model, st.session_state.messages)
                st.session_state.messages.append(message)

                # Increment the counter to ensure the next input_key is unique
                st.session_state.message_counter += 1

                # Update the conversation display
                conversation_text = "\n".join(
                    [
                        f"{msg['role'].title()}: {msg['content']}"
                        for msg in st.session_state.messages
                    ]
                )
                conversation_box.text_area(
                    "Conversation", value=conversation_text, height=250, disabled=True
                )

                # Clear the current input by resetting it
                st.session_state[input_key] = ""

        user_input = st.text_area(
            "Enter a prompt:",
            key=input_key,
            placeholder="Type your message here...",
            height=75,
            on_change=send_message,
            args=(),
        )

        if st.button("Send"):
            send_message()


if __name__ == "__main__":
    app()