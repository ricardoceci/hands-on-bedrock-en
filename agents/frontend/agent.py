import boto3
import streamlit as st
import json
from requests import request
import os

region = 'us-east-1'
os.environ["AWS_REGION"] = region
llm_response = ""

# Aqui va el perfil de AWS que tienes configurado en tu maquina
aws = boto3.session.Session(profile_name='genaiday', region_name=region)
client = aws.client('bedrock-agent-runtime')

def invokeAgent(agent_id,agent_alias_id,prompt,session_id):
    response = client.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        inputText=prompt,
        sessionId=session_id
    )
    return response

with st.sidebar:
    agent_id = st.text_input("Agent ID", key="bedrock_agent_id")
    agent_alias_id = st.text_input("Agent Alias", key="bedrock_agent_alias")
    session_id = st.text_input("Sesion Id", key="session_id")

st.title("💬 Pausa Cafetera")
   
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not agent_id or not agent_alias_id:
        st.info("Please add your agent id and alias id.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)    
    response = invokeAgent(agent_id, agent_alias_id, prompt, session_id)
    completion = ""
    if(response.get("completion")):
       for event in response.get("completion"):
            chunk = event["chunk"]
            completion = completion + chunk["bytes"].decode('utf-8')
    if(completion):
        st.session_state.messages.append({"role": "assistant", "content": completion})
        st.chat_message("assistant").write(completion)
        

