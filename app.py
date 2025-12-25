from config import USER_PROMPT
from dependencies import MyDeps
from planner_agent.agent import planner_agent

if __name__ == "__main__":
    my_db_deps = MyDeps(db_name="Production_SQL_Azure", is_admin=True)
    result = planner_agent.run_sync(USER_PROMPT, deps=my_db_deps)
    print(result.output)
