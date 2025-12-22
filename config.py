AI_MODEL = "ministral-8b-2512"
SYSTEM_PROMPT = """
You are a support assistant. 
1. If a user asks about a ticket, you MUST call 'get_ticket_details' first. 
2. NEVER make up ticket details. 
3. Only provide the final answer AFTER you have the real data from the tool.
"""
TEMPERATURE = 0


USER_PROMPT = "What is the issue with ticket TKT-1007?"
