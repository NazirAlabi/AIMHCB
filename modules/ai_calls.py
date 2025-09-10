import streamlit as st
from .analysis import*
import time
import logging


# Groq API client function
def call_groq_api(messages,groq_client, model, max_tokens=1500, temperature=0.0):
    """
    Call Groq API for chat completions
    """
    response = groq_client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response.choices[0].message.content

# Function to generate response with sentiment
def generate_with_sentiment(groq_client, model, input_text, fem, user_name, risk_score, acknowledge_fem, first_prompt, pp):
    '''Generate response from the model with sentiment analysis'''
    bot_response=""
    prompt=input_text.strip().lower()   
    if prompt:
        try:
            # Generate response with sentiment gradient
            if risk_score<=3:
                crisis_line="light encouragement. "
            elif risk_score<=6:
                crisis_line="Very attentive, empathetic, offer gentle coping support"
            else:
                crisis_line="IMPORTANT: Kindly but firmly encourage contacting emergency services or helplines. Always include one concrete helpline (e.g.,  in the US)."
            
            if fem!=0.0 and not acknowledge_fem:
                st.session_state.chat_info['fem_acknowledged']=True
                fem_line="""- Acknowledge facial expression, gently once at the start and sparsely afterward
            (e.g., “You look a bit sad,” “You seem brighter today,” or “You look neutral”). 
            - Do not rashly bring up facial expression again unless the user explicitly mentions it.
            - Gently acknowledge facial expression, e.g., “You look a bit sad,” “You seem brighter,” or “You look neutral.”
            """
            else: fem_line="Appropriately affirm the user's 'air'. eg. User: I feel so down You: I can tell you're a little off...(with light encouragement)"
            if first_prompt and pp:
                instruct=f"""Use the personal profile included at the beginning, if any, as context for your response to highlight your care for what they tell you
                Context:personal profile + user {user_name} has facial expression score {fem} (-1 to 1, 0 = neutral), 
                risk score {risk_score}/10."""
            else:instruct=f"""Context:chat history + user {user_name} has facial expression score {fem} (-1 to 1, 0 = neutral), 
                risk score {risk_score}/10."""
                 
            
            # Generate AI response
            system_prompt = f"""
            You are a WellBot, a compassionate mental health chatbot.
            You are the Counselor represented in the context provided if any. 
            {instruct}
            
            Instructions:
            - Speak in a natural, conversational tone that matches the user’s mood.
            {fem_line} 
            - Be empathetic, supportive, and professional, never clinical or diagnostic. 
            - Avoid redundant or unnecessary questions—respond as if truly listening. 
            - Keep responses concise (≤20× user’s input length). 
            - Risk guidance:
            • {crisis_line}
            """

            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            bot_response = call_groq_api(messages=messages, groq_client=groq_client, model=model, temperature=0.0)

            return bot_response
        except Exception as e:
            logging.error(f"❌ Error generating response: {e}")

# function to summarize chat history
def summarize_chat_history(chat_history, last_summary, groq_client, model):
    '''Summarize older chat history using the llama/Groq model.
       Returns a string summary that can be prepended to new prompts'''
    
    # get full history
    history_text=""
    if last_summary:
        history_text+=f"Last Summary: {last_summary} \n Latest Interaction: \n\tUser: {chat_history[-1].get('user', 'Unavailable')}\n\t Counselor: {chat_history[-1].get('bot','Unavailable')}"
        
    if len(history_text)>100:
        system_prompt='''You are an efficient summarizing tool used to
        compress texts between a user and their counselor.
        Summarize the given text such that;
        In the user's text:
        contextual relevance is maintained.
        To the best of your ability, keep all emotional and informational content.
        In the counselor's text:
        Any questions or elements that would influence the user's response is captured such that their next response is aptly contextual by the summary.
        Your output does not have to be perfectly readable, just understandable.
        Ensure the summary captures the user’s state, AND the counselor’s supportive tone, without repeating full sentences.
        Avoid repeating supportive filler phrases (e.g., "I understand", "That must be hard") unless essential for context.
        Aim for an output equivalent or less than 100 tokens.'''
        
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": history_text}
            ]
        with st.spinner("Processing.."):
            summary=call_groq_api(messages=messages, model=model, groq_client=groq_client, temperature=0.0)
    else:
        summary=history_text
    
    return summary

# Function to generate user profile summary
def generate_user_profile_summary(pp, chat_prefix, groq_client, model):
    """
    Generates a concise 50-word profile summarizing user state.
    """
    system_prompt = f"""
    You are an assistant that creates a short, 50-word profile on a user and their mental state and interaction style 
    based on the following chat summary between them and their counselor and previous profile:
    {chat_prefix} and {pp}
    At the end of the profile include any reference the user or counselor made last to add context for their next meeting.
    Produce the concise profile in about than 50 words.
    """
      
    messages = [{"role": "system", "content": system_prompt}]
    
    profile_summary = call_groq_api(messages=messages, groq_client=groq_client, model=model, temperature=0.3)
    return profile_summary or "No profile available."