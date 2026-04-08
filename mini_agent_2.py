import anthropic
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()
client = anthropic.Anthropic() 
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["week2_mini_agent"]
collection = db["tool_history"]

def save_to_mongodb(step,topic,content):
    doc ={
        "step": step,
        "topic": topic,
        "content": content,
        "timestamp": datetime.now().isoformat()
        
    }
    collection.insert_one(doc)
def word_count(text):
    """Counts the number of words in the input text."""
    try:
        words = text.split()
        return f"Word count: {len(words)}"
    except:
        return "Error in counting words"
def hashtag_generator(topic):
    """Generates hashtags based on a topic."""
    try:
        tags = f"#{topic.replace(' ', '')} #Business #Marketing #SmallBusiness #Entrepreneur"
        return tags
    except:
        return "Error in generating hashtags"
    
def save_content(topic,content):
    """Saves content to a MongoDB collection."""
    try:
        save_to_mongodb("user_content",topic,content)
        return "Content saved to database"
    except:
        return "Error in saving content"

tools = [
    {
        "name":"word_count",
        "description":"Counts the number of words in a text. Use this when the user wants to know how many words are in something.",
        "input_schema":{
            "type":"object",
            "properties":{
                "text":{
                    "type":"string",
                    "description":"The text to count words in"
                }
            },
            "required":["text"]
        }
    },
    {
        "name":"hashtag_generator",
        "description":"Generates hashtags based on a topic. Use this when the user wants to create hashtags for a topic.",
        "input_schema":{
            "type":"object",
            "properties":{
                "topic":{
                    "type":"string",
                    "description":"The topic to generate hashtags for"
                }
            },
            "required":["topic"]
        }
    },
    {
        "name":"save_content",
        "description":"Saves content to a MongoDB collection. Use this when the user wants to save something to the database.",
        "input_schema":{
            "type":"object",
            "properties":{
                "topic":{
                    "type":"string",
                    "description":"The topic of the content"
                },
                "content":{
                    "type":"string",
                    "description":"The content to save"
                }
            },
            "required":["topic","content"]
        }
    }
]

def run_tool(tool_name, tool_input):
    if tool_name == "word_count":
        return word_count(tool_input["text"])
    elif tool_name == "hashtag_generator":
        return hashtag_generator(tool_input["topic"])
    elif tool_name == "save_content":
        return save_content(tool_input["topic"], tool_input["content"])
    else:
        return "Error: Tool not found"
    
def run_pipeline(business_description):
    print("\n=== Step 1: Research ===")
    
    step1_prompt = f"""
    <task>Analyze this business for social media promotion</task>
    <context>{business_description}</context>
    <rules>
    - Identify the target audience
    - List 3 key selling points
    - Suggest the best social media platforms
    - Keep your analysis under 200 words
    </rules>
    <format>Write a brief research summary</format>
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": step1_prompt}]
    )
    
    step1_result = response.content[0].text
    print(f"Research:\n{step1_result}")
    save_to_mongodb("step1_research", business_description, step1_result)

    print("\n=== Step 2: Strategy ===")
    
    step2_prompt = f"""
    <task>Create a social media promotion strategy</task>
    <context>{step1_result}</context>
    <rules>
    - Suggest 3 post ideas for each platform
    - Include best posting times
    - Define the tone and style
    - Keep strategy under 300 words
    </rules>
    <format>Write a clear promotion strategy</format>
    """
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": step2_prompt}]
    )
    
    step2_result = response.content[0].text
    print(f"Strategy:\n{step2_result}")
    save_to_mongodb("step2_strategy", business_description, step2_result)

    print("\n=== Step 3: Content Creation ===")

    step3_prompt = f"""
    <task>Generate social media post content</task>
    <context>{step2_result}</context>
    <rules>
    - Create 3 posts for each platform  
    - Use engaging language and relevant hashtags
    - Keep each post under 280 characters
    </rules>
    <format>Write the social media posts</format>
    """ 
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": step3_prompt}]
    )
    step3_result = response.content[0].text
    print(f"Content:\n{step3_result}")
    save_to_mongodb("step3_content", business_description, step3_result)

    print("\n=== Step 4: Edit + Polish ===")
    
    step4_prompt = f"""
    <task>Edit and polish these social media posts</task>
    <context>{step3_result}</context>
    <rules>
    - Use the word_count tool to check post lengths
    - Use the hashtag_generator tool to add relevant hashtags
    - Make sure posts are engaging and professional
    - Save the final version using save_content tool
    </rules>
    <format>Return the final polished posts</format>
    """

    messages = [{"role": "user", "content": step4_prompt}]
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            step4_result = response.content[0].text
            print(f"Final Posts:\n{step4_result}")
            save_to_mongodb("step4_final", business_description, step4_result)
            return step4_result
        
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    result = run_tool(tool_name, tool_input)
                    save_to_mongodb("tool_call", tool_name, result)
                    print(f"Tool used: {tool_name}")
                    print(f"Result: {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result
                    })

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result
                        }]
                    })

print("=== Mini Agent for Social Media Promotion ===")
business_description = input("Enter a brief description of your business: ")
run_pipeline(business_description)

